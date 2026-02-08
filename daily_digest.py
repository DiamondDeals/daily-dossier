#!/usr/bin/env python3
"""
Daily Business Digest - Reddit + Twitter
Combined pain point detection from both platforms
"""
import json
import sys
from datetime import datetime

# Import our modules
from reddit_json_client import RedditJSONClient
from business_lead_detector import BusinessLeadDetector
from twitter_monitor_100 import TwitterMonitor100

def generate_daily_digest():
    """Generate combined Reddit + Twitter daily digest"""
    
    print("=" * 70)
    print("DAILY BUSINESS DIGEST")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print("=" * 70)
    
    # === REDDIT SECTION ===
    print("\n🔍 SCANNING REDDIT...")
    print("-" * 70)
    
    reddit_client = RedditJSONClient()
    detector = BusinessLeadDetector()
    
    # Top business subreddits
    subreddits = [
        'Entrepreneur', 'smallbusiness', 'startups', 'SaaS',
        'AgencyAutomation', 'AiForSmallBusiness', 'freelance',
        'productivity', 'digitalnomad', 'ecommerce'
    ]
    
    all_reddit_leads = []
    
    for subreddit in subreddits:
        print(f"  Checking r/{subreddit}...", end=" ")
        posts = reddit_client.fetch_posts(subreddit, limit=25, sort='hot')
        
        # Score and detect business leads
        for post in posts:
            keyword_count, matched_keywords = detector.score_post(post)
            if keyword_count >= 2:  # Minimum 2 keywords
                lead = {
                    'title': post['title'],
                    'subreddit': post['subreddit'],
                    'author': post['author'],
                    'url': post['url'],
                    'score': post['score'],
                    'num_comments': post['num_comments'],
                    'engagement_score': post['engagement_score'],
                    'keyword_count': keyword_count,
                    'matched_keywords': matched_keywords
                }
                all_reddit_leads.append(lead)
        
        print(f"✅")
    
    # Sort by engagement + keywords
    all_reddit_leads.sort(key=lambda x: x['engagement_score'] + (x['keyword_count'] * 10), reverse=True)
    
    print(f"\n✅ Reddit: Found {len(all_reddit_leads)} leads")
    
    # === TWITTER SECTION ===
    print("\n🐦 SCANNING TWITTER (112 ACCOUNTS)...")
    print("-" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    twitter_monitor = TwitterMonitor100(bearer_token)
    twitter_leads = twitter_monitor.scan_accounts(max_accounts=30, tweets_per_account=10)
    
    print(f"\n✅ Twitter: Found {len(twitter_leads)} pain points")
    
    # === GENERATE REPORT ===
    print("\n" + "=" * 70)
    print("📊 DAILY DIGEST SUMMARY")
    print("=" * 70)
    
    report = []
    report.append("# 🚀 Daily Business Opportunities Digest")
    report.append(f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p PST')}*\n")
    report.append("---\n")
    
    # Reddit Section
    report.append("## 📊 REDDIT - Top 10 Business Leads\n")
    
    for i, lead in enumerate(all_reddit_leads[:10], 1):
        report.append(f"**{i}. {lead['title']}**")
        report.append(f"- 📍 r/{lead['subreddit']} • 👤 u/{lead['author']}")
        report.append(f"- 📈 Engagement: {lead['engagement_score']} (↑{lead['score']} + 💬{lead['num_comments']})")
        report.append(f"- 🔑 Keywords: {', '.join(lead['matched_keywords'][:3])}")
        report.append(f"- 🔗 {lead['url']}\n")
    
    report.append(f"*Total Reddit leads: {len(all_reddit_leads)}*\n")
    report.append("---\n")
    
    # Twitter Section
    report.append("## 🐦 TWITTER - Top 10 Pain Points\n")
    
    for i, point in enumerate(twitter_leads[:10], 1):
        report.append(f"**{i}. @{point['author']}**")
        report.append(f"- 📊 Score: {point['total_score']} ({point['keyword_count']} keywords + {point['engagement_score']} engagement)")
        report.append(f"- 🔑 {', '.join(point['matched_keywords'][:3])}")
        report.append(f"- 💬 \"{point['text'][:150]}...\"")
        report.append(f"- 🔗 {point['url']}\n")
    
    report.append(f"*Total Twitter leads: {len(twitter_leads)}*\n")
    report.append("---\n")
    
    # Stats
    report.append("## 📈 Stats\n")
    report.append(f"- **Reddit:** {len(subreddits)} subreddits scanned, {len(all_reddit_leads)} leads found")
    report.append(f"- **Twitter:** 30 accounts scanned, {len(twitter_leads)} pain points found")
    report.append(f"- **Total opportunities:** {len(all_reddit_leads) + len(twitter_leads)}\n")
    
    # Print to console
    full_report = '\n'.join(report)
    print("\n" + full_report)
    
    # Save to file
    filename = f"Exports/daily_digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w') as f:
        f.write(full_report)
    
    print(f"\n✅ Saved to: {filename}")
    
    return {
        'reddit_leads': all_reddit_leads[:10],
        'twitter_leads': twitter_leads[:10],
        'total_reddit': len(all_reddit_leads),
        'total_twitter': len(twitter_leads),
        'report': full_report
    }

if __name__ == '__main__':
    try:
        result = generate_daily_digest()
        print("\n" + "=" * 70)
        print("✅ DAILY DIGEST COMPLETE!")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Error generating digest: {e}")
        sys.exit(1)
