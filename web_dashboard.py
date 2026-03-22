from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)

# Import analysis function
import sys
sys.path.append(os.path.dirname(__file__))
from analyze_ideas import analyze_feasibility, YOUR_SKILLS

def load_knowledge():
    """Load knowledge base"""
    try:
        with open('knowledge.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"posts": [], "metadata": {}}

def load_seen():
    """Load seen posts"""
    try:
        with open('seen_posts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"seen": [], "last_check": None}

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    knowledge = load_knowledge()
    seen = load_seen()
    
    posts = knowledge.get('posts', [])
    seen_ids = set(seen.get('seen', []))
    new_count = len([p for p in posts if p.get('id') not in seen_ids])
    
    return jsonify({
        'total_posts': len(posts),
        'new_posts': new_count,
        'seen_posts': len(seen_ids),
        'last_check': seen.get('last_check'),
        'last_updated': knowledge.get('metadata', {}).get('last_updated')
    })

@app.route('/api/ideas')
def get_ideas():
    """Get all ideas with AI analysis"""
    
    # Try to load AI-analyzed ideas first
    try:
        with open('ai_analyzed_ideas.json', 'r') as f:
            analyzed = json.load(f)
        
        # Transform to match frontend format
        ideas = []
        for item in analyzed:
            post = item['post']
            ai = item['ai_analysis']
            
            ideas.append({
                'id': post.get('id'),
                'title': post.get('title', 'Untitled'),
                'author': post.get('author', 'Unknown'),
                'submolt': post.get('submolt', 'general'),
                'content': post.get('content', ''),
                'url': post.get('url', ''),
                'score': post.get('score', 0),
                'comment_count': post.get('comment_count', 0),
                'created_at': post.get('created_at', ''),
                'saved_at': post.get('saved_at', ''),
                'analysis': {
                    'feasibility_score': ai.get('feasibility_score', 0),
                    'verdict': get_verdict(ai.get('feasibility_score', 0)),
                    'recommendation': ai.get('recommendation', ''),
                    'reasons_can_do': ai.get('skill_match_details', []),
                    'reasons_cant_do': ai.get('missing_skills', []),
                    'time_estimate': ai.get('time_to_build', 'Unknown'),
                    'difficulty': ai.get('difficulty', 'Unknown'),
                    'profit_potential': ai.get('profit_potential', 'Unknown'),
                    'is_ai_analysis': True,  # Flag to show this is AI-powered
                    'business_model': ai.get('business_model', 'Unknown'),
                    'tags': ai.get('tags', []),
                    'key_insights': ai.get('key_insights', [])
                }
            })
        
        return jsonify(ideas)
        
    except FileNotFoundError:
        # Fall back to knowledge base with keyword analysis
        knowledge = load_knowledge()
        posts = knowledge.get('posts', [])
        
        analyzed = []
        for post in posts:
            analysis = analyze_feasibility(post)
            analyzed.append({
                'id': post.get('id'),
                'title': post.get('title', 'Untitled'),
                'author': post.get('author', 'Unknown'),
                'submolt': post.get('submolt', 'general'),
                'content': post.get('content', ''),
                'url': post.get('url', ''),
                'score': post.get('score', 0),
                'comment_count': post.get('comment_count', 0),
                'created_at': post.get('created_at', ''),
                'saved_at': post.get('saved_at', ''),
                'analysis': {
                    'feasibility_score': analysis['score'],
                    'verdict': analysis['verdict'],
                    'recommendation': analysis['recommendation'],
                    'reasons_can_do': analysis['reasons_can_do'],
                    'reasons_cant_do': analysis['reasons_cant_do'],
                    'time_estimate': analysis['time_estimate'],
                    'difficulty': analysis['difficulty'],
                    'profit_potential': analysis['profit_potential'],
                    'is_ai_analysis': False  # Flag to show this is keyword-based
                }
            })
        
        analyzed.sort(key=lambda x: x['analysis']['feasibility_score'], reverse=True)
        return jsonify(analyzed)

def get_verdict(score):
    """Get verdict based on score"""
    if score >= 70:
        return "🟢 HIGHLY FEASIBLE"
    elif score >= 50:
        return "🟢 FEASIBLE"
    elif score >= 30:
        return "🟡 FEASIBLE - Consider Building"
    elif score >= 10:
        return "🟠 CHALLENGING"
    else:
        return "🔴 NOT RECOMMENDED"

@app.route('/api/new')
def get_new_ideas():
    """Get only new ideas"""
    knowledge = load_knowledge()
    seen = load_seen()
    
    posts = knowledge.get('posts', [])
    seen_ids = set(seen.get('seen', []))
    
    new_posts = [p for p in posts if p.get('id') not in seen_ids]
    
    # Analyze new posts
    analyzed = []
    for post in new_posts:
        analysis = analyze_feasibility(post)
        analyzed.append({
            'id': post.get('id'),
            'title': post.get('title', 'Untitled'),
            'author': post.get('author', 'Unknown'),
            'content': post.get('content', ''),
            'url': post.get('url', ''),
            'analysis': analysis
        })
    
    analyzed.sort(key=lambda x: x['analysis']['score'], reverse=True)
    
    return jsonify(analyzed)

@app.route('/api/my-posts')
def get_my_posts():
    """Get user's posts with comment counts"""
    try:
        with open('my_posts_with_comments.json', 'r') as f:
            data = json.load(f)
        
        posts = []
        for post in data.get('posts', []):
            posts.append({
                'id': post.get('id'),
                'content': post.get('content', ''),
                'created_at': post.get('created_at', ''),
                'score': post.get('score', 0),
                'comment_count': post.get('comment_count', 0),
                'url': post.get('url', '')
            })
        
        return jsonify({
            'total_posts': data.get('total_posts', 0),
            'total_comments': data.get('total_comments', 0),
            'collected_at': data.get('collected_at', ''),
            'posts': posts
        })
    except FileNotFoundError:
        return jsonify({
            'total_posts': 0,
            'total_comments': 0,
            'posts': []
        })

@app.route('/api/comment-opportunities')
def get_comment_opportunities():
    """Get AI-analyzed comment opportunities"""
    try:
        min_score = int(request.args.get('min_score', 70))
        
        if os.path.exists('comment_opportunities.json'):
            with open('comment_opportunities.json', 'r') as f:
                data = json.load(f)
            
            # Filter by minimum score
            opportunities = data.get('opportunities', [])
            filtered = [opp for opp in opportunities if opp.get('analysis', {}).get('feasibility_score', 0) >= min_score]
            
            return jsonify({
                'analyzed_at': data.get('analyzed_at'),
                'total_comments_analyzed': data.get('total_comments_analyzed'),
                'services_found': len(filtered),
                'opportunities': filtered
            })
        else:
            return jsonify({
                'services_found': 0,
                'opportunities': []
            })
    
    except Exception as e:
        print(f"Error in get_comment_opportunities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feed-opportunities')
def get_feed_opportunities():
    """Get opportunities from feed monitoring"""
    try:
        min_score = int(request.args.get('min_score', 70))
        
        if os.path.exists('feed_opportunities.json'):
            with open('feed_opportunities.json', 'r') as f:
                data = json.load(f)
            
            # Filter by minimum score
            opportunities = data.get('opportunities', [])
            filtered = [opp for opp in opportunities if opp.get('score', 0) >= min_score]
            
            return jsonify({
                'total': len(filtered),
                'scanned_at': data.get('scanned_at'),
                'opportunities': filtered
            })
        else:
            return jsonify({'total': 0, 'opportunities': []})
    
    except Exception as e:
        print(f"Error in get_feed_opportunities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/comments')
def comments_page():
    """Comments analysis page"""
    return render_template('comments.html')

@app.route('/api/mark_seen', methods=['POST'])
def mark_seen():
    """Mark ideas as seen"""
    knowledge = load_knowledge()
    seen = load_seen()
    
    # Mark all current posts as seen
    all_ids = [p.get('id') for p in knowledge.get('posts', [])]
    seen['seen'] = list(set(seen.get('seen', []) + all_ids))
    seen['last_check'] = datetime.now().isoformat()
    
    with open('seen_posts.json', 'w') as f:
        json.dump(seen, f, indent=2)

    return jsonify({"success": True, "marked": len(all_ids)})

# ── Instagram Auto-Poster routes ─────────────────────────────────

@app.route('/ig')
def ig_dashboard():
    """IG Auto-Poster dashboard page."""
    return render_template('ig_dashboard.html')

@app.route('/api/ig-cron')
def ig_cron():
    """Triggered by Render cron or external scheduler. Posts today's carousel."""
    try:
        from ig_auto_poster import run_daily_post
        result = run_daily_post()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ig-status')
def ig_status():
    """Check posting status — reads Excel from Drive."""
    try:
        from ig_auto_poster import get_drive_service, list_drive_folder, download_drive_file, DRIVE_FOLDER_ID
        import io as _io
        from openpyxl import load_workbook as _load_wb

        drive = get_drive_service()
        root_files = list_drive_folder(drive, DRIVE_FOLDER_ID)
        excel_file = next((f for f in root_files if f["name"] == "carousel_report.xlsx"), None)
        if not excel_file:
            return jsonify({"error": "Excel not found on Drive"})

        data = download_drive_file(drive, excel_file["id"])
        wb = _load_wb(_io.BytesIO(data))
        ws = wb["★ Wishlist"]

        posts = []
        for row in range(2, ws.max_row + 1):
            num = ws.cell(row=row, column=1).value
            if not num:
                continue
            posts.append({
                "num": num,
                "shortcode": ws.cell(row=row, column=2).value,
                "likes": ws.cell(row=row, column=4).value or 0,
                "slides": ws.cell(row=row, column=5).value or 0,
                "scheduled": str(ws.cell(row=row, column=8).value or ""),
                "status": ws.cell(row=row, column=11).value or "pending",
                "posted": str(ws.cell(row=row, column=12).value or ""),
            })

        return jsonify({"posts": posts, "total": len(posts)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 MOLTBOOK IDEA ANALYZER - WEB DASHBOARD")
    print("=" * 70)
    print("\n📊 Starting web server...")
    print("🌐 Open your browser to: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server\n")
    # Run on 0.0.0.0 to be accessible from outside container
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
