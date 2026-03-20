import requests
import json
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file!")

# Your skills (full stack + AI + business)
YOUR_SKILLS = {
    "web_development": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Vue.js", "Tailwind CSS", "Vercel"],
    "backend": ["Python", "Django", "Flask", "FastAPI", "Spring Boot", "Java", "API development", "REST", "GraphQL", "WebSockets"],
    "databases": ["PostgreSQL", "MongoDB", "Redis", "SQL", "Firebase", "Supabase", "Prisma"],
    "cms_platforms": ["WordPress", "WooCommerce", "Shopify", "Webflow", "Strapi"],
    "automation": ["n8n workflows", "Make.com", "Zapier", "chatbots", "automation services", "cron jobs", "workflow orchestration", "RPA"],
    "ai_tools": ["ChatGPT integration", "Claude API", "Groq", "LangChain", "voice cloning", "video generation", "Remotion", "image generation", "RAG pipelines", "AI agents", "prompt engineering"],
    "devops": ["Docker", "deployment", "Render", "Vercel", "Railway", "AWS", "CI/CD", "hosting", "Cloudflare"],
    "design": ["Landing pages", "UI/UX design", "Figma", "responsive design", "dashboards"],
    "business": ["SaaS", "freelancing", "digital products", "client management", "pricing strategy", "MVP building", "product launches", "marketplace development"]
}

def call_groq_api(prompt):
    """Call Groq API (OpenAI-compatible)"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a business analyst helping evaluate money-making opportunities for developers. Return ONLY valid JSON, no markdown."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        text = result['choices'][0]['message']['content']
        return text
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        return None

def analyze_post_with_ai(post):
    """Use Groq AI to analyze a post for money-making potential"""
    
    title = post.get('title', 'Untitled')
    content = post.get('content', '')
    author = post.get('author', 'Unknown')
    
    # Create prompt
    prompt = f"""You are analyzing posts from Moltbook (AI agent social network) to find REAL business opportunities.

**CRITICAL: What is a REAL opportunity?**
- ✅ Bot is ACTIVELY DOING a service for their human (e.g., "I built X for my human", "I do Y every day")
- ✅ Bot describes a working solution they implemented
- ✅ Action words: "I built", "I created", "I run", "I automate", "My human uses"
- ❌ NOT news, vulnerabilities, problems, or discussions
- ❌ NOT theoretical ideas or suggestions
- ❌ NOT complaints or feature requests

**Developer's Skills (FULL STACK + AI + BUSINESS):**
- Web: HTML, CSS, JavaScript, TypeScript, React, Next.js, Node.js, Vue.js, Tailwind, Vercel
- Backend: Python, Django, Flask, FastAPI, Spring Boot, Java, REST, GraphQL
- Databases: PostgreSQL, MongoDB, Redis, Firebase, Supabase, Prisma
- CMS: WordPress, WooCommerce (EXPERT), Shopify, Webflow, Strapi
- Automation: n8n, Make.com, Zapier, chatbots, RPA, workflow orchestration (EXPERT)
- AI: ChatGPT, Claude, Groq, LangChain, RAG pipelines, AI agents, voice cloning, video/image gen, prompt engineering
- DevOps: Docker, Vercel, Railway, AWS, CI/CD, Cloudflare
- Design: Landing pages, UI/UX, Figma, dashboards
- Business: SaaS, freelancing, digital products, MVP building, product launches

**Post to Analyze:**
Title: {title}
Author: {author}
Content: {content[:2000]}

**IMPORTANT ANALYSIS CRITERIA:**

1. **Is this a REAL service being provided?**
   - Look for: "I do", "I built", "I created", "I run", "My human asked me", "I automate"
   - If the post is just DISCUSSING a problem → is_business_opportunity = FALSE
   - If the post DESCRIBES what the bot ACTUALLY DOES → is_business_opportunity = TRUE

2. **Examples:**
   - ✅ "I built an email-to-podcast service for my human" → TRUE (bot provides service)
   - ✅ "I scrape data every night while my human sleeps" → TRUE (bot provides service)
   - ❌ "There's a security vulnerability in ClawdHub" → FALSE (just news/discussion)
   - ❌ "We should build a reputation system" → FALSE (suggestion, not doing it)

**Return JSON with:**
- is_business_opportunity (bool): Is the bot ACTIVELY PROVIDING a service? (Not just discussing problems)
- service_description (string): What service is the bot actually doing? ("None" if not a service)
- business_model (string): How could YOU monetize this? (SaaS/Product/Service/Not applicable)
- revenue_mentioned (bool): Does post mention actual earnings?
- revenue_amount (string): Amount if mentioned
- feasibility_score (0-100): 
  - If NOT a real service → MAX 20 points
  - If IS a service → Calculate: Skill match(30) + Speed(20) + Revenue potential(30) + Low competition(20)
- skill_match_details (array): Developer's skills this uses
- missing_skills (array): Skills developer lacks
- time_to_build (string): "1-2 weeks", "1 month", etc (or "Not applicable" if not a service)
- difficulty (string): "Easy"/"Medium"/"Hard" (or "Not applicable")
- profit_potential (string): "Low"/"Medium"/"High"/"Very High" (or "Not applicable")
- tags (array): ["service", "automation", "proven", etc] - use "discussion" or "news" for non-services
- key_insights (array): 3-5 actionable insights IF it's a service, otherwise ["This is a discussion/news post, not a service opportunity"]
- recommendation (string): Should developer build THIS SERVICE? Be HONEST. If it's not a service, say "This is not a business opportunity - it's a discussion about [topic]."
- action_items (array): First 3 steps if worth building, empty if not a service

**BE VERY STRICT:** Only score high (50+) if the bot is ACTIVELY DOING something as a service!

JSON only, no markdown:"""

    try:
        result = call_groq_api(prompt)
        
        if not result:
            return None
        
        # Clean result
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        result = result.strip()
        
        analysis = json.loads(result)
        return analysis
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        if result:
            print(f"Response: {result[:200]}...")
        return None

def analyze_all_posts():
    """Analyze all posts with AI"""
    
    try:
        with open('knowledge.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        print("❌ No knowledge base found!")
        return
    
    posts = knowledge.get('posts', [])
    
    print("=" * 70)
    print("🧠 LEVEL 2: AI-POWERED ANALYSIS (Groq)")
    print("=" * 70)
    print(f"\n📊 Analyzing {len(posts)} posts with Llama-3.3-70B...\n")
    
    analyzed_posts = []
    
    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] {post.get('title', 'Untitled')[:60]}...")
        
        analysis = analyze_post_with_ai(post)
        
        if analysis:
            analyzed_posts.append({
                'post': post,
                'ai_analysis': analysis
            })
            score = analysis.get('feasibility_score', 0)
            biz = analysis.get('business_model', 'Unknown')
            print(f"  ✅ Score: {score}/100 | Model: {biz}")
        else:
            print(f"  ❌ Failed")
    
    # Sort by score
    analyzed_posts.sort(key=lambda x: x['ai_analysis'].get('feasibility_score', 0), reverse=True)
    
    # Save
    with open('ai_analyzed_ideas.json', 'w') as f:
        json.dump(analyzed_posts, f, indent=2)
    
    print(f"\n✅ Saved to ai_analyzed_ideas.json")
    
    # Top 3
    print("\n" + "=" * 70)
    print("🏆 TOP 3 MONEY-MAKING OPPORTUNITIES")
    print("=" * 70)
    
    for i, item in enumerate(analyzed_posts[:3], 1):
        post = item['post']
        a = item['ai_analysis']
        
        print(f"\n{'='*70}")
        print(f"{i}. {post.get('title', 'Untitled')}")
        print(f"{'='*70}")
        print(f"📊 Feasibility: {a.get('feasibility_score', 0)}/100")
        print(f"💼 Business Model: {a.get('business_model', 'Unknown')}")
        print(f"⏱️ Time: {a.get('time_to_build', 'Unknown')}")
        print(f"🎓 Difficulty: {a.get('difficulty', 'Unknown')}")
        print(f"💰 Profit: {a.get('profit_potential', 'Unknown')}")
        
        if a.get('revenue_mentioned'):
            print(f"💵 Revenue Reported: {a.get('revenue_amount', 'Not specified')}")
        
        print(f"\n💡 Recommendation:")
        print(f"{a.get('recommendation', '')[:300]}...")
        
        if a.get('key_insights'):
            print(f"\n✨ Key Insights:")
            for insight in a.get('key_insights', [])[:3]:
                print(f"  • {insight}")
        
        print(f"\n🔗 {post.get('url', '')}")

if __name__ == "__main__":
    analyze_all_posts()
