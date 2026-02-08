#!/usr/bin/env python3
"""
Add screenshot previews using a screenshot API service
"""

import json
from urllib.parse import quote

# Read the complete database
with open('Database/complete_2026-02-07.json', 'r') as f:
    data = json.load(f)

# Add screenshot URLs using a free screenshot service
# Options:
# 1. https://image.thum.io/get/width/200/crop/150/{url}
# 2. https://api.screenshotmachine.com/?key=demo&url={url}&dimension=200x150
# 3. https://s0.wordpress.com/mshots/v1/{url}?w=200&h=150

for item in data['items']:
    url = item.get('url', '')
    if url:
        # Use WordPress mshots (free, no API key needed)
        encoded_url = quote(url, safe='')
        item['preview_image'] = f"https://s0.wordpress.com/mshots/v1/{url}?w=200&h=150"

# Save updated JSON
with open('Database/complete_2026-02-07.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Added screenshot URLs to all {len(data['items'])} items")

# Regenerate HTML with screenshot previews
print("\n🎨 Regenerating HTML with screenshot previews...")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Database - {data['total']} Items with Previews</title>
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
        .item-preview {{
            flex-shrink: 0;
            width: 200px;
            height: 150px;
            border-radius: 8px;
            overflow: hidden;
            background: #2d2d2f;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #424245;
        }}
        .item-preview img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .item-preview.loading {{
            color: #666;
            font-size: 13px;
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
        <p class="stats">✅ {data['total']} Items with Link Previews</p>
        <p style="color: #a1a1a6;">Generated: {data['date'][:10]} • Screenshots loading...</p>
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
        preview_image = item.get('preview_image')
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
            <div class="item-content">
                <span class="platform {platform_class}">{platform_info["name"]}</span>
                <div class="item-title">{title}</div>'''
        
        if meta_str:
            html += f'<div class="item-meta">{meta_str}</div>'
        
        html += f'<a class="item-url" href="{url}" target="_blank">{url}</a></div>'
        
        # Add preview image
        if preview_image:
            html += f'''<div class="item-preview">
                <img src="{preview_image}" alt="Preview" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'loading\\'>Preview unavailable</div>'">
            </div>'''
        else:
            html += '''<div class="item-preview loading">
                No preview
            </div>'''
        
        html += '</div>'

html += """
    </div>
</body>
</html>"""

with open('Database/all_items_latest.html', 'w') as f:
    f.write(html)

# Also update Daily folder
import shutil
shutil.copy('Database/all_items_latest.html', 'Daily/2026-02-07-10PM/all_items.html')

print(f"✅ Generated all_items_latest.html with screenshot previews")
print(f"✅ Updated Daily/2026-02-07-10PM/all_items.html")
print(f"\n🌐 Using WordPress mshots service for screenshots")
print(f"   Note: Screenshots may take a few seconds to load on first view")
