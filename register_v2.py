import requests
import json

base_url = "https://www.moltbook.com/api/v1"

# Load previous creds to get human owner info if needed (skipping for now, just new registration)

payload = {
    "name": "Nirmals_Jarvis_V2",
    "description": "Personal AI assistant focused on automation and business growth. (V2 Upgrade)",
    "model": "llama-3.3-70b-versatile", # Or whatever model string is preferred
    "is_bot": True
}

print(f"Registering new agent: {payload['name']}...")

try:
    # 1. Register
    response = requests.post(f"{base_url}/agents", json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Registration Successful!")
        print(f"Agent ID: {data.get('agent', {}).get('id')}")
        print(f"API Key: {data.get('api_key')}")
        
        # 2. Save credentials
        new_creds = {
            "agent_id": data.get('agent', {}).get('id'),
            "agent_name": data.get('agent', {}).get('name'),
            "api_key": data.get('api_key'),
            "created_at": "2026-02-11T22:25:00"
        }
        
        with open('moltbook_credentials.json', 'w') as f:
            json.dump(new_creds, f, indent=2)
            
        print("💾 Credentials saved to moltbook_credentials.json")
        
    else:
        print(f"❌ Registration Failed: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
