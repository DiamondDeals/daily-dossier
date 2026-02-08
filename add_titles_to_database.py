#!/usr/bin/env python3
"""
Parse titles from URLs and add to complete database
"""

import re
import json

def parse_title_from_url(url):
    """Extract title from URL slug"""
    
    # Reddit URLs: extract the slug before the last /
    if 'reddit.com' in url:
        # Example: /r/nutrition/comments/1qxg185/i_can_barely_taste_so_how_could_i_make_a/
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            # Replace underscores and dashes with spaces, capitalize
            title = slug.replace('_', ' ').replace('-', ' ')
            return title.title()
    
    # YouTube URLs: extract video title from v= parameter or path
    elif 'youtube.com' in url or 'youtu.be' in url:
        # We'll need to fetch these - for now use a placeholder
        return "YouTube Video"
    
    # Twitter URLs: extract tweet ID (can't get title without API)
    elif 'twitter.com' in url or 'x.com' in url:
        return "Twitter Post"
    
    # Moltbook URLs: extract post slug
    elif 'moltbook.com' in url:
        match = re.search(r'/post/([^/]+)', url)
        if match:
            slug = match.group(1)
            # It's a hash, not useful - return placeholder
            return "Moltbook Post"
    
    # Generic: extract last path segment
    else:
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            title = slug.replace('_', ' ').replace('-', ' ')
            return title.title()
    
    return "Link"

# Read the complete database JSON
with open('Database/complete_2026-02-07.json', 'r') as f:
    data = json.load(f)

# Add titles to each item
print("🔍 Parsing titles from URLs...")
for item in data['items']:
    url = item.get('url', '')
    if url and 'title' not in item:
        item['title'] = parse_title_from_url(url)

# Save updated JSON
with open('Database/complete_2026-02-07.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Added titles to {len(data['items'])} items")

# Regenerate the HTML with titles
print("\n🎨 Regenerating HTML with titles...")

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
            margin-bottom: 10px;
        }}
        .item-url {{
            color: #0a84ff;
            text-decoration: none;
            word-break: break-all;
            font-size: 13px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Complete Database</h1>
        <p class="stats">✅ {data['total']} Items</p>
        <p style="color: #a1a1a6;">Generated: {data['date'][:10]}</p>
"""

# Group by platform
platforms_map = {
    'reddit': {'name': 'Reddit', 'color': 'reddit'},
    'twitter': {'name': 'Twitter', 'color': 'twitter'},
    'youtube': {'name': 'YouTube', 'color': 'youtube'},
    'moltbook': {'name': 'Moltbook', 'color': 'moltbook'},
    'health': {'name': 'Health', 'color': 'health'},
    'rss': {'name': 'RSS', 'color': 'rss'}
}

grouped = {}
for item in data['items']:
    platform = item.get('platform', 'unknown')
    if platform not in grouped:
        grouped[platform] = []
    grouped[platform].append(item)

for platform_key, items in grouped.items():
    platform_info = platforms_map.get(platform_key, {'name': platform_key.title(), 'color': 'reddit'})
    html += f'<h2>{platform_info["name"]} ({len(items)} items)</h2>'
    
    for item in items:
        title = item.get('title', 'Untitled')
        url = item.get('url', '')
        platform_class = platform_info['color']
        
        # Get metadata
        meta = []
        if 'subreddit' in item:
            meta.append(f"r/{item['subreddit']}")
        if 'channel' in item:
            meta.append(item['channel'])
        if 'source' in item:
            meta.append(item['source'])
        
        meta_str = ' • '.join(meta) if meta else ''
        
        html += f'''<div class="item">
            <span class="platform {platform_class}">{platform_info["name"]}</span>
            <div class="item-title">{title}</div>'''
        
        if meta_str:
            html += f'<div class="item-meta">{meta_str}</div>'
        
        html += f'''<a class="item-url" href="{url}" target="_blank">{url}</a>
        </div>'''

html += """
    </div>
</body>
</html>"""

with open('Database/all_items_2026-02-07.html', 'w') as f:
    f.write(html)

# Also update the latest copy
with open('Database/all_items_latest.html', 'w') as f:
    f.write(html)

# Update Daily folder
import shutil
shutil.copy('Database/all_items_2026-02-07.html', 'Daily/2026-02-07-10PM/all_items.html')

print(f"✅ Regenerated all_items_2026-02-07.html with titles")
print(f"✅ Updated all_items_latest.html")
print(f"✅ Updated Daily/2026-02-07-10PM/all_items.html")
