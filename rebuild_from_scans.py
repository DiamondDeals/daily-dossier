#!/usr/bin/env python3
"""
Rebuild complete database from /tmp scan results
"""

import json
import re
from datetime import datetime

all_items = []

def parse_title_from_url(url):
    if 'reddit.com' in url:
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            return slug.replace('_', ' ').replace('-', ' ').title()
    elif 'youtube.com' in url or 'youtu.be' in url:
        return "YouTube Video"
    elif 'twitter.com' in url or 'x.com' in url:
        return "Twitter Post"
    elif 'moltbook.com' in url:
        return "Moltbook Post"
    else:
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            return slug.replace('_', ' ').replace('-', ' ').title()
    return "Link"

# Parse Reddit
print("🟠 Parsing Reddit...")
try:
    with open('/tmp/reddit.txt', 'r') as f:
        reddit_text = f.read()
    
    entries = reddit_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'🔗 (https://www\.reddit\.com[^\s]+)', entry)
        subreddit_match = re.search(r'📍 r/(\w+)', entry)
        engagement_match = re.search(r'📊 Engagement: (\d+) \(↑(\d+) upvotes \+ 💬(\d+) comments\)', entry)
        
        if url_match:
            url = url_match.group(1)
            subreddit = subreddit_match.group(1) if subreddit_match else 'unknown'
            item = {
                'platform': 'reddit',
                'url': url,
                'subreddit': subreddit,
                'title': parse_title_from_url(url)
            }
            if engagement_match:
                item['upvotes'] = int(engagement_match.group(2))
                item['comments'] = int(engagement_match.group(3))
            all_items.append(item)
    
    print(f"  ✅ Found {len([i for i in all_items if i['platform']=='reddit'])} Reddit posts")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# Parse Twitter
print("🔵 Parsing Twitter...")
try:
    with open('/tmp/twitter.txt', 'r') as f:
        twitter_text = f.read()
    
    entries = twitter_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'https://(?:twitter\.com|x\.com)/[^\s]+', entry)
        if url_match:
            url = url_match.group(0)
            all_items.append({
                'platform': 'twitter',
                'url': url,
                'title': parse_title_from_url(url)
            })
    
    print(f"  ✅ Found {len([i for i in all_items if i['platform']=='twitter'])} Twitter posts")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# Parse YouTube
print("🎥 Parsing YouTube...")
try:
    with open('/tmp/youtube.txt', 'r') as f:
        youtube_text = f.read()
    
    entries = youtube_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'(https://www\.youtube\.com/watch\?v=[^\s]+)', entry)
        channel_match = re.search(r'Channel: ([^\n]+)', entry)
        if url_match:
            url = url_match.group(1)
            all_items.append({
                'platform': 'youtube',
                'url': url,
                'title': parse_title_from_url(url),
                'channel': channel_match.group(1) if channel_match else 'unknown'
            })
    
    print(f"  ✅ Found {len([i for i in all_items if i['platform']=='youtube'])} YouTube videos")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# Parse Moltbook
print("🤖 Parsing Moltbook...")
try:
    with open('/tmp/moltbook.txt', 'r') as f:
        moltbook_text = f.read()
    
    entries = moltbook_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'(https://moltbook\.com/post/[^\s]+)', entry)
        score_match = re.search(r'Score: (\d+)', entry)
        if url_match:
            url = url_match.group(1)
            item = {
                'platform': 'moltbook',
                'url': url,
                'title': parse_title_from_url(url)
            }
            if score_match:
                item['score'] = int(score_match.group(1))
            all_items.append(item)
    
    print(f"  ✅ Found {len([i for i in all_items if i['platform']=='moltbook'])} Moltbook posts")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# Parse Health
print("🟢 Parsing Health...")
try:
    with open('/tmp/health.txt', 'r') as f:
        health_text = f.read()
    
    entries = health_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'🔗 (https://www\.reddit\.com[^\s]+)', entry)
        source_match = re.search(r'Source: ([^\n]+)', entry)
        if url_match:
            url = url_match.group(1)
            all_items.append({
                'platform': 'health',
                'url': url,
                'title': parse_title_from_url(url),
                'source': source_match.group(1) if source_match else 'unknown'
            })
    
    print(f"  ✅ Found {len([i for i in all_items if i['platform']=='health'])} Health posts")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# Parse RSS
print("📰 Parsing RSS...")
try:
    with open('/tmp/rss.txt', 'r') as f:
        rss_text = f.read()
    
    entries = rss_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'Link: (https://[^\s]+)', entry)
        source_match = re.search(r'- ([^•]+)•', entry)
        if url_match:
            url = url_match.group(1)
            all_items.append({
                'platform': 'rss',
                'url': url,
                'title': parse_title_from_url(url),
                'source': source_match.group(1).strip() if source_match else 'unknown'
            })
    
    print(f"  ✅ Found {len([i for i in all_items if i['platform']=='rss'])} RSS items")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# Count platforms
platforms = {}
for item in all_items:
    platform = item['platform']
    platforms[platform] = platforms.get(platform, 0) + 1

print(f"\n✅ Total: {len(all_items)} items")
print(f"   Platforms: {platforms}")

# Save database
database = {
    'date': datetime.now().isoformat(),
    'total': len(all_items),
    'platforms': platforms,
    'items': all_items
}

with open('Database/complete_2026-02-07.json', 'w') as f:
    json.dump(database, f, indent=2)

print(f"\n💾 Saved: Database/complete_2026-02-07.json")
