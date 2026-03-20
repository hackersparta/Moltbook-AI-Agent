import requests
import json

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://www.moltbook.com/api/v1"

# Get Profile
profile_resp = requests.get(f"{base_url}/agents/me", headers=headers)
agent_id = profile_resp.json().get('agent', {}).get('id')
agent_name = profile_resp.json().get('agent', {}).get('name')

print(f"Your Agent: {agent_name} (ID: {agent_id})\n")

# Fetch posts
response = requests.get(f"{base_url}/posts?limit=100", headers=headers)
all_posts = response.json().get('posts', [])

print(f"Total posts fetched: {len(all_posts)}\n")
print("=" * 70)

# Check first 15 posts for YOUR posts
my_count = 0
for i, post in enumerate(all_posts[:15], 1):
    content_preview = post.get('content', '')[:60]
    author_obj = post.get('author')
    
    print(f"\n{i}. {content_preview}...")
    print(f"   Author object: {author_obj}")
    
    if author_obj:
        post_author_id = author_obj.get('id')
        post_author_name = author_obj.get('name')
        print(f"   Author: {post_author_name} (ID: {post_author_id})")
        
        if post_author_id == agent_id:
            print(f"   ✅ THIS IS YOUR POST!")
            my_count += 1
        else:
            print(f"   ❌ Not yours (expected ID: {agent_id})")
    else:
        print(f"   ⚠️ No author object!")

print(f"\n\n{'='*70}")
print(f"Found {my_count} of YOUR posts in first 15 results")
