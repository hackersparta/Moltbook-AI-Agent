import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}

# Try to verify the post
print("🔍 Checking verification requirements...")

# First, let's see what verification endpoint expects
verify_response = requests.post(
    "https://www.moltbook.com/api/v1/verify",
    headers=headers,
    json={}
)

print(f"Verification Status: {verify_response.status_code}")
print("\nResponse:")
print(json.dumps(verify_response.json(), indent=2))
