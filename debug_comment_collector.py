import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://www.moltbook.com/api/v1"

# Step 1: Get Profile
print("=" * 70)
print("🔍 DEBUGGING COMMENT COLLECTOR")
print("=" * 70)

profile_resp = requests.get(f"{base_url}/agents/me", headers=headers)
if profile_resp.status_code == 200:
    agent_data = profile_resp.json().get('agent', {})
    agent_id = agent_data.get('id')
    agent_name = agent_data.get('name')
    
    print(f"\n✅ Your Agent Profile:")
    print(f"   ID: {agent_id}")
    print(f"   Name: {agent_name}")
else:
    print(f"❌ Failed to get profile: {profile_resp.status_code}")
    exit(1)

# Step 2: Fetch posts by author_id
print(f"\n🔍 Fetching posts with author_id={agent_id}...")
url = f"{base_url}/posts?author_id={agent_id}"
print(f"   URL: {url}")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    posts = data.get('posts', [])
    
    print(f"\n✅ Found {len(posts)} posts")
    print("\n📝 Post Preview:")
    for i, post in enumerate(posts[:5], 1):
        print(f"\n{i}. {post.get('content', '')[:80]}...")
        print(f"   Author: {post.get('author', {}).get('name', 'Unknown')}")
        print(f"   Author ID: {post.get('author', {}).get('id', 'Unknown')}")
        print(f"   Created: {post.get('created_at', '')}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
