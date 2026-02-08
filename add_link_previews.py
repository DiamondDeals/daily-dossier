#!/usr/bin/env python3
"""
Add link preview thumbnails to complete database
Uses Open Graph images from URLs
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

def get_og_image(url, timeout=3):
    """Fetch Open Graph image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try og:image first
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']
            # Make absolute URL
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            return image_url
        
        # Try twitter:image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            image_url = twitter_image['content']
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            return image_url
        
        return None
    except Exception as e:
        print(f"  ⚠️  Could not fetch image for {url[:50]}...: {e}")
        return None

# Read the complete database
print("📸 Fetching link preview images...")
with open('Database/complete_2026-02-07.json', 'r') as f:
    data = json.load(f)

# Fetch images for a sample (first 50 items to test)
print(f"Testing with first 50 items out of {len(data['items'])}...")

for i, item in enumerate(data['items'][:50]):
    url = item.get('url', '')
    if url and 'preview_image' not in item:
        print(f"  [{i+1}/50] Fetching: {url[:60]}...")
        item['preview_image'] = get_og_image(url)
        time.sleep(0.5)  # Rate limiting

# Save updated JSON
with open('Database/complete_2026-02-07.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Added preview images to first 50 items")

# Regenerate HTML with preview images
print("\n🎨 Regenerating HTML with preview images...")

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
        }}
        .item-preview img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .item-preview.no-image {{
            color: #666;
            font-size: 14px;
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
        <p class="stats">✅ {data['total']} Items</p>
        <p style="color: #a1a1a6;">Generated: {data['date'][:10]} • With Link Previews</p>
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
                <img src="{preview_image}" alt="Preview" loading="lazy">
            </div>'''
        else:
            html += '''<div class="item-preview no-image">
                No preview
            </div>'''
        
        html += '</div>'

html += """
    </div>
</body>
</html>"""

with open('Database/all_items_latest.html', 'w') as f:
    f.write(html)

print(f"✅ Generated all_items_latest.html with preview images")
print(f"   First 50 items have preview images, rest show 'No preview'")
