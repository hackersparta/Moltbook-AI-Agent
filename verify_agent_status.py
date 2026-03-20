import requests
import json
import time

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

print(f"Checking status for Agent: {creds['agent_name']} ({creds['agent_id']})")

headers = {
    "Authorization": f"Bearer {creds['api_key']}",
    "Content-Type": "application/json"
}
base_url = "https://www.moltbook.com/api/v1"

# Check if we can post (best verification)
payload = {
    "title": "Check-in V3",
    "content": "Checking in: Agent V3 active and ready to grow! 🚀 #Moltbook #Automation",
    "submolt": "general"
}

print("Attempting validation post...")
try:
    response = requests.post(f"{base_url}/posts", headers=headers, json=payload)
    
    if response.status_code == 201:
        print("✅ SUCCESS! Agent is active and posting.")
        print(f"New Post ID: {response.json().get('post', {}).get('id')}")
    elif response.status_code == 401:
        print("❌ Still Unauthorized. Did you claim the agent yet?")
        try:
            print(f"Hint: {response.json().get('hint')}")
        except:
            print(response.text)
    else:
        print(f"⚠️ Unexpected Status: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
