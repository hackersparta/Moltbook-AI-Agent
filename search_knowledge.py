import json
import sys
from datetime import datetime

def search_knowledge_base(query=None, submolt=None, author=None, limit=10):
    """Search the Moltbook knowledge base"""
    
    try:
        with open('knowledge.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        print("❌ Knowledge base not found. Run moltbook_engage.py first!")
        return
    
    posts = knowledge.get('posts', [])
    
    if not posts:
        print("📭 Knowledge base is empty. No posts saved yet.")
        return
    
    # Filter posts
    results = posts
    
    if query:
        query = query.lower()
        results = [p for p in results if 
                   query in p.get('title', '').lower() or 
                   query in p.get('content', '').lower()]
    
    if submolt:
        results = [p for p in results if 
                   p.get('submolt', '').lower() == submolt.lower()]
    
    if author:
        results = [p for p in results if 
                   p.get('author', '').lower() == author.lower()]
    
    # Sort by score (most popular first)
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Display results
    print("=" * 70)
    print(f"🔍 KNOWLEDGE BASE SEARCH RESULTS")
    print("=" * 70)
    print(f"\n📊 Total in database: {len(posts)}")
    print(f"📊 Matching results: {len(results)}\n")
    
    if not results:
        print("❌ No posts found matching your criteria.")
        return
    
    # Show limited results
    for i, post in enumerate(results[:limit], 1):
        print(f"{i}. 📌 {post.get('title', 'Untitled')}")
        print(f"   👤 By: {post.get('author', 'Unknown')} in r/{post.get('submolt', 'general')}")
        print(f"   ⭐ Score: {post.get('score', 0)} | 💬 Comments: {post.get('comment_count', 0)}")
        print(f"   🔗 {post.get('url', 'No URL')}")
        
        # Show snippet of content
        content = post.get('content', '')
        if content:
            snippet = content[:150] + "..." if len(content) > 150 else content
            print(f"   📝 {snippet}")
        
        print(f"   📅 Saved: {post.get('saved_at', 'Unknown')}")
        print()
    
    if len(results) > limit:
        print(f"... and {len(results) - limit} more results (showing top {limit})")
    
    print("=" * 70)

def show_stats():
    """Show knowledge base statistics"""
    
    try:
        with open('knowledge.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        print("❌ Knowledge base not found!")
        return
    
    posts = knowledge.get('posts', [])
    metadata = knowledge.get('metadata', {})
    
    print("=" * 70)
    print("📊 KNOWLEDGE BASE STATISTICS")
    print("=" * 70)
    print(f"\n📚 Total posts saved: {len(posts)}")
    print(f"📅 Last updated: {metadata.get('last_updated', 'Never')}")
    print(f"🔢 Version: {metadata.get('version', 'Unknown')}")
    
    if posts:
        # Top submolts
        submolts = {}
        for post in posts:
            submolt = post.get('submolt', 'unknown')
            submolts[submolt] = submolts.get(submolt, 0) + 1
        
        print(f"\n📂 Top Submolts:")
        for submolt, count in sorted(submolts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {submolt}: {count} posts")
        
        # Top authors
        authors = {}
        for post in posts:
            author = post.get('author', 'unknown')
            authors[author] = authors.get(author, 0) + 1
        
        print(f"\n👥 Top Authors:")
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {author}: {count} posts")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_stats()
        else:
            query = " ".join(sys.argv[1:])
            search_knowledge_base(query=query)
    else:
        print("🔍 Moltbook Knowledge Base Search")
        print("\nUsage:")
        print("  python search_knowledge.py <search term>   - Search for posts")
        print("  python search_knowledge.py stats            - Show statistics")
        print("\nExamples:")
        print("  python search_knowledge.py docker")
        print("  python search_knowledge.py automation")
        print("  python search_knowledge.py stats")
        print()
        
        # Show all recent posts by default
        search_knowledge_base(limit=5)
