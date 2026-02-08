#!/usr/bin/env python3
"""
Daily Business Digest v2 - Reddit + Twitter
Simplified and working version
"""
import json
import sys
from datetime import datetime
from reddit_json_client import RedditJSONClient
from twitter_monitor_100 import TwitterMonitor100

# Business keywords
KEYWORDS = [
    "manual process", "manually", "repetitive task", "spending hours",
    "there must be a better way", "there has to be", "automate",
    "automation", "workflow", "bottleneck", "time consuming",
    "inefficient", "tedious", "overwhelming", "frustrated"
]

def score_reddit_post(post):
    """Score a Reddit post for business opportunity"""
    text = (post['title'] + ' ' + post['text']).lower()
    
    matched = []
    for keyword in KEYWORDS:
        if keyword in text:
            matched.append(keyword)
    
    return len(matched), matched

def generate_digest():
    print("=" * 70)
    print("DAILY BUSINESS DIGEST - REDDIT + TWITTER")
    print(f"{datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}")
    print("=" * 70)
    
    # REDDIT
    print("\n🔍 SCANNING REDDIT...")
    reddit_client = RedditJSONClient()
    
    subreddits = [
        'Entrepreneur', 'smallbusiness', 'startups', 'SaaS',
        'AgencyAutomation', 'AiForSmallBusiness', 'freelance',
        'productivity', 'digitalnomad', 'ecommerce'
    ]
    
    all_reddit = []
    for sub in subreddits:
        print(f"  r/{sub}...", end=" ", flush=True)
        posts = reddit_client.fetch_posts(sub, limit=25, sort='hot')
        
        for post in posts:
            count, keywords = score_reddit_post(post)
            if count >= 2:
                post['keyword_count'] = count
                post['matched_keywords'] = keywords
                all_reddit.append(post)
        print("✅")
    
    all_reddit.sort(key=lambda x: x['engagement_score'] + (x['keyword_count'] * 10), reverse=True)
    print(f"✅ Found {len(all_reddit)} Reddit leads")
    
    # TWITTER
    print("\n🐦 SCANNING TWITTER...")
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        bearer_token = [line.split('=')[1].strip() for line in f if line.startswith('BEARER_TOKEN=')][0]
    
    twitter = TwitterMonitor100(bearer_token)
    twitter_leads = twitter.scan_accounts(max_accounts=30, tweets_per_account=10)
    print(f"✅ Found {len(twitter_leads)} Twitter pain points")
    
    # GENERATE REPORT
    print("\n" + "=" * 70)
    print("📊 COMBINED REPORT")
    print("=" * 70)
    
    report = []
    report.append(f"# Daily Business Opportunities\n*{datetime.now().strftime('%B %d, %Y')}*\n")
    
    report.append("## 📊 Reddit - Top 10\n")
    for i, lead in enumerate(all_reddit[:10], 1):
        report.append(f"**{i}. {lead['title']}**")
        report.append(f"- r/{lead['subreddit']} • {lead['engagement_score']} engagement • {lead['keyword_count']} keywords")
        report.append(f"- {lead['url']}\n")
    
    report.append(f"\n## 🐦 Twitter - Top 10\n")
    for i, tw in enumerate(twitter_leads[:10], 1):
        report.append(f"**{i}. @{tw['author']}** (Score: {tw['total_score']})")
        report.append(f"- \"{tw['text'][:120]}...\"")
        report.append(f"- {tw['url']}\n")
    
    report.append(f"\n**Total: {len(all_reddit)} Reddit + {len(twitter_leads)} Twitter**")
    
    full_report = '\n'.join(report)
    print("\n" + full_report)
    
    # Save
    filename = f"Exports/digest_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    with open(filename, 'w') as f:
        f.write(full_report)
    
    print(f"\n✅ Saved: {filename}")
    return {'reddit': len(all_reddit), 'twitter': len(twitter_leads)}

if __name__ == '__main__':
    try:
        generate_digest()
        print("\n✅ DIGEST COMPLETE!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
