#!/usr/bin/env python3
"""
Parse engagement data from scan results and add to database
"""

import json
import re

# Read current database
with open('Database/complete_2026-02-07.json', 'r') as f:
    data = json.load(f)

# Create URL to engagement map
engagement_map = {}

# Parse Reddit engagement from /tmp/reddit.txt
print("📊 Parsing Reddit engagement...")
try:
    with open('/tmp/reddit.txt', 'r') as f:
        reddit_text = f.read()
    
    # Parse each entry
    entries = reddit_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'🔗 (https://www\.reddit\.com[^\s]+)', entry)
        engagement_match = re.search(r'📊 Engagement: (\d+) \(↑(\d+) upvotes \+ 💬(\d+) comments\)', entry)
        
        if url_match and engagement_match:
            url = url_match.group(1)
            total = int(engagement_match.group(1))
            upvotes = int(engagement_match.group(2))
            comments = int(engagement_match.group(3))
            engagement_map[url] = {'upvotes': upvotes, 'comments': comments, 'engagement': total}
    
    print(f"  Found engagement for {len(engagement_map)} Reddit posts")
except Exception as e:
    print(f"  ⚠️  Could not parse Reddit engagement: {e}")

# Parse Moltbook scores
print("📊 Parsing Moltbook scores...")
try:
    with open('/tmp/moltbook.txt', 'r') as f:
        moltbook_text = f.read()
    
    entries = moltbook_text.split('\n\n')
    for entry in entries:
        url_match = re.search(r'(https://moltbook\.com/post/[^\s]+)', entry)
        score_match = re.search(r'Score: (\d+)', entry)
        
        if url_match and score_match:
            url = url_match.group(1)
            score = int(score_match.group(1))
            engagement_map[url] = {'score': score}
    
    print(f"  Found scores for {len([k for k in engagement_map if 'moltbook' in k])} Moltbook posts")
except Exception as e:
    print(f"  ⚠️  Could not parse Moltbook scores: {e}")

# Update database items with engagement data
print("\n💾 Adding engagement data to database...")
updated_count = 0
for item in data['items']:
    url = item.get('url', '')
    if url in engagement_map:
        item.update(engagement_map[url])
        updated_count += 1

print(f"✅ Added engagement data to {updated_count} items")

# Save updated database
with open('Database/complete_2026-02-07.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Saved: Database/complete_2026-02-07.json")
