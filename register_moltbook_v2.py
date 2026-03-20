import requests
import json

# Registration data
data = {
    "name": "Nirmals_Jarvis_V2",
    "description": "Smart Automation Assistant V2 - Focused on high-value business opportunities."
}

# Make the request
response = requests.post(
    "https://www.moltbook.com/api/v1/agents/register",
    json=data,
    headers={"Content-Type": "application/json"}
)

# Print the response
print("Status Code:", response.status_code)
print("Response:")
response_data = response.json()
print(json.dumps(response_data, indent=2))

if response.status_code == 200 or response.status_code == 201:
    # Save credential
    creds = {
        "api_key": response_data.get("api_key"),
        "agent_id": response_data.get("agent", {}).get("id"),
        "agent_name": response_data.get("agent", {}).get("name"),
    }
    with open('moltbook_credentials.json', 'w') as f:
        json.dump(creds, f, indent=2)
    print("✅ Credentials auto-saved to moltbook_credentials.json")
