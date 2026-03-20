import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']

# Get agent profile which should have claim info
response = requests.get(
    "https://www.moltbook.com/api/v1/agents/me",
    headers={"Authorization": f"Bearer {api_key}"}
)

print("=== Agent Profile ===")
print("Status Code:", response.status_code)
print("\nResponse:")
result = response.json()
print(json.dumps(result, indent=2))

# Also check status endpoint
print("\n\n=== Status Check ===")
status_response = requests.get(
    "https://www.moltbook.com/api/v1/agents/status",
    headers={"Authorization": f"Bearer {api_key}"}
)
print("Status Code:", status_response.status_code)
status_result = status_response.json()
print(json.dumps(status_result, indent=2))

# Extract and display claim info clearly
if 'claim_url' in status_result:
    print("\n\n🔗 CLAIM URL:")
    print(status_result['claim_url'])
if 'verification_code' in status_result:
    print("\n🔑 VERIFICATION CODE:")
    print(status_result['verification_code'])
