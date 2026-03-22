"""
Instagram Auto-Poster for Render deployment.
Downloads carousel slides from Google Drive, posts to IG via Meta Graph API.

Flow:
  1. Download carousel_report.xlsx from Drive
  2. Find today's scheduled post (match Scheduled Date column)
  3. Download all slides for that post from Drive
  4. Upload slides to Meta as carousel containers
  5. Publish carousel to Instagram
  6. Update Excel status → re-upload to Drive

Environment variables required on Render:
  META_PAGE_ACCESS_TOKEN  - long-lived page access token
  META_IG_ACCOUNT_ID      - Instagram business account ID
  DRIVE_FOLDER_ID         - Google Drive folder ID with posts
  GOOGLE_CREDENTIALS_JSON - service account JSON (base64 encoded) OR
  DRIVE_REFRESH_TOKEN     - OAuth refresh token
  DRIVE_CLIENT_ID         - OAuth client ID
  DRIVE_CLIENT_SECRET     - OAuth client secret
"""

import os
import io
import json
import base64
import tempfile
import logging
from datetime import datetime, date

import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from openpyxl import load_workbook

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Config from env ──────────────────────────────────────────────
META_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN", "")
IG_ACCOUNT_ID = os.environ.get("META_IG_ACCOUNT_ID", "17841445079545451")
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "1u5TWQ4T4IP8HdnO3hhPuyPaqftt46CF5")
META_API = "https://graph.facebook.com/v21.0"

# ── Google Drive auth ────────────────────────────────────────────
def get_drive_service():
    """Build Drive service from OAuth refresh token stored in env."""
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get("DRIVE_REFRESH_TOKEN"),
        client_id=os.environ.get("DRIVE_CLIENT_ID"),
        client_secret=os.environ.get("DRIVE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def list_drive_folder(drive, folder_id):
    """List files in a Drive folder."""
    results = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)",
        pageSize=100,
    ).execute()
    return results.get("files", [])


def download_drive_file(drive, file_id):
    """Download file content as bytes."""
    return drive.files().get_media(fileId=file_id).execute()


def upload_drive_file(drive, folder_id, name, content_bytes, mime_type):
    """Upload/replace a file in Drive folder."""
    # Check if file already exists
    existing = drive.files().list(
        q=f"'{folder_id}' in parents and name='{name}' and trashed=false",
        fields="files(id)",
    ).execute().get("files", [])

    media = MediaIoBaseUpload(io.BytesIO(content_bytes), mimetype=mime_type)

    if existing:
        # Update existing file
        return drive.files().update(
            fileId=existing[0]["id"],
            media_body=media,
        ).execute()
    else:
        # Create new file
        return drive.files().create(
            body={"name": name, "parents": [folder_id]},
            media_body=media,
            fields="id",
        ).execute()


# ── Excel helpers ────────────────────────────────────────────────
# ★ Wishlist sheet columns (1-indexed):
#  1=#, 2=Post ID (shortcode), 3=Date, 4=Likes, 5=Slides,
#  6=Post URL, 7=Caption,
#  8=Scheduled Date, 9=Cover Image, 10=Rendered Path,
#  11=Status, 12=Posted Date

COL_NUM = 1
COL_SHORTCODE = 2
COL_DATE = 3
COL_LIKES = 4
COL_SLIDES = 5
COL_URL = 6
COL_CAPTION = 7
COL_SCHEDULED = 8
COL_STATUS = 11
COL_POSTED = 12


def find_todays_post(wb):
    """Find the row in ★ Wishlist where Scheduled Date = today and Status = 'rendered'."""
    ws = wb["★ Wishlist"]
    today_str = date.today().strftime("%Y-%m-%d")

    for row in range(2, ws.max_row + 1):
        sched = ws.cell(row=row, column=COL_SCHEDULED).value
        status = ws.cell(row=row, column=COL_STATUS).value

        if sched is None:
            continue

        # Handle both date objects and strings
        if hasattr(sched, "strftime"):
            sched_str = sched.strftime("%Y-%m-%d")
        else:
            sched_str = str(sched).strip()

        if sched_str == today_str and str(status).strip().lower() == "rendered":
            shortcode = ws.cell(row=row, column=COL_SHORTCODE).value
            log.info(f"Found today's post: row={row}, shortcode={shortcode}")
            return row, shortcode

    log.info(f"No post scheduled for {today_str}")
    return None, None


def mark_posted(wb, row):
    """Update Status to 'posted' and set Posted Date."""
    ws = wb["★ Wishlist"]
    ws.cell(row=row, column=COL_STATUS).value = "posted"
    ws.cell(row=row, column=COL_POSTED).value = date.today().strftime("%Y-%m-%d")


# ── Meta Graph API ───────────────────────────────────────────────
def upload_image_to_meta(image_url, caption=None, is_carousel_item=True):
    """Upload a single image as a carousel item container."""
    payload = {
        "image_url": image_url,
        "access_token": META_TOKEN,
    }
    if is_carousel_item:
        payload["is_carousel_item"] = "true"
    if caption:
        payload["caption"] = caption

    resp = requests.post(f"{META_API}/{IG_ACCOUNT_ID}/media", data=payload)
    resp.raise_for_status()
    return resp.json()["id"]


def create_carousel(container_ids, caption):
    """Create carousel container from item IDs."""
    payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(container_ids),
        "caption": caption,
        "access_token": META_TOKEN,
    }
    resp = requests.post(f"{META_API}/{IG_ACCOUNT_ID}/media", data=payload)
    resp.raise_for_status()
    return resp.json()["id"]


def publish_container(container_id):
    """Publish a media container with retry."""
    import time
    # Wait for Meta to process all images
    time.sleep(20)
    for attempt in range(3):
        resp = requests.post(
            f"{META_API}/{IG_ACCOUNT_ID}/media_publish",
            data={"creation_id": container_id, "access_token": META_TOKEN},
        )
        if resp.status_code == 200:
            return resp.json()["id"]
        log.warning(f"Publish attempt {attempt+1} failed: {resp.status_code} {resp.text}")
        if attempt < 2:
            time.sleep(15)  # Wait more before retry
    resp.raise_for_status()
    return resp.json()["id"]


def get_public_url(drive, file_id):
    """Make file publicly readable and return direct image URL."""
    try:
        drive.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
    except Exception:
        pass  # May already be shared
    return f"https://lh3.googleusercontent.com/d/{file_id}"


# ── Main pipeline ────────────────────────────────────────────────
def run_daily_post():
    """Main function: check today's schedule, download slides, post to IG."""
    log.info("=== IG Auto-Poster starting ===")

    if not META_TOKEN:
        log.error("META_PAGE_ACCESS_TOKEN not set")
        return {"status": "error", "message": "META_PAGE_ACCESS_TOKEN not set"}

    drive = get_drive_service()

    # 1. Find and download carousel_report.xlsx
    log.info("Downloading carousel_report.xlsx from Drive...")
    root_files = list_drive_folder(drive, DRIVE_FOLDER_ID)
    excel_file = next((f for f in root_files if f["name"] == "carousel_report.xlsx"), None)
    if not excel_file:
        log.error("carousel_report.xlsx not found in Drive")
        return {"status": "error", "message": "carousel_report.xlsx not found"}

    excel_bytes = download_drive_file(drive, excel_file["id"])
    wb = load_workbook(io.BytesIO(excel_bytes))

    # 2. Find today's scheduled post
    row, shortcode = find_todays_post(wb)
    if row is None:
        return {"status": "skipped", "message": "No post scheduled for today"}

    # 3. Find post folder on Drive
    post_folder = next((f for f in root_files if f["name"] == shortcode), None)
    if not post_folder:
        log.error(f"Folder '{shortcode}' not found on Drive")
        return {"status": "error", "message": f"Folder '{shortcode}' not found"}

    # 4. List slides and caption
    post_files = list_drive_folder(drive, post_folder["id"])
    slides = sorted([f for f in post_files if f["name"].startswith("slide_") and f["name"].endswith(".png")],
                     key=lambda x: x["name"])
    caption_file = next((f for f in post_files if f["name"] == "caption.txt"), None)

    if not slides:
        log.error(f"No slides found in {shortcode}")
        return {"status": "error", "message": f"No slides in {shortcode}"}

    caption = ""
    if caption_file:
        caption = download_drive_file(drive, caption_file["id"]).decode("utf-8")

    log.info(f"Posting {shortcode}: {len(slides)} slides, caption={len(caption)} chars")

    # 5. Make slides public and upload to Meta
    container_ids = []
    for slide in slides:
        url = get_public_url(drive, slide["id"])
        log.info(f"  Uploading {slide['name']} -> {url}")
        cid = upload_image_to_meta(url)
        container_ids.append(cid)
        log.info(f"  Container: {cid}")

    # 6. Create carousel and publish
    carousel_id = create_carousel(container_ids, caption)
    log.info(f"Carousel container: {carousel_id}")

    media_id = publish_container(carousel_id)
    log.info(f"Published! Media ID: {media_id}")

    # 7. Update Excel and re-upload
    mark_posted(wb, row)
    buf = io.BytesIO()
    wb.save(buf)
    upload_drive_file(
        drive, DRIVE_FOLDER_ID, "carousel_report.xlsx",
        buf.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    log.info("Excel updated on Drive")

    return {
        "status": "posted",
        "shortcode": shortcode,
        "slides": len(slides),
        "media_id": media_id,
    }


if __name__ == "__main__":
    result = run_daily_post()
    print(json.dumps(result, indent=2))
