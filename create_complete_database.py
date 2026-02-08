#!/usr/bin/env python3
"""
Create complete JSON database with ALL found items
"""

import json
import subprocess
from datetime import datetime

# Run all scanners with NO limits
print("🔍 Running ALL scanners with NO limits...")

# Reddit
reddit_result = subprocess.run(
    ['python3', 'reddit_json_client.py'],
    capture_output=True, text=True, timeout=60
)

# Twitter  
twitter_result = subprocess.run(
    ['python3', 'twitter_builders_monitor.py'],
    capture_output=True, text=True, timeout=60
)

# YouTube
youtube_result = subprocess.run(
    ['python3', 'youtube_ai_monitor.py'],
    capture_output=True, text=True, timeout=60
)

# Moltbook
moltbook_result = subprocess.run(
    ['python3', 'moltbook_scanner.py'],
    capture_output=True, text=True, timeout=60
)

# Health
health_result = subprocess.run(
    ['python3', 'health_tracker.py'],
    capture_output=True, text=True, timeout=60
)

# RSS
rss_result = subprocess.run(
    ['python3', 'rss_news_scanner.py'],
    capture_output=True, text=True, timeout=60
)

print("✅ All scanners complete")

# Parse outputs and count
reddit_items = reddit_result.stdout.count('\n   🔗 https://www.reddit.com')
twitter_items = twitter_result.stdout.count('\n   🔗 https://twitter.com')
youtube_items = youtube_result.stdout.count('- https://www.youtube.com')
moltbook_items = moltbook_result.stdout.count('- https://moltbook.com/post/')
health_items = health_result.stdout.count('- https://www.reddit.com') + health_result.stdout.count('- https://twitter.com')
rss_items = rss_result.stdout.count('- Link: https://')

total = reddit_items + twitter_items + youtube_items + moltbook_items + health_items + rss_items

print(f"\n📊 ACTUAL COUNTS:")
print(f"Reddit: {reddit_items}")
print(f"Twitter: {twitter_items}")
print(f"YouTube: {youtube_items}")
print(f"Moltbook: {moltbook_items}")
print(f"Health: {health_items}")
print(f"RSS: {rss_items}")
print(f"TOTAL: {total}")

# Create database
database = {
    'date': datetime.now().isoformat(),
    'total_count': total,
    'platforms': {
        'reddit': {
            'count': reddit_items,
            'output': reddit_result.stdout
        },
        'twitter': {
            'count': twitter_items,
            'output': twitter_result.stdout
        },
        'youtube': {
            'count': youtube_items,
            'output': youtube_result.stdout
        },
        'moltbook': {
            'count': moltbook_items,
            'output': moltbook_result.stdout
        },
        'health': {
            'count': health_items,
            'output': health_result.stdout
        },
        'rss': {
            'count': rss_items,
            'output': rss_result.stdout
        }
    }
}

# Save to JSON
date_str = datetime.now().strftime('%Y-%m-%d')
json_file = f'Database/digest_{date_str}.json'

import os
os.makedirs('Database', exist_ok=True)

with open(json_file, 'w') as f:
    json.dump(database, f, indent=2)

print(f"\n✅ Database saved: {json_file}")

# Create human-readable HTML
html_file = f'Database/digest_{date_str}.html'

html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Complete Digest Database - {date_str}</title>
    <style>
        body {{ font-family: monospace; background: #1d1d1f; color: #f5f5f7; padding: 20px; }}
        h1 {{ color: #0a84ff; }}
        h2 {{ color: #0a84ff; margin-top: 40px; }}
        pre {{ background: #2d2d2f; padding: 20px; border-radius: 8px; overflow-x: auto; }}
        .count {{ color: #30d158; font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Complete Digest Database</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}</p>
    <p class="count">Total Items: {total}</p>
    
    <h2>Reddit ({reddit_items} items)</h2>
    <pre>{reddit_result.stdout}</pre>
    
    <h2>Twitter ({twitter_items} items)</h2>
    <pre>{twitter_result.stdout}</pre>
    
    <h2>YouTube ({youtube_items} items)</h2>
    <pre>{youtube_result.stdout}</pre>
    
    <h2>Moltbook ({moltbook_items} items)</h2>
    <pre>{moltbook_result.stdout}</pre>
    
    <h2>Health ({health_items} items)</h2>
    <pre>{health_result.stdout}</pre>
    
    <h2>RSS News ({rss_items} items)</h2>
    <pre>{rss_result.stdout}</pre>
</body>
</html>"""

with open(html_file, 'w') as f:
    f.write(html)

print(f"✅ HTML saved: {html_file}")

# Update main dossier with CORRECT count
print(f"\n🔄 Updating main dossier with correct count: {total}")
