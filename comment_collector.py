import requests
import json
from datetime import datetime

class CommentCollector:
    def __init__(self, credentials_file='moltbook_credentials.json'):
        with open(credentials_file, 'r') as f:
            self.creds = json.load(f)
        self.api_key = self.creds['api_key']
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://www.moltbook.com/api/v1"
    
    def get_my_posts(self):
        """Fetch all posts created by this account"""
        # Load posting history to get post IDs
        post_ids = []
        
        try:
            with open('posting_history.json', 'r') as f:
                history = json.load(f)
            # Extract non-null post IDs
            post_ids = [p['id'] for p in history.get('posts', []) if p.get('id')]
            print(f"✅ Loaded {len(post_ids)} post IDs from posting_history.json")
        except:
            print("⚠️ Could not load posting_history.json")
        
        # Fallback to hardcoded IDs if history is empty
        if not post_ids:
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
            print(f"✅ Using {len(post_ids)} hardcoded post IDs as fallback")
        
        # Fetch posts by ID
        my_posts = []
        for post_id in post_ids:
            try:
                response = requests.get(f"{self.base_url}/posts/{post_id}", headers=self.headers)
                if response.status_code == 200:
                    post_data = response.json().get('post', {})
                    if post_data:
                        my_posts.append(post_data)
            except Exception as e:
                print(f"⚠️ Could not fetch post {post_id}: {e}")
        
        print(f"🔍 Successfully fetched {len(my_posts)} posts")
        return my_posts
    
    def get_post_comments(self, post_id):
        """Fetch all comments on a specific post"""
        url = f"{self.base_url}/posts/{post_id}/comments"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch comments for post {post_id}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching comments: {e}")
            return []
    
    def collect_all_comments(self):
        """Collect all comments from all user's posts"""
        
        print("=" * 70)
        print("💬 COMMENT COLLECTOR")
        print("=" * 70)
        
        # Get all posts
        my_posts = self.get_my_posts()
        
        if not my_posts:
            print("\n📭 No posts found!")
            return
        
        print(f"\n📝 Found {len(my_posts)} posts\n")
        
        all_data = {
            "collected_at": datetime.now().isoformat(),
            "total_posts": len(my_posts),
            "total_comments": 0,
            "posts": []
        }
        
        for post in my_posts:
            post_id = post.get('id')
            title = post.get('content', '')[:50] + '...'
            
            print(f"[Post {post_id}] {title}")
            
            # Get comments for this post
            comments = self.get_post_comments(post_id)
            
            print(f"  💬 {len(comments)} comments")
            
            all_data['posts'].append({
                "id": post_id,
                "content": post.get('content', ''),
                "created_at": post.get('created_at', ''),
                "score": post.get('score', 0),
                "comment_count": len(comments),
                "url": f"https://www.moltbook.com/post/{post_id}",
                "comments": comments
            })
            
            all_data['total_comments'] += len(comments)
        
        # Save to file
        with open('my_posts_with_comments.json', 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"\n✅ Collected {all_data['total_comments']} total comments from {len(my_posts)} posts")
        print(f"💾 Saved to my_posts_with_comments.json")
        
        return all_data

if __name__ == "__main__":
    collector = CommentCollector()
    collector.collect_all_comments()
