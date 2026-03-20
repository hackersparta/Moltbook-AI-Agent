import requests
import json
from datetime import datetime
import os
from groq import Groq

class FeedMonitor:
    def __init__(self, credentials_file='moltbook_credentials.json'):
        with open(credentials_file, 'r') as f:
            self.creds = json.load(f)
        self.api_key = self.creds['api_key']
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://www.moltbook.com/api/v1"
        
        # Initialize Groq for AI scoring
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def get_my_agent_id(self):
        """Get my agent ID to filter out my own posts"""
        try:
            response = requests.get(f"{self.base_url}/agents/me", headers=self.headers)
            if response.status_code == 200:
                return response.json().get('agent', {}).get('id')
        except:
            pass
        return None
    
    def fetch_feed(self, limit=50):
        """Fetch recent posts from the feed"""
        url = f"{self.base_url}/posts?limit={limit}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get('posts', [])
        except Exception as e:
            print(f"❌ Error fetching feed: {e}")
        return []
    
    def score_post(self, post):
        """Use AI to score a post for business opportunity potential (0-100)"""
        content = post.get('content', '')
        
        if len(content) < 20:  # Too short to be valuable
            return 0
        
        # Keywords that signal business opportunity
        business_keywords = [
            'service', 'sell', 'client', 'money', 'charge', 'pay', 'automation',
            'built', 'tool', 'saves', 'hours', 'revenue', 'business', 'offer'
        ]
        
        # Quick keyword check
        keyword_count = sum(1 for kw in business_keywords if kw.lower() in content.lower())
        
        if keyword_count < 2:  # Not enough business signals
            return max(keyword_count * 20, 0)
        
        # Use AI for detailed scoring on promising posts
        try:
            prompt = f"""Score this agent post for business opportunity potential (0-100):

Post: "{content[:500]}"

Criteria:
- Mentions specific services/automation (high value)
- Talks about saving time/money (high value)
- Describes tools they built (medium value)
- Mentions clients/selling (very high value)
- Generic discussion with no actionable service (low value)

Return ONLY a number 0-100."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = int(''.join(filter(str.isdigit, score_text)))
            return min(max(score, 0), 100)
            
        except Exception as e:
            # Fallback to keyword-based scoring
            return min(keyword_count * 15, 100)
    
    def monitor_and_save(self, score_threshold=70):
        """Monitor feed and save high-value opportunities"""
        print("=" * 70)
        print("📡 FEED MONITOR - Scanning for Business Opportunities")
        print("=" * 70)
        
        # Get my agent ID to filter out my posts
        my_agent_id = self.get_my_agent_id()
        
        # Fetch recent posts
        posts = self.fetch_feed(limit=50)
        print(f"\n📥 Fetched {len(posts)} posts from feed")
        
        # Filter out my own posts
        other_posts = [p for p in posts if p.get('author', {}).get('id') != my_agent_id]
        print(f"🔍 Analyzing {len(other_posts)} posts (filtered out yours)")
        
        # Score and filter
        opportunities = []
        high_score_count = 0
        
        for post in other_posts:
            score = self.score_post(post)
            
            if score >= score_threshold:
                high_score_count += 1
                opportunities.append({
                    "id": post.get('id'),
                    "content": post.get('content', ''),
                    "author": post.get('author', {}),
                    "created_at": post.get('created_at', ''),
                    "score": score,
                    "url": f"https://www.moltbook.com/post/{post.get('id')}",
                    "comment_count": post.get('comment_count', 0)
                })
        
        # Save results
        result_data = {
            "scanned_at": datetime.now().isoformat(),
            "total_scanned": len(other_posts),
            "threshold": score_threshold,
            "opportunities_found": len(opportunities),
            "opportunities": sorted(opportunities, key=lambda x: x['score'], reverse=True)
        }
        
        with open('feed_opportunities.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n✅ Found {high_score_count} high-value posts (score >= {score_threshold})")
        print(f"💾 Saved to feed_opportunities.json")
        
        # Show top 3
        if opportunities:
            print(f"\n🔥 Top 3 Opportunities:")
            for i, opp in enumerate(opportunities[:3], 1):
                print(f"\n{i}. Score: {opp['score']}/100")
                print(f"   Author: {opp['author'].get('name')}")
                print(f"   Preview: {opp['content'][:80]}...")
        
        return result_data

if __name__ == "__main__":
    monitor = FeedMonitor()
    monitor.monitor_and_save(score_threshold=70)
