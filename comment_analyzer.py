import requests
import json
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def call_groq_api(prompt):
    """Call Groq API"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are analyzing comments on Moltbook to find real business opportunities. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    return None

def analyze_comment(comment, original_post):
    """Analyze a comment for service opportunities"""
    
    author = comment.get('author', 'Unknown')
    content = comment.get('content', '')
    
    prompt = f"""Analyze this comment for REAL money-making services.

**Original Post:**
{original_post[:200]}...

**Comment by {author}:**
{content}

**Is this comment describing a REAL service?**
- ✅ "I do X for my human" → TRUE
- ✅ "I built Y" → TRUE
- ❌ "That's interesting" → FALSE
- ❌ General discussion → FALSE

Return JSON:
- is_service (bool): Is bot describing service they provide?
- service_description (string): What service? ("None" if not a service)
- feasibility_score (0-100): How easy for developer to build? (MAX 20 if not a service)
- business_potential (string): "Low"/"Medium"/"High"/"Very High"
- key_insight (string): Main takeaway
- recommendation (string): Should developer build this?

JSON only:"""

    try:
        result = call_groq_api(prompt)
        
        if result:
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.startswith('```'):
                result = result[3:]
            if result.endswith('```'):
                result = result[:-3]
            result = result.strip()
            
            return json.loads(result)
        return None
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def analyze_all_comments():
    """Analyze all comments from my posts"""
    
    try:
        with open('my_posts_with_comments.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No comments file found! Run comment_collector.py first.")
        return
    
    print("=" * 70)
    print("🧠 COMMENT ANALYZER (Level 3)")
    print("=" * 70)
    print(f"\n📊 Analyzing comments from {data['total_posts']} posts...")
    print(f"💬 Total comments: {data['total_comments']}\n")
    
    analyzed = []
    service_count = 0
    
    for post in data['posts']:
        post_content = post.get('content', '')
        comments_wrapper = post.get('comments', {})
        
        # Handle wrapper structure
        if isinstance(comments_wrapper, dict):
            comments = comments_wrapper.get('comments', [])
        elif isinstance(comments_wrapper, list):
            comments = comments_wrapper
        else:
            comments = []
        
        print(f"\n📝 Post: {post_content[:50]}...")
        print(f"   💬 {len(comments)} comments")
        
        for i, comment in enumerate(comments, 1):
            author = comment.get('author', 'Unknown')
            print(f"   [{i}/{len(comments)}] Analyzing comment by {author}...")
            
            analysis = analyze_comment(comment, post_content)
            
            if analysis and analysis.get('is_service'):
                service_count += 1
                print(f"      ✅ SERVICE FOUND! Score: {analysis.get('feasibility_score', 0)}/100")
                
                analyzed.append({
                    'comment': comment,
                    'original_post': {
                        'id': post['id'],
                        'content': post_content,
                        'url': post['url']
                    },
                    'analysis': analysis
                })
            elif analysis:
                print(f"      ❌ Not a service (just discussion)")
    
    # Sort by feasibility
    analyzed.sort(key=lambda x: x['analysis'].get('feasibility_score', 0), reverse=True)
    
    # Save
    output = {
        "analyzed_at": data['collected_at'],
        "total_comments_analyzed": data['total_comments'],
        "services_found": service_count,
        "opportunities": analyzed
    }
    
    with open('comment_opportunities.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Found {service_count} service opportunities from {data['total_comments']} comments")
    print(f"💾 Saved to comment_opportunities.json")
    
    # Show top 3
    if analyzed:
        print("\n" + "=" * 70)
        print("🏆 TOP 3 COMMENT OPPORTUNITIES")
        print("=" * 70)
        
        for i, item in enumerate(analyzed[:3], 1):
            a = item['analysis']
            c = item['comment']
            
            print(f"\n{i}. By {c.get('author', 'Unknown')}")
            print(f"   📊 Score: {a.get('feasibility_score', 0)}/100")
            print(f"   💼 Service: {a.get('service_description', 'N/A')}")
            print(f"   💰 Potential: {a.get('business_potential', 'N/A')}")
            print(f"   💡 {a.get('recommendation', '')[:100]}...")

if __name__ == "__main__":
    analyze_all_comments()
