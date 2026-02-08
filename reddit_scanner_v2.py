#!/usr/bin/env python3
"""
Reddit Business Lead Scanner v2 - STRICT ENGAGEMENT FILTERING
Only returns posts with REAL engagement
"""
from reddit_json_client import RedditJSONClient
from reddit_engagement_filter import filter_by_engagement
from business_lead_detector import BusinessLeadDetector
from datetime import datetime

def scan_reddit_business_leads():
    """Scan Reddit for business leads - STRICT engagement filter"""
    
    print("=" * 70)
    print("REDDIT BUSINESS LEAD SCANNER - STRICT ENGAGEMENT FILTER")
    print(f"{datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}")
    print("=" * 70)
    print()
    
    client = RedditJSONClient()
    detector = BusinessLeadDetector()
    
    # Business subreddits
    subreddits = [
        'Entrepreneur', 'smallbusiness', 'startups', 'SaaS',
        'AgencyAutomation', 'AiForSmallBusiness', 'freelance',
        'productivity', 'digitalnomad', 'ecommerce',
        'marketing', 'business', 'smallbusinessowners'
    ]
    
    all_posts = []
    
    print("🔍 Scanning subreddits...")
    for subreddit in subreddits:
        print(f"  r/{subreddit}...", end=" ", flush=True)
        
        try:
            posts = client.fetch_posts(subreddit, limit=25, sort='hot')
            
            # STRICT ENGAGEMENT FILTER
            filtered = filter_by_engagement(
                posts,
                min_score=50,       # Minimum 50 upvotes
                min_comments=5,     # Minimum 5 comments
                min_engagement=100  # Minimum 100 engagement score
            )
            
            if filtered:
                print(f"✅ {len(filtered)}")
                all_posts.extend(filtered)
            else:
                print("○ (no high-engagement posts)")
        
        except Exception as e:
            print(f"❌ {e}")
    
    print()
    print("=" * 70)
    print(f"FOUND {len(all_posts)} HIGH-ENGAGEMENT BUSINESS POSTS")
    print("=" * 70)
    
    if not all_posts:
        print("\n⚠️ No posts met strict engagement criteria")
        print("   Requirements: 50+ upvotes, 5+ comments, 100+ engagement")
        return []
    
    # Detect business keywords
    scored_posts = []
    for post in all_posts:
        keyword_count, keywords = detector.score_post(post)
        if keyword_count >= 2:  # Minimum 2 business keywords
            post['keyword_count'] = keyword_count
            post['matched_keywords'] = keywords
            scored_posts.append(post)
    
    # Sort by engagement + keywords
    scored_posts.sort(
        key=lambda x: x['engagement_score'] + (x['keyword_count'] * 10),
        reverse=True
    )
    
    print(f"\n🎯 {len(scored_posts)} posts with business keywords")
    print("\n" + "=" * 70)
    print("TOP 10 HIGH-ENGAGEMENT BUSINESS LEADS")
    print("=" * 70)
    
    for i, post in enumerate(scored_posts[:10], 1):
        print(f"\n{i}. {post['title'][:60]}...")
        print(f"   📍 r/{post['subreddit']}")
        print(f"   📊 Engagement: {post['engagement_score']} (↑{post['score']} + 💬{post['num_comments']})")
        print(f"   🔑 Keywords: {', '.join(post['matched_keywords'][:3])}")
        print(f"   🔗 {post['url']}")
    
    print("\n" + "=" * 70)
    print("✅ Only posts with REAL engagement included!")
    print("=" * 70)
    
    return scored_posts

if __name__ == '__main__':
    leads = scan_reddit_business_leads()
    print(f"\nTotal leads found: {len(leads)}")
