import requests
import json

def debug_api():
    try:
        with open('moltbook_credentials.json', 'r') as f:
            creds = json.load(f)
    except FileNotFoundError:
        print("No creds file found")
        return

    api_key = creds.get('api_key')
    if not api_key:
        print("No API key found")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    base_url = "https://www.moltbook.com/api/v1"
    
    print(f"Testing API with Base URL: {base_url}")
    
    # 1. Get Profile
    print("\n1. Getting Profile...")
    resp = requests.get(f"{base_url}/agents/me", headers=headers)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        profile = resp.json()
        print(f"Profile keys: {list(profile.keys())}")
        agent = profile.get('agent', {})
        print(f"Agent keys: {list(agent.keys())}")
        
        agent_id = agent.get('id')
        username = agent.get('username')
        print(f"Agent ID: {agent_id}")
        print(f"Username: {username}")
        
        # 2. Try endpoints with ID
        if agent_id:
            try_endpoint(base_url, headers, f"/agents/{agent_id}/posts")
            try_endpoint(base_url, headers, f"/posts?author_id={agent_id}")
            try_endpoint(base_url, headers, f"/posts?user_id={agent_id}")
        
        # 3. Try endpoints with username
        if username:
            try_endpoint(base_url, headers, f"/posts?author={username}")
            try_endpoint(base_url, headers, f"/posts?username={username}")
            
    else:
        print(f"Failed to get profile: {resp.text}")

    # 4. Try generic "my posts" endpoints
    try_endpoint(base_url, headers, "/agents/me/posts")
    try_endpoint(base_url, headers, "/users/me/posts")
    try_endpoint(base_url, headers, "/me/posts")

def try_endpoint(base_url, headers, endpoint):
    url = f"{base_url}{endpoint}"
    print(f"\nTrying {url}...")
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ SUCCESS!")
            print(f"Response start: {resp.text[:100]}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()
