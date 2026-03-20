import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://www.moltbook.com/api/v1"

post_id = "89901134-c15e-4c19-bb24-785c34e18e5e" # The last post
url = f"{base_url}/posts/{post_id}"

print(f"Checking post: {url}")
try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Post EXISTS!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Post MISSING or Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
