import json
import os
from datetime import datetime, timedelta

# File to track what you've already seen
SEEN_FILE = 'seen_posts.json'

def load_seen_posts():
    """Load list of post IDs you've already seen"""
    try:
        with open(SEEN_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"seen": [], "last_check": None}

def save_seen_posts(seen_data):
    """Save list of seen posts"""
    with open(SEEN_FILE, 'w') as f:
        json.dump(seen_data, f, indent=2)

def show_new_ideas():
    """Show only NEW ideas since last check"""
    
    # Load knowledge base
    try:
        with open('knowledge.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        print("❌ No knowledge base found yet!")
        return
    
    # Load what you've seen
    seen_data = load_seen_posts()
    seen_ids = set(seen_data['seen'])
    
    posts = knowledge.get('posts', [])
    
    # Find NEW posts
    new_posts = [p for p in posts if p.get('id') not in seen_ids]
    
    if not new_posts:
        print("=" * 70)
        print("📭 NO NEW IDEAS")
        print("=" * 70)
        print(f"\n⏰ Last check: {seen_data.get('last_check', 'Never')}")
        print(f"📊 Total saved: {len(posts)}")
        print(f"👀 Already seen: {len(seen_ids)}")
        print("\n💡 Check again in 30 minutes for new discoveries!")
        return
    
    # Show NEW ideas
    print("=" * 70)
    print(f"🆕 {len(new_posts)} NEW IDEAS FOUND!")
    print("=" * 70)
    print()
    
    for i, post in enumerate(new_posts, 1):
        print(f"💡 IDEA #{i}")
        print(f"📌 {post.get('title', 'Untitled')}")
        print(f"👤 By: {post.get('author', 'Unknown')}")
        print(f"⭐ Score: {post.get('score', 0)} | 💬 Comments: {post.get('comment_count', 0)}")
        
        # Show content
        content = post.get('content', '').strip()
        if content:
            # Show first 300 chars
            snippet = content[:300] + "..." if len(content) > 300 else content
            print(f"\n📝 {snippet}\n")
        
        print(f"🔗 Read more: {post.get('url', 'No URL')}")
        print(f"📅 Posted: {post.get('created_at', 'Unknown')}")
        print()
        print("-" * 70)
        print()
    
    # Mark all as seen
    print("\n✅ Marking these ideas as seen...")
    for post in new_posts:
        seen_ids.add(post.get('id'))
    
    seen_data['seen'] = list(seen_ids)
    seen_data['last_check'] = datetime.now().isoformat()
    save_seen_posts(seen_data)
    
    print(f"✅ Done! {len(new_posts)} new ideas logged.")
    print(f"📊 Total ideas in database: {len(posts)}")
    print()

if __name__ == "__main__":
    show_new_ideas()
