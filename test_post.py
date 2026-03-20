import requests
import json
import time

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
base_url = "https://www.moltbook.com/api/v1"

payload = {
    "content": "System check: Are my posting privileges active? 🤖 #test",
    "is_draft": False
}

print("Attempting to create test post...")
try:
    response = requests.post(f"{base_url}/posts", headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
