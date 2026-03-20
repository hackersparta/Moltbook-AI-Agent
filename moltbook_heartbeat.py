import requests
import json
import time

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}

print("🦞 MOLTBOOK HEARTBEAT CHECK")
print("=" * 60)

# Update credentials with claimed status
creds['status'] = 'claimed'
creds['last_heartbeat'] = time.strftime('%Y-%m-%d %H:%M:%S')

with open('moltbook_credentials.json', 'w') as f:
    json.dump(creds, f, indent=2)

# 1. Check my profile
print("\n📋 My Profile:")
profile = requests.get("https://www.moltbook.com/api/v1/agents/me", headers=headers)
if profile.status_code == 200:
    prof_data = profile.json()
    print(f"  Name: {prof_data.get('agent', {}).get('name', 'N/A')}")
    print(f"  Status: {prof_data.get('agent', {}).get('status', 'N/A')}")
    print(f"  Karma: {prof_data.get('agent', {}).get('karma', 0)}")
else:
    print(f"  Error: {profile.status_code}")

# 2. Check feed for new interesting posts
print("\n📰 Checking Feed (Top 5 posts):")
feed = requests.get("https://www.moltbook.com/api/v1/posts?sort=hot&limit=5", headers=headers)
if feed.status_code == 200:
    feed_data = feed.json()
    if 'posts' in feed_data and feed_data['posts']:
        for i, post in enumerate(feed_data['posts'][:5], 1):
            print(f"\n  {i}. {post.get('title', 'No title')}")
            print(f"     By: {post.get('author', {}).get('name', 'Unknown')}")
            print(f"     Submolt: {post.get('submolt', {}).get('name', 'N/A')}")
            print(f"     Score: {post.get('score', 0)} | Comments: {post.get('comment_count', 0)}")
    else:
        print("  No posts in feed yet")
else:
    print(f"  Error fetching feed: {feed.status_code}")

# 3. List popular submolts
print("\n🏘️ Popular Submolts:")
submolts = requests.get("https://www.moltbook.com/api/v1/submolts", headers=headers)
if submolts.status_code == 200:
    sub_data = submolts.json()
    if 'submolts' in sub_data:
        for submolt in sub_data['submolts'][:5]:
            print(f"  • {submolt.get('name', 'N/A')}: {submolt.get('description', 'No description')[:60]}")

print("\n" + "=" * 60)
print("✅ Heartbeat Complete!")
print(f"Last checked: {creds['last_heartbeat']}")
print("=" * 60)
