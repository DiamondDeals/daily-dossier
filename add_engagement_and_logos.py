#!/usr/bin/env python3
"""
Add engagement metrics (upvotes/comments) and platform logo fallbacks
"""

import json
import shutil

# Read the complete database
with open('Database/complete_2026-02-07.json', 'r') as f:
    data = json.load(f)

# Platform logos (using simple emoji/unicode for now, can be replaced with actual logo URLs)
platform_logos = {
    'reddit': 'https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png',
    'twitter': 'https://abs.twimg.com/icons/apple-touch-icon-192x192.png',
    'youtube': 'https://www.youtube.com/s/desktop/2a9f7e4d/img/favicon_144x144.png',
    'moltbook': 'https://moltbook.com/favicon.ico',
    'health': 'https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png',  # Most health is Reddit
    'rss': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Feed-icon.svg'
}

print("🎨 Generating HTML with engagement metrics and logo fallbacks...")

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
        .item-preview.logo-fallback {{
            background: #1d1d1f;
        }}
        .item-preview.logo-fallback img {{
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
        <p class="stats">✅ {data['total']} Items with Engagement & Previews</p>
        <p style="color: #a1a1a6;">Generated: {data['date'][:10]}</p>
"""

# SVG icons for upvotes and comments
upvote_icon = '<svg viewBox="0 0 24 24"><path d="M12 4l-8 8h5v8h6v-8h5z"/></svg>'
comment_icon = '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>'

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
        platform_logo = platform_logos.get(platform_key, platform_logos['reddit'])
        
        # Get metadata
        meta = []
        if 'subreddit' in item:
            meta.append(f"r/{item['subreddit']}")
        if 'channel' in item:
            meta.append(item['channel'])
        if 'source' in item:
            meta.append(item['source'])
        
        meta_str = ' • '.join(meta) if meta else ''
        
        # Get engagement metrics
        upvotes = item.get('upvotes', item.get('score', 0))
        comments = item.get('comments', item.get('comment_count', 0))
        
        html += f'''<div class="item">
            <div class="item-content">
                <span class="platform {platform_class}">{platform_info["name"]}</span>
                <div class="item-title">{title}</div>'''
        
        if meta_str:
            html += f'<div class="item-meta">{meta_str}</div>'
        
        # Add engagement metrics if available
        if upvotes or comments:
            html += '<div class="item-engagement">'
            if upvotes:
                html += f'<div class="engagement-item">{upvote_icon}<span>{upvotes} upvotes</span></div>'
            if comments:
                html += f'<div class="engagement-item">{comment_icon}<span>{comments} comments</span></div>'
            html += '</div>'
        
        html += f'<a class="item-url" href="{url}" target="_blank">{url}</a></div>'
        
        # Add preview image or logo fallback
        html += f'''<div class="item-preview logo-fallback">
            <img src="{platform_logo}" alt="{platform_info["name"]} logo" loading="lazy" 
                 onerror="this.style.display='none'">
        </div>'''
        
        html += '</div>'

html += """
    </div>
</body>
</html>"""

with open('Database/all_items_latest.html', 'w') as f:
    f.write(html)

# Also update Daily folder
shutil.copy('Database/all_items_latest.html', 'Daily/2026-02-07-10PM/all_items.html')

print(f"✅ Generated all_items_latest.html with:")
print(f"   - Engagement metrics (upvotes/comments)")
print(f"   - Platform logo fallbacks")
print(f"✅ Updated Daily/2026-02-07-10PM/all_items.html")
