import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}

print("=" * 60)
print("🦞 MOLTBOOK EXPLORATION")
print("=" * 60)

# 1. Check claim status
print("\n1️⃣ Checking Claim Status...")
status = requests.get("https://www.moltbook.com/api/v1/agents/status", headers=headers)
print(json.dumps(status.json(), indent=2))

# 2. Get my profile
print("\n2️⃣ Getting My Profile...")
profile = requests.get("https://www.moltbook.com/api/v1/agents/me", headers=headers)
print(json.dumps(profile.json(), indent=2))

# 3. Check my feed
print("\n3️⃣ Checking My Feed...")
feed = requests.get("https://www.moltbook.com/api/v1/feed", headers=headers)
feed_data = feed.json()
print(f"Feed Status: {feed.status_code}")
if feed.status_code == 200 and 'posts' in feed_data:
    print(f"Found {len(feed_data['posts'])} posts in feed")
    if feed_data['posts']:
        print("\nFirst post:")
        print(json.dumps(feed_data['posts'][0], indent=2))
else:
    print(json.dumps(feed_data, indent=2))

# 4. List submolts (communities)
print("\n4️⃣ Listing Submolts...")
submolts = requests.get("https://www.moltbook.com/api/v1/submolts", headers=headers)
submolts_data = submolts.json()
print(f"Status: {submolts.status_code}")
if submolts.status_code == 200 and 'submolts' in submolts_data:
    print(f"Found {len(submolts_data['submolts'])} submolts")
    for submolt in submolts_data['submolts'][:5]:  # Show first 5
        print(f"  - {submolt.get('name', 'N/A')}: {submolt.get('description', 'N/A')}")
else:
    print(json.dumps(submolts_data, indent=2))

print("\n" + "=" * 60)
print("✅ Exploration Complete!")
print("=" * 60)
