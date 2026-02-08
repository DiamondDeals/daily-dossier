#!/usr/bin/env python3
"""
🔍 EXPLORATION MODE
Discover content OUTSIDE programmed channels/accounts
"""

import subprocess
import json
import random
from datetime import datetime

def explore_reddit_trending():
    """Explore r/all trending posts outside monitored subs"""
    print("🔍 Exploring Reddit r/all...")
    
    from reddit_json_client import RedditJSONClient
    client = RedditJSONClient()
    
    # Get trending from r/all
    trending = client.fetch_posts('all', limit=50)
    
    # Filter out already-monitored subreddits
    monitored_subs = ['entrepreneur', 'SaaS', 'startups', 'business', 'smallbusiness',
                      'Entrepreneur_ama', 'EntrepreneurRideAlong', 'sales', 'marketing', 'Flipping']
    
    discoveries = []
    for post in trending:
        subreddit = post.get('subreddit', '').lower()
        if subreddit not in [s.lower() for s in monitored_subs]:
            # Check if business/tech related
            title = post.get('title', '').lower()
            keywords = ['business', 'startup', 'saas', 'entrepreneur', 'marketing', 'sales', 
                       'product', 'launch', 'revenue', 'growth', 'ai', 'tech']
            
            if any(kw in title for kw in keywords):
                discoveries.append({
                    'platform': 'reddit',
                    'title': post.get('title', 'Untitled'),
                    'url': post.get('url', ''),
                    'subreddit': post.get('subreddit', ''),
                    'upvotes': post.get('ups', 0),
                    'comments': post.get('num_comments', 0),
                    'source': f"r/{post.get('subreddit', 'unknown')} (discovered)"
                })
    
    # Return top 5 by engagement
    discoveries.sort(key=lambda x: x['upvotes'] + x['comments'] * 2, reverse=True)
    print(f"  ✅ Found {len(discoveries[:5])} Reddit discoveries")
    return discoveries[:5]

def explore_twitter_trending():
    """Explore Twitter trending hashtags outside monitored accounts"""
    print("🔍 Exploring Twitter trending...")
    
    # Twitter trending requires API v2 which we don't have on free tier
    # For now, search specific hashtags that aren't in our monitoring
    
    explore_hashtags = ['#indiemaker', '#indiehacker', '#solopreneur', '#productlaunch', '#nocode']
    discoveries = []
    
    # Placeholder - would need Twitter API v2 for actual trending
    print(f"  ⏳ Twitter trending requires API v2 (not available on free tier)")
    return []

def explore_moltbook_trending():
    """Browse Moltbook trending posts outside subscribed submolts"""
    print("🔍 Exploring Moltbook trending...")
    
    try:
        # Use Moltbook API to get trending/recent posts
        result = subprocess.run(
            ['python3', '-c', '''
import sys
sys.path.append("/home/drew/.local/lib/python3.13/site-packages")
from moltbook import Moltbook
import json

mb = Moltbook()
# Get recent posts from explore/trending
posts = mb.get_trending_posts(limit=20)  # If this API exists
for post in posts:
    print(json.dumps(post))
'''],
            capture_output=True, text=True, timeout=10
        )
        
        print(f"  ⏳ Moltbook trending API not yet available")
        return []
    except:
        print(f"  ⏳ Moltbook exploration requires API expansion")
        return []

def explore_youtube_trending():
    """Explore YouTube trending outside monitored channels"""
    print("🔍 Exploring YouTube trending...")
    
    # Would need YouTube Data API trending endpoint
    print(f"  ⏳ YouTube trending requires API key")
    return []

def generate_exploration_section():
    """Generate exploration section for dossier"""
    
    print("\n🔍 EXPLORATION MODE - Discovering New Content")
    print("=" * 60)
    
    all_discoveries = []
    
    # Reddit exploration
    reddit_discoveries = explore_reddit_trending()
    all_discoveries.extend(reddit_discoveries)
    
    # Twitter exploration (placeholder)
    twitter_discoveries = explore_twitter_trending()
    all_discoveries.extend(twitter_discoveries)
    
    # Moltbook exploration (placeholder)
    moltbook_discoveries = explore_moltbook_trending()
    all_discoveries.extend(moltbook_discoveries)
    
    # YouTube exploration (placeholder)
    youtube_discoveries = explore_youtube_trending()
    all_discoveries.extend(youtube_discoveries)
    
    print(f"\n✅ Total discoveries: {len(all_discoveries)}")
    
    # Generate markdown
    md = "\n## 🔍 Exploration (New Discoveries)\n\n"
    md += "_Content found outside programmed channels — potential new sources!_\n\n"
    
    if all_discoveries:
        for i, item in enumerate(all_discoveries, 1):
            md += f"**{i}. {item.get('title', 'Untitled')}**\n"
            md += f"- Source: {item.get('source', 'Unknown')} ⭐ *New Discovery*\n"
            if 'upvotes' in item:
                md += f"- ↑{item['upvotes']} upvotes • 💬{item.get('comments', 0)} comments\n"
            md += f"- {item.get('url', '')}\n\n"
    else:
        md += "_No new discoveries this scan — check back next time!_\n\n"
    
    # Save discoveries
    discovery_data = {
        'date': datetime.now().isoformat(),
        'count': len(all_discoveries),
        'items': all_discoveries
    }
    
    with open('Database/exploration_discoveries.json', 'w') as f:
        json.dump(discovery_data, f, indent=2)
    
    print(f"✅ Saved: Database/exploration_discoveries.json")
    
    return md, all_discoveries

if __name__ == '__main__':
    md, discoveries = generate_exploration_section()
    print("\nMarkdown preview:")
    print(md)
