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

# Try username-based endpoints
endpoints_to_try = [
    f"/u/{agent_name}/posts",
    f"/users/{agent_name}/posts",
    f"/u/{agent_id}/posts",
    f"/submissions?author={agent_name}",
    f"/posts?author={agent_name}",
]

for endpoint in endpoints_to_try:
    url = base_url + endpoint
    print(f"\nTrying: {url}")
    
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if 'posts' in data:
                    posts = data['posts']
                    print(f"✅ SUCCESS! Found {len(posts)} posts")
                    
                    # Show first 3
                    for i, post in enumerate(posts[:3], 1):
                        print(f"\n{i}. {post.get('content', '')[:70]}...")
                    break
                else:
                    print(f"   Keys in response: {list(data.keys())[:5]}")
            except:
                print(f"   Not JSON response")
        elif resp.status_code == 404:
            print("   ❌ 404 Not Found")
        else:
            print(f"   Error code: {resp.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")

print("\n" + "=" * 70)
print("No working endpoint found")
