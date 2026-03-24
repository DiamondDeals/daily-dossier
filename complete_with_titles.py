#!/usr/bin/env python3
"""
Complete scan with titles/summaries
"""

import sys
import subprocess
import json
import re
from datetime import datetime
import os

# Fix emoji output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

all_items = []

# Run Reddit scanner and capture output
print("🟠 Scanning Reddit...")
result = subprocess.run(['python3', 'reddit_json_client.py'], 
                       capture_output=True, encoding='utf-8', errors='replace', timeout=60)

lines = result.stdout.split('\n')
for i, line in enumerate(lines):
    if re.match(r'^\d+\.', line.strip()):
        title = re.sub(r'^\d+\.\s*', '', line.strip()).replace('...', '')
        url = subreddit = score = ""
        
        for j in range(1, 6):
            if i+j < len(lines):
                if '🔗 https://www.reddit.com' in lines[i+j]:
                    url = lines[i+j].split('🔗 ')[1].strip()
                if '📍 r/' in lines[i+j]:
                    m = re.search(r'r/(\w+)', lines[i+j])
                    subreddit = m.group(1) if m else ""
                if '📊 Engagement:' in lines[i+j]:
                    score = lines[i+j].split('📊 ')[1].strip()
        
        if url:
            all_items.append({
                'platform': 'Reddit',
                'title': title,
                'summary': f"r/{subreddit} • {score}",
                'url': url
            })

print(f"  Found {len([i for i in all_items if i['platform']=='Reddit'])} Reddit items")

# Run Moltbook scanner
print("🤖 Scanning Moltbook...")
result = subprocess.run(['python3', 'moltbook_scanner.py'], 
                       capture_output=True, encoding='utf-8', errors='replace', timeout=60)

lines = result.stdout.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('**') and re.match(r'\*\*\d+\.', line.strip()):
        title = line.strip().replace('**', '')
        title = re.sub(r'^\d+\.\s*', '', title)
        url = score = ""
        
        for j in range(1, 6):
            if i+j < len(lines):
                if 'https://moltbook.com/post/' in lines[i+j]:
                    url = lines[i+j].strip().replace('- ', '')
                if 'Score:' in lines[i+j]:
                    m = re.search(r'Score: (\d+)', lines[i+j])
                    score = m.group(1) if m else ""
        
        if url:
            all_items.append({
                'platform': 'Moltbook',
                'title': title,
                'summary': f"Score: {score}",
                'url': url
            })

print(f"  Found {len([i for i in all_items if i['platform']=='Moltbook'])} Moltbook items")

# Run YouTube scanner
print("🎥 Scanning YouTube...")
result = subprocess.run(['python3', 'youtube_ai_monitor.py'], 
                       capture_output=True, encoding='utf-8', errors='replace', timeout=60)

lines = result.stdout.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('**') and re.match(r'\*\*\d+\.', line.strip()):
        title = line.strip().replace('**', '')
        title = re.sub(r'^\d+\.\s*', '', title)
        url = channel = ""
        
        for j in range(1, 4):
            if i+j < len(lines):
                if 'https://www.youtube.com' in lines[i+j]:
                    url = lines[i+j].strip().replace('- ', '')
                if 'Channel:' in lines[i+j]:
                    channel = lines[i+j].split('Channel: ')[1].strip()
        
        if url:
            all_items.append({
                'platform': 'YouTube',
                'title': title,
                'summary': f"Channel: {channel}",
                'url': url
            })

print(f"  Found {len([i for i in all_items if i['platform']=='YouTube'])} YouTube items")

# Run RSS scanner
print("📰 Scanning RSS...")
result = subprocess.run(['python3', 'rss_news_scanner.py'], 
                       capture_output=True, encoding='utf-8', errors='replace', timeout=60)

lines = result.stdout.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('**') and re.match(r'\*\*\d+\.', line.strip()):
        title = line.strip().replace('**', '')
        title = re.sub(r'^\d+\.\s*', '', title)
        url = source = ""
        
        for j in range(1, 4):
            if i+j < len(lines):
                if 'Link: https://' in lines[i+j]:
                    url = lines[i+j].split('Link: ')[1].strip()
                elif '- https://' in lines[i+j]:
                    url = lines[i+j].split('- ')[1].strip()
                if '- ' in lines[i+j] and '•' in lines[i+j]:
                    source = lines[i+j].split('- ')[1].split('•')[0].strip()
        
        if url:
            all_items.append({
                'platform': 'RSS',
                'title': title,
                'summary': source,
                'url': url
            })

print(f"  Found {len([i for i in all_items if i['platform']=='RSS'])} RSS items")

print(f"\n✅ Total: {len(all_items)} items with titles/summaries")

# Save database
database = {
    'date': datetime.now().isoformat(),
    'total': len(all_items),
    'items': all_items
}

os.makedirs('Database', exist_ok=True)
with open('Database/complete_with_titles.json', 'w') as f:
    json.dump(database, f, indent=2)

print(f"✅ Saved: Database/complete_with_titles.json")

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Database with Summaries - {len(all_items)} Items</title>
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
        .item-summary {{
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
        .Reddit {{ background: #FF4500; }}
        .Moltbook {{ background: #9B59B6; }}
        .YouTube {{ background: #FF0000; }}
        .RSS {{ background: #FFA500; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Complete Database</h1>
        <p class="stats">✅ {len(all_items)} Items with Titles & Summaries</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}</p>
"""

# Group by platform
platforms = {}
for item in all_items:
    plat = item['platform']
    if plat not in platforms:
        platforms[plat] = []
    platforms[plat].append(item)

for platform in ['Reddit', 'Moltbook', 'YouTube', 'RSS']:
    if platform in platforms:
        items = platforms[platform]
        html += f'<h2>{platform} ({len(items)} items)</h2>'
        for item in items:
            html += f'''<div class="item">
                <span class="platform {platform}">{platform}</span>
                <div class="item-title">{item['title']}</div>
                <div class="item-summary">{item.get('summary', '')}</div>
                <a class="item-url" href="{item['url']}" target="_blank">{item['url']}</a>
            </div>'''

html += """
    </div>
</body>
</html>"""

with open('Database/complete_with_titles.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Saved: Database/complete_with_titles.html")
