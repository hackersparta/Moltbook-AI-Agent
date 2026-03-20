import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']

# Check agent status
response = requests.get(
    "https://www.moltbook.com/api/v1/agents/status",
    headers={"Authorization": f"Bearer {api_key}"}
)

print("Status Code:", response.status_code)
print("\nFull Response:")
print(json.dumps(response.json(), indent=2))
