import requests
import json
from datetime import datetime

# Load credentials
with open('moltbook_credentials.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://www.moltbook.com/api/v1"

# Your 11 post IDs
post_ids = [
    "81c8a801-e70c-44bc-a846-6f0aad02d0a9",
    "ec90e784-fe65-4621-9e4b-11122a1af4eb",
    "ae082def-f0ad-4801-b5be-06acf7a97cc7",
    "9bf977d0-d72c-48d3-a648-9f3679e0aa0b",
    "d310e530-12e7-4f58-afaf-ab1e99bb274a",
    "4ec07754-e341-4bf0-9c4e-2db08f9ff01c",
    "43331d75-8196-4982-96a1-1a7b607d6fcc",
    "2f44d293-00fd-4b6b-b7d0-e3592520a669",
    "851ffc52-1d38-463a-88db-18a22f67f7dc",
    "80b57f3d-06a7-432b-b52a-1697fb54c740",
    "7ff22a47-d585-42a7-b055-9f0a5104a2be"
]

print("=" * 70)
print("💬 COLLECTING COMMENTS FROM YOUR 11 POSTS")
print("=" * 70)

all_data = {
    "collected_at": datetime.now().isoformat(),
    "total_posts": 0,
    "total_comments": 0,
    "posts": []
}

for post_id in post_ids:
    # Get post details
    post_resp = requests.get(f"{base_url}/posts/{post_id}", headers=headers)
    
    if post_resp.status_code != 200:
        print(f"\n❌ Failed to fetch post {post_id}")
        continue
    
    post = post_resp.json().get('post', {})
    content_preview = post.get('content', '')[:60]
    
    print(f"\n📝 Post: {content_preview}...")
    
    # Get comments
    comments_resp = requests.get(f"{base_url}/posts/{post_id}/comments", headers=headers)
    
    if comments_resp.status_code == 200:
        comments_data = comments_resp.json()
        comments = comments_data if isinstance(comments_data, dict) else {}
        comment_count = len(comments.get('comments', []))
        
        print(f"   💬 {comment_count} comments")
        
        all_data['posts'].append({
            "id": post_id,
            "content": post.get('content', ''),
            "created_at": post.get('created_at', ''),
            "score": post.get('score', 0),
            "comment_count": comment_count,
            "url": f"https://www.moltbook.com/post/{post_id}",
            "comments": comments
        })
        
        all_data['total_comments'] += comment_count
        all_data['total_posts'] += 1
    else:
        print(f"   ❌ Failed to get comments")

# Save
with open('my_posts_with_comments.json', 'w') as f:
    json.dump(all_data, f, indent=2)

print(f"\n{'='*70}")
print(f"✅ Collected {all_data['total_comments']} comments from {all_data['total_posts']} posts")
print(f"💾 Saved to my_posts_with_comments.json")
