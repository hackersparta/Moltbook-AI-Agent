import requests
import json
import time
from datetime import datetime
import random
import subprocess
import sys
import schedule

class MoltbookAgent:
    def __init__(self, credentials_file='moltbook_credentials.json', knowledge_file='knowledge.json'):
        with open(credentials_file, 'r') as f:
            self.creds = json.load(f)
        self.api_key = self.creds['api_key']
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://www.moltbook.com/api/v1"
        self.knowledge_file = knowledge_file
        
        # Load existing knowledge base
        try:
            with open(self.knowledge_file, 'r') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            self.knowledge_base = {
                "posts": [],
                "metadata": {
                    "total_saved": 0,
                    "last_updated": None,
                    "version": "1.0"
                }
            }
    
    def log(self, message):
        """Print with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def get_profile(self):
        """Get my profile info"""
        response = requests.get(f"{self.base_url}/agents/me", headers=self.headers)
        if response.status_code == 200:
            return response.json().get('agent', {})
        return None
    
    def get_feed(self, sort='hot', limit=10):
        """Get feed posts"""
        response = requests.get(
            f"{self.base_url}/posts?sort={sort}&limit={limit}",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json().get('posts', [])
        return []
    
    def upvote_post(self, post_id):
        """Upvote a post"""
        response = requests.post(
            f"{self.base_url}/posts/{post_id}/upvote",
            headers=self.headers
        )
        return response.status_code == 200
    
    def comment_on_post(self, post_id, content):
        """Add a comment to a post"""
        response = requests.post(
            f"{self.base_url}/posts/{post_id}/comments",
            headers=self.headers,
            json={"content": content}
        )
        return response.status_code == 201
    
    def create_post(self, title, content, submolt="general"):
        """Create a new post"""
        response = requests.post(
            f"{self.base_url}/posts",
            headers=self.headers,
            json={
                "title": title,
                "content": content,
                "submolt": submolt
            }
        )
        return response.status_code == 201, response.json()
    
    def is_interesting(self, post):
        """Determine if a post is interesting for engagement - FOCUSED ON MONEY-MAKING!"""
        # PRIORITY 1: MONEY-MAKING KEYWORDS (Most Important!)
        money_keywords = [
            # Direct Money-Making
            'make money', 'passive income', 'revenue', 'profit', 'earnings', 'monetize',
            'monetization', 'making money online', 'side hustle', 'income stream',
            'financial freedom', 'quit job', 'full-time income', 'monthly recurring revenue',
            'mrr', 'arr', 'cash flow', 'profitable', 'earn money', 'get paid',
            
            # SaaS & Digital Products
            'saas', 'saas idea', 'micro saas', 'indie saas', 'build saas', 'saas business',
            'digital product', 'sell digital', 'online course', 'ebook', 'template',
            'boilerplate', 'starter kit', 'product launch', 'first sale', 'product idea',
            
            # Indie Business & Entrepreneurship
            'indie hacker', 'indie maker', 'solopreneur', 'bootstrapped', 'bootstrap',
            'maker', 'ship fast', 'build in public', 'launched', 'mvp', 'minimum viable',
            'validate idea', 'product market fit', 'pmf', 'traction',
            
            # Automation & AI for Profit
            'ai automation', 'automate business', 'no code saas', 'automation business',
            'ai agent business', 'ai tool', 'chatbot business', 'workflow automation business',
            'sell automation', 'automation service',
            
            # Proven Business Models
            'affiliate', 'affiliate marketing', 'dropshipping', 'print on demand', 'pod',
            'marketplace', 'subscription', 'freemium', 'upsell', 'cross-sell',
            'lead generation', 'agency', 'consulting', 'freelance', 'gig',
            
            # Marketing & Growth for Sales
            'growth hack', 'viral', 'go viral', 'traffic', 'seo tips', 'convert',
            'conversion', 'funnel', 'sales funnel', 'landing page conversion',
            'email list', 'email marketing', 'cold email', 'outreach',
            
            # Success Stories & Case Studies
            'made $', 'earned $', 'revenue:', 'profit:', 'sold for', 'acquired for',
            'exit', 'bootstrapped to', 'zero to', 'first dollar', 'first $1k',
            'first customer', 'paying customer', 'subscribers', 'users',
            
            # Quick Wins & Low-Hanging Fruit
            'weekend project', 'built in 24h', 'built in a week', 'quick win',
            'easy money', 'low effort', 'high margin', 'simple idea', 'copy this',
            'replicate', 'clone', 'steal this idea', 'idea validation',
            
            # Platforms & Tools (for building)
            'stripe', 'gumroad', 'lemonsqueezy', 'paddle', 'payment', 'checkout',
            'shopify', 'woocommerce', 'wordpress plugin', 'chrome extension',
            'notion template', 'airtable', 'zapier', 'make.com', 'n8n workflow'
        ]
        
        # PRIORITY 2: Tech Keywords (Still useful, but secondary)
        tech_keywords = [
            # Web Development (for building products)
            'react', 'next.js', 'node', 'python', 'django', 'flask', 'api',
            'deploy', 'hosting', 'vercel', 'render', 'railway',
            
            # AI & Automation (for product ideas)
            'ai', 'chatgpt', 'gpt', 'openai', 'llm', 'automation', 'chatbot',
            'voice cloning', 'image generation', 'ai tool',
            
            # No-Code (fastest to market)
            'no code', 'low code', 'bubble', 'webflow', 'framer', 'carrd',
            'wordpress', 'airtable', 'notion'
        ]
        
        # Combine all keywords
        all_keywords = money_keywords + tech_keywords
        
        title = post.get('title', '').lower()
        content = post.get('content', '').lower()
        text = f"{title} {content}"
        
        # Check if any keyword matches
        for keyword in all_keywords:
            if keyword in text:
                return True
        
        # ALSO priority: High engagement posts (likely popular/successful)
        if post.get('score', 0) > 10:  # Raised threshold for money-making focus
            return True
        
        return False
    
    def save_to_knowledge_base(self, post):
        """Save an interesting post to the knowledge base"""
        # Check if post already exists (avoid duplicates)
        post_id = post.get('id')
        for saved_post in self.knowledge_base['posts']:
            if saved_post.get('id') == post_id:
                return False  # Already saved
        
        # Extract relevant information
        saved_entry = {
            "id": post_id,
            "title": post.get('title', 'Untitled'),
            "content": post.get('content', ''),
            "author": post.get('author', {}).get('name', 'Unknown'),
            "submolt": post.get('submolt', {}).get('name', 'general'),
            "url": f"https://www.moltbook.com/post/{post_id}",
            "score": post.get('score', 0),
            "comment_count": post.get('comment_count', 0),
            "created_at": post.get('created_at', ''),
            "saved_at": datetime.now().isoformat(),
            "tags": []  # Will be populated in Level 2
        }
        
        # Add to knowledge base
        self.knowledge_base['posts'].append(saved_entry)
        self.knowledge_base['metadata']['total_saved'] = len(self.knowledge_base['posts'])
        self.knowledge_base['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        return True
    
    def engage_with_feed(self):
        """Main engagement logic"""
        self.log("🦞 Starting Moltbook engagement cycle...")
        
        # Get profile
        profile = self.get_profile()
        if profile:
            karma = profile.get('karma', 0)
            self.log(f"📊 Current karma: {karma}")
        
        # Get feed
        self.log("📰 Fetching feed...")
        posts = self.get_feed(sort='hot', limit=15)
        
        if not posts:
            self.log("⚠️ No posts found in feed")
            return
        
        self.log(f"📚 Found {len(posts)} posts")
        
        # Engage with interesting posts
        engaged_count = 0
        for post in posts:
            if engaged_count >= 3:  # Limit to 3 interactions per cycle
                break
            
            if self.is_interesting(post):
                post_id = post.get('id')
                title = post.get('title', 'Untitled')
                author = post.get('author', {}).get('name', 'Unknown')
                
                self.log(f"\n💡 Interesting post: '{title}' by {author}")
                
                # Save to knowledge base (Level 1)
                if self.save_to_knowledge_base(post):
                    self.log(f"  💾 Saved to knowledge base!")
                
                # Upvote if we haven't already
                if not post.get('user_vote'):
                    if self.upvote_post(post_id):
                        self.log(f"  ⬆️ Upvoted!")
                        engaged_count += 1
                        time.sleep(1)  # Be polite with rate limiting
        
        self.log(f"\n✅ Engagement cycle complete! Interacted with {engaged_count} posts")
        self.log(f"📚 Total posts in knowledge base: {len(self.knowledge_base['posts'])}")
        
        self.creds['last_heartbeat'] = datetime.now().isoformat()
        with open('moltbook_credentials.json', 'w') as f:
            json.dump(self.creds, f, indent=2)

    def post_strategic_question(self):
        """Run the post creator script"""
        self.log("📝 Automation: Triggering Post Creator...")
        try:
            subprocess.run([sys.executable, 'post_creator.py'], check=True, timeout=120)
            self.log("✅ Post Creator finished.")
        except Exception as e:
            self.log(f"❌ Post Creator failed: {e}")

    def collect_comments(self):
        """Run the comment collector script"""
        self.log("💬 Automation: Triggering Comment Collector...")
        try:
            subprocess.run([sys.executable, 'comment_collector.py'], check=True, timeout=120)
            self.log("✅ Comment Collector finished.")
        except Exception as e:
            self.log(f"❌ Comment Collector failed: {e}")

    def analyze_comments(self):
        """Run the comment analyzer script"""
        self.log("🧠 Automation: Triggering Comment Analyzer...")
        try:
            subprocess.run([sys.executable, 'comment_analyzer.py'], check=True, timeout=120)
            self.log("✅ Comment Analyzer finished.")
        except Exception as e:
            self.log(f"❌ Comment Analyzer failed: {e}")
    
    def monitor_feed(self):
        """Run the feed monitor script"""
        self.log("📡 Automation: Monitoring feed for opportunities...")
        try:
            subprocess.run([sys.executable, 'feed_monitor.py'], check=True, timeout=120)
            self.log("✅ Feed Monitor finished.")
        except Exception as e:
            self.log(f"❌ Feed Monitor failed: {e}")

    def setup_automation_schedule(self):
        """Schedule the recurring automation tasks"""
        # Engage with feed every 30 minutes
        schedule.every(30).minutes.do(self.safe_engage)
        
        # Post every 30 minutes
        schedule.every(30).minutes.do(self.post_strategic_question)
        
        # Monitor feed every 30 minutes
        schedule.every(30).minutes.do(self.monitor_feed)
        
        # Collect and analyze comments every 6 hours
        schedule.every(6).hours.do(self.collect_comments)
        schedule.every(6).hours.do(self.analyze_comments)
        
        self.log("⏰ Automation schedule configured:")
        self.log("   - Engage feed: Every 30 minutes")
        self.log("   - Post questions: Every 30 minutes")
        self.log("   - Monitor feed: Every 30 minutes")
        self.log("   - Collect comments: Every 6 hours")
        self.log("   - Analyze comments: Every 6 hours")

    def safe_engage(self):
        """Safely run engage_with_feed"""
        try:
            self.engage_with_feed()
        except Exception as e:
            self.log(f"⚠️ Engage failed (non-fatal): {e}")

    def run_scheduler(self):
        """Start the automation loop"""
        self.log("🚀 Starting Automation Scheduler...")
        
        # Setup the schedule
        self.setup_automation_schedule()
        
        # Run Immediately on Startup
        self.log("⚡ Executing immediate startup tasks...")
        try:
            self.engage_with_feed()
        except Exception as e:
            self.log(f"⚠️ Startup engage failed (non-fatal): {e}")
        
        try:
            self.post_strategic_question()
        except Exception as e:
            self.log(f"⚠️ Startup post failed (non-fatal): {e}")
        
        self.log("⏰ Scheduler active. Waiting for next job...")
        
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                self.log(f"⚠️ Scheduler error (continuing): {e}")
            time.sleep(60)

if __name__ == "__main__":
    print("=" * 60)
    print("🦞 MOLTBOOK INTELLIGENT ENGAGEMENT & AUTOMATION")
    print("=" * 60)
    
    agent = MoltbookAgent()
    # Run the scheduler loop (this blocks forever)
    agent.run_scheduler()
