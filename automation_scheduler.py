import time
import schedule
from datetime import datetime, timedelta
import json
import os

# Import our scripts
from post_creator import MoltbookPoster
from comment_collector import CommentCollector
from comment_analyzer import analyze_all_comments

class AutomationScheduler:
    def __init__(self):
        self.poster = MoltbookPoster()
        self.collector = CommentCollector()
        self.post_schedule = {}  # Track when to collect comments for each post
        
        # Load schedule
        try:
            with open('automation_schedule.json', 'r') as f:
                self.post_schedule = json.load(f)
        except FileNotFoundError:
            self.post_schedule = {'posts': []}
    
    def save_schedule(self):
        """Save the schedule"""
        with open('automation_schedule.json', 'w') as f:
            json.dump(self.post_schedule, f, indent=2)
    
    def auto_post(self):
        """Automatically post strategic question"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📝 AUTO-POSTING...")
        
        result = self.poster.post_strategic_question(min_hours=0.5)
        
        if result:
            post_id = result.get('id')
            collect_time = datetime.now() + timedelta(hours=48)
            
            # Schedule collection for this post
            self.post_schedule['posts'].append({
                'post_id': post_id,
                'posted_at': datetime.now().isoformat(),
                'collect_at': collect_time.isoformat(),
                'collected': False,
                'analyzed': False
            })
            
            self.save_schedule()
            print(f"✅ Posted! Will collect comments at: {collect_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("⏰ Too soon to post or error occurred")
    
    def auto_collect(self):
        """Check if it's time to collect comments for any post"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 💬 CHECKING FOR COMMENTS...")
        
        now = datetime.now()
        collected_any = False
        
        for post in self.post_schedule['posts']:
            if post['collected']:
                continue
            
            collect_time = datetime.fromisoformat(post['collect_at'])
            
            if now >= collect_time:
                print(f"💬 Collecting comments for post {post['post_id']}...")
                
                # Collect comments
                self.collector.collect_all_comments()
                
                post['collected'] = True
                post['collected_at'] = now.isoformat()
                collected_any = True
                
                print(f"✅ Comments collected for post {post['post_id']}!")
        
        if collected_any:
            self.save_schedule()
            # Trigger analysis
            self.auto_analyze()
        else:
            print("⏰ No posts ready for comment collection yet")
    
    def auto_analyze(self):
        """Analyze collected comments"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧠 AUTO-ANALYZING...")
        
        # Check if there are any collected but unanalyzed posts
        needs_analysis = any(p['collected'] and not p['analyzed'] for p in self.post_schedule['posts'])
        
        if needs_analysis:
            print("🧠 Analyzing comments...")
            analyze_all_comments()
            
            # Mark as analyzed
            for post in self.post_schedule['posts']:
                if post['collected'] and not post['analyzed']:
                    post['analyzed'] = True
                    post['analyzed_at'] = datetime.now().isoformat()
            
            self.save_schedule()
            print("✅ Analysis complete!")
        else:
            print("⏰ No new comments to analyze")
    
    def run_scheduler(self):
        """Run the automation scheduler"""
        print("=" * 70)
        print("🤖 MOLTBOOK AUTOMATION SCHEDULER")
        print("=" * 70)
        print("\n📅 Schedule:")
        print("  📝 Post strategic questions: Every 30 minutes")
        print("  💬 Collect comments: 48 hours after each post")
        print("  🧠 Analyze comments: Immediately after collection")
        print("\n🚀 Starting automation...\n")
        
        # Schedule jobs
        schedule.every(30).minutes.do(self.auto_post)
        schedule.every(1).hours.do(self.auto_collect)
        
        # Run once immediately
        self.auto_post()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    scheduler = AutomationScheduler()
    scheduler.run_scheduler()
