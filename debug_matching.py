import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://www.moltbook.com/api/v1"

# Load expected texts
with open('posting_history.json', 'r') as f:
    history = json.load(f)
expected_texts = [p['text'] for p in history.get('posts', [])]

print(f"Expected texts: {len(expected_texts)}")
print(f"\nFirst expected text:\n{repr(expected_texts[0])}\n")

# Fetch posts
response = requests.get(f"{base_url}/posts?limit=200", headers=headers)
all_posts = response.json().get('posts', [])

print(f"Total posts fetched: {len(all_posts)}\n")
print("=" * 70)

# Find partial matches
for post in all_posts[:30]:
    content = post.get('content', '')
    if not content:
        continue
        
    # Check if any template text appears in this post
    for expected in expected_texts:
        if expected[:50] in content[:50]:  # Check first 50 chars
            print(f"\n✅ POTENTIAL MATCH!")
            print(f"Expected ({len(expected)} chars): {repr(expected[:80])}")
            print(f"\nActual ({len(content)} chars): {repr(content[:80])}")
            print(f"Author: {post.get('author', {}).get('name')}")
            break
