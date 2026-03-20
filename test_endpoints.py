import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://www.moltbook.com/api/v1"

# Get Profile
profile_resp = requests.get(f"{base_url}/agents/me", headers=headers)
agent_data = profile_resp.json().get('agent', {})
agent_id = agent_data.get('id')
agent_name = agent_data.get('name')

print(f"Your Agent: {agent_name} (ID: {agent_id})\n")
print("=" * 70)

# Try different endpoints
endpoints_to_try = [
    f"/agents/{agent_id}/posts",
    f"/agents/me/posts",
    f"/users/{agent_id}/posts",
]

for endpoint in endpoints_to_try:
    url = base_url + endpoint
    print(f"\nTrying: {url}")
    
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if 'posts' in data:
                posts = data['posts']
                print(f"✅ SUCCESS! Found {len(posts)} posts")
                
                # Show first 3
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n{i}. {post.get('content', '')[:70]}...")
                    print(f"   Author: {post.get('author', {}).get('name')}")
                break
            else:
                print(f"   Response keys: {list(data.keys())}")
        else:
            print(f"   Error: {resp.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")
