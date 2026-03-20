import json
import sys

# YOUR SKILLS (full stack + AI + business)
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

def analyze_feasibility(post):
    """Analyze if YOU can build this and make money"""
    
    title = post.get('title', '').lower()
    content = post.get('content', '').lower()
    text = f"{title} {content}"
    
    # Scoring system
    score = 0
    reasons_can_do = []
    reasons_cant_do = []
    time_estimate = "Unknown"
    difficulty = "Unknown"
    profit_potential = "Unknown"
    
    # Check skill match
    skill_matches = []
    for category, skills in YOUR_SKILLS.items():
        for skill in skills:
            if skill.lower() in text:
                skill_matches.append(skill)
                score += 10
    
    if skill_matches:
        reasons_can_do.append(f"Uses your skills: {', '.join(skill_matches[:3])}")
    
    # Money-making indicators
    if any(word in text for word in ['saas', 'subscription', 'mrr', 'arr']):
        score += 20
        reasons_can_do.append("Recurring revenue model (good!)")
        profit_potential = "High (recurring income)"
    
    if any(word in text for word in ['made $', 'earned $', 'revenue', 'profit']):
        score += 15
        reasons_can_do.append("Has proven revenue results!")
    
    if any(word in text for word in ['wordpress', 'woocommerce', 'plugin']):
        score += 25
        reasons_can_do.append("WordPress/WooCommerce (YOUR EXPERTISE!)")
        time_estimate = "2-4 weeks"
        difficulty = "Medium (you know this!)"
    
    if any(word in text for word in ['chatbot', 'automation', 'n8n', 'workflow']):
        score += 25
        reasons_can_do.append("Automation/chatbot (YOUR EXPERTISE!)")
        time_estimate = "1-3 weeks"
        difficulty = "Easy-Medium"
    
    if any(word in text for word in ['template', 'boilerplate', 'starter']):
        score += 15
        reasons_can_do.append("Can package your existing code!")
        time_estimate = "1 week"
        difficulty = "Easy"
        profit_potential = "Medium (one-time sales)"
    
    if any(word in text for word in ['no code', 'low code', 'bubble', 'webflow']):
        score += 10
        reasons_can_do.append("No-code = faster to build")
        time_estimate = "1-2 weeks"
        difficulty = "Easy"
    
    # Quick win indicators
    if any(word in text for word in ['weekend project', 'built in 24h', 'simple', 'easy']):
        score += 20
        reasons_can_do.append("Quick to build!")
        time_estimate = "Weekend project"
        difficulty = "Easy"
    
    # Red flags
    if any(word in text for word in ['blockchain', 'crypto', 'defi', 'smart contract']):
        score -= 15
        reasons_cant_do.append("Requires blockchain knowledge")
    
    if any(word in text for word in ['machine learning', 'deep learning', 'model training']):
        score -= 10
        reasons_cant_do.append("Requires ML expertise")
    
    if any(word in text for word in ['mobile', 'ios', 'android', 'app store']):
        score -= 5
        reasons_cant_do.append("Mobile development (not your strength)")
    
    # Final assessment
    if score >= 50:
        verdict = "🟢 HIGHLY FEASIBLE - BUILD THIS!"
        recommendation = "This matches your skills perfectly. You should build this ASAP."
    elif score >= 30:
        verdict = "🟡 FEASIBLE - Consider Building"
        recommendation = "You can build this with some learning. Good opportunity."
    elif score >= 10:
        verdict = "🟠 CHALLENGING - Requires New Skills"
        recommendation = "Possible but requires significant learning. Consider if worth the time."
    else:
        verdict = "🔴 NOT RECOMMENDED"
        recommendation = "Doesn't match your skills well. Focus on better-fit opportunities."
    
    return {
        "score": score,
        "verdict": verdict,
        "recommendation": recommendation,
        "reasons_can_do": reasons_can_do,
        "reasons_cant_do": reasons_cant_do,
        "time_estimate": time_estimate,
        "difficulty": difficulty,
        "profit_potential": profit_potential,
        "skill_matches": skill_matches
    }

def analyze_all():
    """Analyze ALL ideas in knowledge base"""
    
    try:
        with open('knowledge.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        print("❌ No knowledge base found!")
        return
    
    posts = knowledge.get('posts', [])
    
    if not posts:
        print("📭 No ideas saved yet. Run moltbook_engage.py first!")
        return
    
    # Analyze each
    analyzed = []
    for post in posts:
        analysis = analyze_feasibility(post)
        analyzed.append({
            "post": post,
            "analysis": analysis
        })
    
    # Sort by feasibility score
    analyzed.sort(key=lambda x: x['analysis']['score'], reverse=True)
    
    # Display results
    print("=" * 70)
    print("🎯 MONEY-MAKING IDEAS - ANALYZED FOR YOU")
    print("=" * 70)
    print(f"\nTotal ideas: {len(analyzed)}\n")
    
    for i, item in enumerate(analyzed, 1):
        post = item['post']
        analysis = item['analysis']
        
        print(f"\n{'='*70}")
        print(f"IDEA #{i}: {post.get('title', 'Untitled')}")
        print(f"{'='*70}")
        print(f"👤 By: {post.get('author', 'Unknown')}")
        print(f"⭐ Engagement: {post.get('score', 0)} upvotes, {post.get('comment_count', 0)} comments")
        print()
        
        print(f"📊 FEASIBILITY SCORE: {analysis['score']}/100")
        print(f"🎯 {analysis['verdict']}")
        print()
        
        print(f"💡 RECOMMENDATION:")
        print(f"   {analysis['recommendation']}")
        print()
        
        if analysis['reasons_can_do']:
            print("✅ WHY YOU CAN DO THIS:")
            for reason in analysis['reasons_can_do']:
                print(f"   • {reason}")
            print()
        
        if analysis['reasons_cant_do']:
            print("❌ CHALLENGES:")
            for reason in analysis['reasons_cant_do']:
                print(f"   • {reason}")
            print()
        
        print(f"⏱️ TIME ESTIMATE: {analysis['time_estimate']}")
        print(f"🎓 DIFFICULTY: {analysis['difficulty']}")
        print(f"💰 PROFIT POTENTIAL: {analysis['profit_potential']}")
        print()
        
        # Show snippet
        content = post.get('content', '')
        if content:
            snippet = content[:200] + "..." if len(content) > 200 else content
            print(f"📝 SUMMARY:")
            print(f"   {snippet}")
        print()
        
        print(f"🔗 Full post: {post.get('url', 'No URL')}")
        print()
    
    # Top 3 recommendations
    print("\n" + "=" * 70)
    print("🏆 TOP 3 RECOMMENDATIONS FOR YOU")
    print("=" * 70)
    for i, item in enumerate(analyzed[:3], 1):
        post = item['post']
        analysis = item['analysis']
        print(f"\n{i}. {post.get('title', 'Untitled')}")
        print(f"   Score: {analysis['score']}/100 | {analysis['verdict']}")
        print(f"   {analysis['recommendation']}")

if __name__ == "__main__":
    analyze_all()
