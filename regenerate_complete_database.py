#!/usr/bin/env python3
"""
Regenerate complete database with ALL platforms, titles, engagement, and logo fallbacks
"""

import json
import re
import shutil

def parse_title_from_url(url):
    """Extract title from URL slug"""
    if 'reddit.com' in url:
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            title = slug.replace('_', ' ').replace('-', ' ')
            return title.title()
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
            title = slug.replace('_', ' ').replace('-', ' ')
            return title.title()
    return "Link"

# Load the restored complete database
print("📂 Loading complete database with all 704 items...")
with open('Database/complete_2026-02-07_backup.json', 'r') as f:
    data = json.load(f)

print(f"✅ Loaded {data['total']} items")
print(f"   Platforms: {data.get('platforms', {})}")

# Add titles to all items
print("\n🏷️  Adding titles...")
for item in data['items']:
    url = item.get('url', '')
    if url and 'title' not in item:
        item['title'] = parse_title_from_url(url)

print(f"✅ Added titles to all items")

# Parse engagement data from scan results
print("\n📊 Adding engagement data...")
engagement_map = {}

# Reddit engagement
try:
    with open('/tmp/reddit.txt', 'r') as f:
        reddit_text = f.read()
    entries = reddit_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'🔗 (https://www\.reddit\.com[^\s]+)', entry)
        engagement_match = re.search(r'📊 Engagement: (\d+) \(↑(\d+) upvotes \+ 💬(\d+) comments\)', entry)
        if url_match and engagement_match:
            url = url_match.group(1)
            engagement_map[url] = {
                'upvotes': int(engagement_match.group(2)),
                'comments': int(engagement_match.group(3))
            }
    print(f"  ✅ Found engagement for {len(engagement_map)} Reddit posts")
except Exception as e:
    print(f"  ⚠️  Reddit engagement: {e}")

# Moltbook scores
try:
    with open('/tmp/moltbook.txt', 'r') as f:
        moltbook_text = f.read()
    entries = moltbook_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'(https://moltbook\.com/post/[^\s]+)', entry)
        score_match = re.search(r'Score: (\d+)', entry)
        if url_match and score_match:
            url = url_match.group(1)
            engagement_map[url] = {'score': int(score_match.group(1))}
    print(f"  ✅ Found scores for Moltbook posts")
except Exception as e:
    print(f"  ⚠️  Moltbook scores: {e}")

# Apply engagement data
updated = 0
for item in data['items']:
    url = item.get('url', '')
    if url in engagement_map:
        item.update(engagement_map[url])
        updated += 1

print(f"✅ Added engagement to {updated} items")

# Save updated database
with open('Database/complete_2026-02-07.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n💾 Saved: Database/complete_2026-02-07.json")

# Now regenerate HTML with all platforms
print("\n🎨 Generating HTML with all platforms...")

platform_logos = {
    'reddit': 'https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png',
    'twitter': 'https://abs.twimg.com/icons/apple-touch-icon-192x192.png',
    'youtube': 'https://www.youtube.com/s/desktop/2a9f7e4d/img/favicon_144x144.png',
    'moltbook': 'https://moltbook.com/favicon.ico',
    'health': 'https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png',
    'rss': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Feed-icon.svg'
}

platforms_map = {
    'reddit': {'name': 'Reddit', 'color': 'reddit'},
    'twitter': {'name': 'Twitter', 'color': 'twitter'},
    'youtube': {'name': 'YouTube', 'color': 'youtube'},
    'moltbook': {'name': 'Moltbook', 'color': 'moltbook'},
    'health': {'name': 'Health', 'color': 'health'},
    'rss': {'name': 'RSS', 'color': 'rss'}
}

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Database - {data['total']} Items</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1d1d1f;
            color: #f5f5f7;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #2d2d2f;
            border-radius: 12px;
            padding: 40px;
        }}
        h1 {{
            color: #0a84ff;
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .stats {{
            font-size: 24px;
            color: #30d158;
            margin: 20px 0;
        }}
        h2 {{
            color: #0a84ff;
            font-size: 32px;
            margin-top: 40px;
            border-left: 4px solid #0a84ff;
            padding-left: 20px;
        }}
        .item {{
            background: #1d1d1f;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 3px solid #0a84ff;
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }}
        .item-content {{
            flex: 1;
            min-width: 0;
        }}
        .item-engagement {{
            display: flex;
            gap: 15px;
            margin: 12px 0;
            font-size: 14px;
            color: #a1a1a6;
        }}
        .engagement-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .engagement-item svg {{
            width: 16px;
            height: 16px;
            fill: #a1a1a6;
        }}
        .item-preview {{
            flex-shrink: 0;
            width: 200px;
            height: 150px;
            border-radius: 8px;
            overflow: hidden;
            background: #1d1d1f;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #424245;
        }}
        .item-preview img {{
            width: 80px;
            height: 80px;
            object-fit: contain;
            opacity: 0.6;
        }}
        .item-title {{
            font-size: 20px;
            font-weight: 700;
            color: #0a84ff;
            margin-bottom: 8px;
        }}
        .item-meta {{
            color: #a1a1a6;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .item-url {{
            color: #0a84ff;
            text-decoration: none;
            word-break: break-all;
            font-size: 13px;
            display: block;
            margin-top: 8px;
        }}
        .item-url:hover {{
            text-decoration: underline;
        }}
        .platform {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .reddit {{ background: #FF4500; }}
        .twitter {{ background: #1DA1F2; }}
        .youtube {{ background: #FF0000; }}
        .moltbook {{ background: #9B59B6; }}
        .health {{ background: #30d158; }}
        .rss {{ background: #FFA500; }}
        
        @media (max-width: 768px) {{
            .item {{
                flex-direction: column;
            }}
            .item-preview {{
                width: 100%;
                height: 200px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Complete Database</h1>
        <p class="stats">✅ {data['total']} Items Across 6 Platforms</p>
        <p style="color: #a1a1a6;">Generated: {data['date'][:10]} • With Engagement & Logos</p>
"""

upvote_icon = '<svg viewBox="0 0 24 24"><path d="M12 4l-8 8h5v8h6v-8h5z"/></svg>'
comment_icon = '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>'

# Group by platform
grouped = {}
for item in data['items']:
    platform = item.get('platform', 'unknown')
    if platform not in grouped:
        grouped[platform] = []
    grouped[platform].append(item)

for platform_key in ['reddit', 'twitter', 'youtube', 'moltbook', 'health', 'rss']:
    if platform_key not in grouped:
        continue
    
    items = grouped[platform_key]
    platform_info = platforms_map[platform_key]
    platform_logo = platform_logos[platform_key]
    
    html += f'<h2>{platform_info["name"]} ({len(items)} items)</h2>'
    
    for item in items:
        title = item.get('title', 'Untitled')
        url = item.get('url', '')
        platform_class = platform_info['color']
        
        # Metadata
        meta = []
        if 'subreddit' in item:
            meta.append(f"r/{item['subreddit']}")
        if 'channel' in item:
            meta.append(item['channel'])
        if 'source' in item:
            meta.append(item['source'])
        meta_str = ' • '.join(meta) if meta else ''
        
        # Engagement
        upvotes = item.get('upvotes', 0)
        comments = item.get('comments', 0)
        score = item.get('score', 0)
        
        html += f'''<div class="item">
            <div class="item-content">
                <span class="platform {platform_class}">{platform_info["name"]}</span>
                <div class="item-title">{title}</div>'''
        
        if meta_str:
            html += f'<div class="item-meta">{meta_str}</div>'
        
        if upvotes or comments:
            html += '<div class="item-engagement">'
            if upvotes:
                html += f'<div class="engagement-item">{upvote_icon}<span>{upvotes} upvotes</span></div>'
            if comments:
                html += f'<div class="engagement-item">{comment_icon}<span>{comments} comments</span></div>'
            html += '</div>'
        elif score:
            html += f'<div class="item-engagement"><div class="engagement-item">Score: {score}</div></div>'
        
        html += f'<a class="item-url" href="{url}" target="_blank">{url}</a></div>'
        html += f'''<div class="item-preview">
            <img src="{platform_logo}" alt="{platform_info["name"]} logo" loading="lazy">
        </div></div>'''

html += """
    </div>
</body>
</html>"""

with open('Database/all_items_latest.html', 'w') as f:
    f.write(html)

# Update Daily folder
shutil.copy('Database/all_items_latest.html', 'Daily/2026-02-07-10PM/all_items.html')

print(f"✅ Generated HTML with ALL 6 platforms")
print(f"✅ Updated Daily/2026-02-07-10PM/all_items.html")
print(f"\n📋 Platform breakdown:")
for platform_key in ['reddit', 'twitter', 'youtube', 'moltbook', 'health', 'rss']:
    if platform_key in grouped:
        print(f"   {platform_key.title()}: {len(grouped[platform_key])} items")
