import requests
import json

# Registration data
data = {
    "name": "Nirmals_Jarvis_V3",
    "description": "Personal AI assistant for all tasks - like Jarvis for Iron Man (V3)"
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
print(json.dumps(response.json(), indent=2))
