#!/usr/bin/env python3
"""
Re-scan with summaries/titles for each item
"""

import subprocess
import json
import re
from datetime import datetime
import os

def extract_reddit_items():
    """Get Reddit items with titles"""
    result = subprocess.run(['cat', '/tmp/reddit.txt'], capture_output=True, text=True)
    items = []
    
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith(tuple(f"{n}." for n in range(1, 100))):
            title = line.strip()
            title = re.sub(r'^\d+\.\s*', '', title)  # Remove number
            title = title.replace('...', '')
            
            # Get URL from next few lines
            url = ""
            subreddit = ""
            score = ""
            for j in range(1, 6):
                if i+j < len(lines):
                    if '🔗 https://www.reddit.com' in lines[i+j]:
                        url = lines[i+j].split('🔗 ')[1].strip()
                    if '📍 r/' in lines[i+j]:
                        subreddit = re.search(r'r/(\w+)', lines[i+j]).group(1) if re.search(r'r/(\w+)', lines[i+j]) else ""
                    if '📊 Engagement:' in lines[i+j]:
                        score = lines[i+j].split('📊 ')[1].strip() if '📊' in lines[i+j] else ""
            
            if url:
                items.append({
                    'platform': 'Reddit',
                    'title': title,
                    'url': url,
                    'subreddit': subreddit,
                    'score': score
                })
    
    return items

def extract_moltbook_items():
    """Get Moltbook items with titles"""
    result = subprocess.run(['cat', '/tmp/moltbook.txt'], capture_output=True, text=True)
    items = []
    
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('**') and '. ' in line:
            title = line.strip().replace('**', '')
            title = re.sub(r'^\d+\.\s*', '', title)
            
            # Get URL from next few lines
            url = ""
            author = ""
            score = ""
            for j in range(1, 6):
                if i+j < len(lines):
                    if 'https://moltbook.com/post/' in lines[i+j]:
                        url = lines[i+j].split('- ')[1].strip() if '- ' in lines[i+j] else lines[i+j].strip()
                    if '@' in lines[i+j] and 'Score:' in lines[i+j]:
                        score = lines[i+j].split('Score: ')[1].strip() if 'Score: ' in lines[i+j] else ""
            
            if url:
                items.append({
                    'platform': 'Moltbook',
                    'title': title,
                    'url': url,
                    'score': score
                })
    
    return items

def extract_youtube_items():
    """Get YouTube items with titles"""
    result = subprocess.run(['cat', '/tmp/youtube.txt'], capture_output=True, text=True)
    items = []
    
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('**') and '. ' in line:
            title = line.strip().replace('**', '')
            title = re.sub(r'^\d+\.\s*', '', title)
            
            # Get URL and channel
            url = ""
            channel = ""
            for j in range(1, 4):
                if i+j < len(lines):
                    if 'https://www.youtube.com' in lines[i+j]:
                        url = lines[i+j].split('- ')[1].strip() if '- ' in lines[i+j] else lines[i+j].strip()
                    if 'Channel:' in lines[i+j]:
                        channel = lines[i+j].split('Channel: ')[1].strip() if 'Channel: ' in lines[i+j] else ""
            
            if url:
                items.append({
                    'platform': 'YouTube',
                    'title': title,
                    'url': url,
                    'channel': channel
                })
    
    return items

def extract_rss_items():
    """Get RSS items with titles"""
    result = subprocess.run(['cat', '/tmp/rss.txt'], capture_output=True, text=True)
    items = []
    
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('**') and '. ' in line:
            title = line.strip().replace('**', '')
            title = re.sub(r'^\d+\.\s*', '', title)
            
            # Get URL and source
            url = ""
            source = ""
            for j in range(1, 4):
                if i+j < len(lines):
                    if 'https://' in lines[i+j] and '- Link:' in lines[i+j]:
                        url = lines[i+j].split('- Link: ')[1].strip() if '- Link: ' in lines[i+j] else ""
                    elif 'https://' in lines[i+j] and '- ' in lines[i+j]:
                        url = lines[i+j].split('- ')[1].strip()
                    if '- ' in lines[i+j] and '•' in lines[i+j]:
                        source = lines[i+j].split('- ')[1].split('•')[0].strip() if '- ' in lines[i+j] else ""
            
            if url:
                items.append({
                    'platform': 'RSS',
                    'title': title,
                    'url': url,
                    'source': source
                })
    
    return items

print("📝 Extracting titles and summaries...")

reddit_items = extract_reddit_items()
moltbook_items = extract_moltbook_items()
youtube_items = extract_youtube_items()
rss_items = extract_rss_items()

all_items = reddit_items + moltbook_items + youtube_items + rss_items

print(f"✅ Extracted {len(all_items)} items with titles")
print(f"  Reddit: {len(reddit_items)}")
print(f"  Moltbook: {len(moltbook_items)}")
print(f"  YouTube: {len(youtube_items)}")
print(f"  RSS: {len(rss_items)}")

# Save database
database = {
    'date': datetime.now().isoformat(),
    'total': len(all_items),
    'items': all_items
}

os.makedirs('Database', exist_ok=True)
with open('Database/with_summaries_2026-02-07.json', 'w') as f:
    json.dump(database, f, indent=2)

print(f"✅ Saved: Database/with_summaries_2026-02-07.json")
