import requests
import json
import time
import os
from datetime import datetime, timedelta
from collections import Counter
import random
import subprocess
import sys
import schedule


class MoltbookAgent:
    # ── Hard Safety Limits ────────────────────────────────────
    MAX_UPVOTES_PER_DAY = 15
    MAX_COMMENTS_PER_DAY = 3
    MAX_API_CALLS_PER_HOUR = 30
    MAX_CONSECUTIVE_ERRORS = 5
    BASE_BACKOFF_SECONDS = 60  # 1 min, doubles each failure

    def __init__(self, credentials_file='moltbook_credentials.json', knowledge_file='knowledge.json'):
        # ── Load API key: env var first, file fallback ────────
        self.api_key = os.environ.get('MOLTBOOK_API_KEY')
        if not self.api_key:
            try:
                with open(credentials_file, 'r') as f:
                    creds = json.load(f)
                self.api_key = creds.get('api_key', '')
            except FileNotFoundError:
                self.api_key = ''

        if not self.api_key:
            raise RuntimeError("No MOLTBOOK_API_KEY env var or credentials file found")

        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://www.moltbook.com/api/v1"
        self.knowledge_file = knowledge_file
        self.state_file = 'agent_state.json'

        # Load knowledge base
        try:
            with open(self.knowledge_file, 'r') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            self.knowledge_base = {
                "posts": [],
                "metadata": {"total_saved": 0, "last_updated": None, "version": "2.0"}
            }

        # Load persistent agent state (circuit breaker, counters, trends)
        self._load_state()

    # ── State persistence ─────────────────────────────────────

    def _load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.state = {}

        today = datetime.now().strftime('%Y-%m-%d')

        # Reset daily counters if new day
        if self.state.get('counter_date') != today:
            self.state['counter_date'] = today
            self.state['upvotes_today'] = 0
            self.state['comments_today'] = 0
            self.state['api_calls_today'] = 0

        # Circuit breaker
        self.state.setdefault('consecutive_errors', 0)
        self.state.setdefault('circuit_open_until', None)
        self.state.setdefault('last_backoff', self.BASE_BACKOFF_SECONDS)

        # Hourly API counter
        self.state.setdefault('api_calls_this_hour', 0)
        self.state.setdefault('hour_started', datetime.now().isoformat())

        # Trend tracking
        self.state.setdefault('trend_history', {})  # {date: {keyword: count}}
        self.state.setdefault('daily_digest', {})

        self._save_state()

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    # ── Logging ───────────────────────────────────────────────

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    # ── Circuit Breaker ───────────────────────────────────────

    def _circuit_is_open(self):
        """Check if circuit breaker is tripped (too many errors)."""
        if self.state.get('circuit_open_until'):
            until = datetime.fromisoformat(self.state['circuit_open_until'])
            if datetime.now() < until:
                self.log(f"CIRCUIT OPEN — backing off until {until.strftime('%H:%M:%S')}")
                return True
            # Circuit recovered
            self.state['circuit_open_until'] = None
            self.state['consecutive_errors'] = 0
            self.state['last_backoff'] = self.BASE_BACKOFF_SECONDS
            self._save_state()
        return False

    def _record_success(self):
        self.state['consecutive_errors'] = 0
        self.state['last_backoff'] = self.BASE_BACKOFF_SECONDS
        self._save_state()

    def _record_error(self, context=""):
        self.state['consecutive_errors'] += 1
        errors = self.state['consecutive_errors']
        self.log(f"ERROR #{errors} ({context})")

        if errors >= self.MAX_CONSECUTIVE_ERRORS:
            backoff = min(self.state['last_backoff'] * 2, 3600)  # max 1 hour
            self.state['last_backoff'] = backoff
            until = datetime.now() + timedelta(seconds=backoff)
            self.state['circuit_open_until'] = until.isoformat()
            self.log(f"CIRCUIT BREAKER TRIPPED — pausing for {backoff}s (until {until.strftime('%H:%M:%S')})")

        self._save_state()

    # ── Rate Limiting ─────────────────────────────────────────

    def _check_hourly_limit(self):
        hour_started = datetime.fromisoformat(self.state['hour_started'])
        if datetime.now() - hour_started > timedelta(hours=1):
            self.state['api_calls_this_hour'] = 0
            self.state['hour_started'] = datetime.now().isoformat()

        if self.state['api_calls_this_hour'] >= self.MAX_API_CALLS_PER_HOUR:
            self.log("Hourly API limit reached, skipping")
            return False
        return True

    def _count_api_call(self):
        self.state['api_calls_this_hour'] += 1
        self.state['api_calls_today'] += 1
        self._save_state()

    def _can_upvote(self):
        return self.state['upvotes_today'] < self.MAX_UPVOTES_PER_DAY

    def _can_comment(self):
        return self.state['comments_today'] < self.MAX_COMMENTS_PER_DAY

    # ── Safe API wrapper ──────────────────────────────────────

    def _api_call(self, method, url, **kwargs):
        """All API calls go through here — circuit breaker + rate limit enforced."""
        if self._circuit_is_open():
            return None
        if not self._check_hourly_limit():
            return None

        self._count_api_call()
        try:
            resp = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
            if resp.status_code in (200, 201):
                self._record_success()
                return resp
            elif resp.status_code == 429:
                self.log("Rate limited by Moltbook API — backing off")
                self._record_error("429 rate limit")
                return None
            elif resp.status_code >= 500:
                self._record_error(f"Server error {resp.status_code}")
                return None
            else:
                return resp  # 4xx client errors aren't circuit-worthy
        except requests.exceptions.Timeout:
            self._record_error("Timeout")
            return None
        except requests.exceptions.ConnectionError:
            self._record_error("Connection failed")
            return None
        except Exception as e:
            self._record_error(str(e))
            return None

    # ── Core API methods ──────────────────────────────────────

    def get_profile(self):
        resp = self._api_call('GET', f"{self.base_url}/agents/me")
        if resp and resp.status_code == 200:
            return resp.json().get('agent', {})
        return None

    def get_feed(self, sort='hot', limit=15):
        resp = self._api_call('GET', f"{self.base_url}/posts?sort={sort}&limit={limit}")
        if resp and resp.status_code == 200:
            return resp.json().get('posts', [])
        return []

    def upvote_post(self, post_id):
        if not self._can_upvote():
            self.log(f"Daily upvote limit ({self.MAX_UPVOTES_PER_DAY}) reached")
            return False
        resp = self._api_call('POST', f"{self.base_url}/posts/{post_id}/upvote")
        if resp and resp.status_code == 200:
            self.state['upvotes_today'] += 1
            self._save_state()
            return True
        return False

    def comment_on_post(self, post_id, content):
        if not self._can_comment():
            self.log(f"Daily comment limit ({self.MAX_COMMENTS_PER_DAY}) reached")
            return False
        resp = self._api_call('POST', f"{self.base_url}/posts/{post_id}/comments",
                              json={"content": content})
        if resp and resp.status_code == 201:
            self.state['comments_today'] += 1
            self._save_state()
            return True
        return False

    def create_post(self, title, content, submolt="general"):
        resp = self._api_call('POST', f"{self.base_url}/posts",
                              json={"title": title, "content": content, "submolt": submolt})
        if resp:
            return resp.status_code == 201, resp.json()
        return False, {}

    # ── Intelligence Scoring (1-100) ──────────────────────────

    def score_post(self, post):
        """Score a post 0-100 for money-making intelligence value."""
        title = (post.get('title') or '').lower()
        content = (post.get('content') or '').lower()
        text = f"{title} {content}"
        score = 0
        matched_categories = []

        # TIER 1: Direct money signals (+20 each, max 40)
        tier1 = [
            'made $', 'earned $', 'revenue:', 'profit:', 'mrr', 'arr',
            'first sale', 'first customer', 'paying customer', 'sold for',
            'monthly recurring', 'passive income', 'quit job'
        ]
        t1_hits = sum(1 for k in tier1 if k in text)
        if t1_hits:
            score += min(t1_hits * 20, 40)
            matched_categories.append('proven-revenue')

        # TIER 2: Business model signals (+12 each, max 24)
        tier2 = [
            'saas', 'micro saas', 'subscription', 'freemium', 'marketplace',
            'affiliate', 'digital product', 'online course', 'template',
            'chrome extension', 'wordpress plugin', 'api as a service'
        ]
        t2_hits = sum(1 for k in tier2 if k in text)
        if t2_hits:
            score += min(t2_hits * 12, 24)
            matched_categories.append('business-model')

        # TIER 3: Actionable builder signals (+8 each, max 16)
        tier3 = [
            'mvp', 'ship', 'launched', 'validate', 'product market fit',
            'build in public', 'bootstrapped', 'indie hacker', 'solopreneur',
            'weekend project', 'built in 24h', 'built in a week'
        ]
        t3_hits = sum(1 for k in tier3 if k in text)
        if t3_hits:
            score += min(t3_hits * 8, 16)
            matched_categories.append('actionable')

        # TIER 4: Automation / AI for profit (+6 each, max 12)
        tier4 = [
            'ai automation', 'automation business', 'chatbot business',
            'sell automation', 'ai agent', 'ai tool', 'workflow automation',
            'no code saas', 'n8n', 'make.com', 'zapier'
        ]
        t4_hits = sum(1 for k in tier4 if k in text)
        if t4_hits:
            score += min(t4_hits * 6, 12)
            matched_categories.append('ai-automation')

        # BONUS: High community engagement
        post_score = post.get('score', 0)
        comments = post.get('comment_count', 0)
        if post_score > 20:
            score += 5
        if comments > 50:
            score += 3

        return min(score, 100), matched_categories

    def is_interesting(self, post):
        """Returns True if post scores above threshold."""
        score, _ = self.score_post(post)
        return score >= 10

    # ── Trend Tracking ────────────────────────────────────────

    TRACKED_TRENDS = [
        'saas', 'ai agent', 'automation', 'chrome extension', 'chatbot',
        'no code', 'marketplace', 'template', 'api', 'subscription',
        'affiliate', 'wordpress', 'course', 'community', 'newsletter',
        'indie hacker', 'bootstrap', 'passive income'
    ]

    def _track_trends(self, posts):
        """Count keyword appearances in today's feed for trend detection."""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.state['trend_history']:
            self.state['trend_history'][today] = {}

        day_counts = self.state['trend_history'][today]
        for post in posts:
            text = f"{post.get('title', '')} {post.get('content', '')}".lower()
            for keyword in self.TRACKED_TRENDS:
                if keyword in text:
                    day_counts[keyword] = day_counts.get(keyword, 0) + 1

        self._save_state()

    def get_trending_keywords(self, days=7):
        """Compare this week vs last week to find rising trends."""
        today = datetime.now()
        this_week = Counter()
        last_week = Counter()

        for i in range(days):
            day_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            day_data = self.state['trend_history'].get(day_str, {})
            for k, v in day_data.items():
                this_week[k] += v

        for i in range(days, days * 2):
            day_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            day_data = self.state['trend_history'].get(day_str, {})
            for k, v in day_data.items():
                last_week[k] += v

        trends = []
        for keyword in self.TRACKED_TRENDS:
            now = this_week.get(keyword, 0)
            before = last_week.get(keyword, 0)
            if now > 0:
                change = ((now - before) / max(before, 1)) * 100
                trends.append({
                    'keyword': keyword,
                    'this_week': now,
                    'last_week': before,
                    'change_pct': round(change, 1),
                    'direction': 'up' if change > 10 else ('down' if change < -10 else 'stable')
                })

        trends.sort(key=lambda x: x['change_pct'], reverse=True)
        return trends

    # ── Knowledge Base ────────────────────────────────────────

    def save_to_knowledge_base(self, post, score=0, categories=None):
        post_id = post.get('id')
        for saved in self.knowledge_base['posts']:
            if saved.get('id') == post_id:
                return False

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
            "intelligence_score": score,
            "categories": categories or [],
            "tags": []
        }

        self.knowledge_base['posts'].append(saved_entry)
        self.knowledge_base['metadata']['total_saved'] = len(self.knowledge_base['posts'])
        self.knowledge_base['metadata']['last_updated'] = datetime.now().isoformat()

        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        return True

    # ── Daily Digest Generator ────────────────────────────────

    def generate_daily_digest(self):
        """Build a daily digest of top intelligence collected today."""
        today = datetime.now().strftime('%Y-%m-%d')
        todays_posts = [
            p for p in self.knowledge_base['posts']
            if p.get('saved_at', '').startswith(today)
        ]
        todays_posts.sort(key=lambda x: x.get('intelligence_score', 0), reverse=True)

        digest = {
            'date': today,
            'generated_at': datetime.now().isoformat(),
            'total_scanned': self.state.get('api_calls_today', 0),
            'ideas_saved': len(todays_posts),
            'top_ideas': todays_posts[:5],
            'trends': self.get_trending_keywords(days=7),
            'safety': {
                'upvotes_today': self.state.get('upvotes_today', 0),
                'comments_today': self.state.get('comments_today', 0),
                'api_calls_today': self.state.get('api_calls_today', 0),
                'circuit_status': 'OPEN' if self.state.get('circuit_open_until') else 'CLOSED',
                'consecutive_errors': self.state.get('consecutive_errors', 0)
            }
        }

        self.state['daily_digest'] = digest
        self._save_state()
        self.log(f"Daily digest generated: {len(todays_posts)} ideas, top score: {todays_posts[0]['intelligence_score'] if todays_posts else 0}")
        return digest

    # ── Main Engagement Loop ──────────────────────────────────

    def engage_with_feed(self):
        """Core engagement cycle — scan, score, upvote, save, track."""
        if self._circuit_is_open():
            self.log("Circuit breaker open, skipping engagement cycle")
            return

        self.log("Starting engagement cycle...")

        profile = self.get_profile()
        if profile:
            self.log(f"Karma: {profile.get('karma', 0)}")

        posts = self.get_feed(sort='hot', limit=15)
        if not posts:
            self.log("No posts in feed")
            return

        self.log(f"Scanned {len(posts)} posts")

        # Track trends from this batch
        self._track_trends(posts)

        # Score and engage
        engaged = 0
        for post in posts:
            if engaged >= 3:
                break

            intel_score, categories = self.score_post(post)

            if intel_score >= 10:
                post_id = post.get('id')
                title = post.get('title', 'Untitled')
                author = post.get('author', {}).get('name', 'Unknown')

                self.log(f"  [{intel_score}/100] '{title[:60]}' by {author} {categories}")

                # Always save to knowledge base
                self.save_to_knowledge_base(post, intel_score, categories)

                # Upvote quality posts
                if intel_score >= 15 and not post.get('user_vote') and self._can_upvote():
                    if self.upvote_post(post_id):
                        self.log(f"    Upvoted")
                        engaged += 1
                        time.sleep(2)

        self.log(f"Cycle complete: {engaged} interactions")

    def post_strategic_question(self):
        """Run the post creator script."""
        self.log("Triggering Post Creator...")
        try:
            subprocess.run([sys.executable, 'post_creator.py'], check=True, timeout=120)
            self.log("Post Creator finished.")
        except Exception as e:
            self.log(f"Post Creator failed: {e}")

    def collect_comments(self):
        self.log("Triggering Comment Collector...")
        try:
            subprocess.run([sys.executable, 'comment_collector.py'], check=True, timeout=120)
            self.log("Comment Collector finished.")
        except Exception as e:
            self.log(f"Comment Collector failed: {e}")

    def analyze_comments(self):
        self.log("Triggering Comment Analyzer...")
        try:
            subprocess.run([sys.executable, 'comment_analyzer.py'], check=True, timeout=120)
            self.log("Comment Analyzer finished.")
        except Exception as e:
            self.log(f"Comment Analyzer failed: {e}")

    def monitor_feed(self):
        self.log("Monitoring feed for opportunities...")
        try:
            subprocess.run([sys.executable, 'feed_monitor.py'], check=True, timeout=120)
            self.log("Feed Monitor finished.")
        except Exception as e:
            self.log(f"Feed Monitor failed: {e}")

    # ── Schedule ──────────────────────────────────────────────

    def setup_automation_schedule(self):
        # Engage with feed every 2 hours
        schedule.every(2).hours.do(self.safe_engage)

        # Monitor feed every 4 hours
        schedule.every(4).hours.do(self.monitor_feed)

        # Collect and analyze comments every 12 hours
        schedule.every(12).hours.do(self.collect_comments)
        schedule.every(12).hours.do(self.analyze_comments)

        # Generate daily digest at end of day
        schedule.every().day.at("23:00").do(self.safe_digest)

        # Auto-posting: DISABLED — manual only via `python post_creator.py`

        self.log("Schedule configured:")
        self.log("   Engage feed:       every 2 hours")
        self.log("   Monitor feed:      every 4 hours")
        self.log("   Collect comments:  every 12 hours")
        self.log("   Analyze comments:  every 12 hours")
        self.log("   Daily digest:      23:00")
        self.log("   Auto-posting:      DISABLED")

    def safe_engage(self):
        try:
            self.engage_with_feed()
        except Exception as e:
            self.log(f"Engage failed (non-fatal): {e}")

    def safe_digest(self):
        try:
            self.generate_daily_digest()
        except Exception as e:
            self.log(f"Digest failed (non-fatal): {e}")

    def run_scheduler(self):
        self.log("=" * 50)
        self.log("MOLTBOOK INTELLIGENCE AGENT v2.0")
        self.log("=" * 50)

        self.setup_automation_schedule()

        # Run initial engagement on startup (NO auto-posting)
        self.log("Running startup engagement scan...")
        try:
            self.engage_with_feed()
        except Exception as e:
            self.log(f"Startup engage failed (non-fatal): {e}")

        self.log("Scheduler active — waiting for next job...")

        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                self.log(f"Scheduler error (continuing): {e}")
            time.sleep(60)

if __name__ == "__main__":
    agent = MoltbookAgent()
    agent.run_scheduler()
