#!/usr/bin/env python3
"""
Track seen URLs and detect engagement jumps
"""
import json
from datetime import datetime, timedelta
import os

SEEN_FILE = 'Database/seen_urls_last_7_days.json'

def load_seen_urls():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_seen_urls(data):
    with open(SEEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clean_old_entries(seen_urls):
    """Remove entries older than 7 days"""
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    return {url: data for url, data in seen_urls.items() 
            if data.get('first_seen', '') > cutoff}

def check_for_hot_items(new_items, seen_urls):
    """Find items with 50%+ engagement jump"""
    hot_items = []
    
    for item in new_items:
        url = item.get('url', '')
        if url in seen_urls:
            old_engagement = seen_urls[url].get('last_engagement', 0)
            new_engagement = item.get('upvotes', 0) + item.get('comments', 0) + item.get('score', 0)
            
            if old_engagement > 0 and new_engagement >= old_engagement * 1.5:
                hot_items.append({
                    **item,
                    'old_engagement': old_engagement,
                    'new_engagement': new_engagement,
                    'jump': new_engagement - old_engagement
                })
    
    return hot_items

def mark_as_seen(items, seen_urls):
    """Mark items as seen and update engagement"""
    now = datetime.now().isoformat()
    
    for item in items:
        url = item.get('url', '')
        engagement = item.get('upvotes', 0) + item.get('comments', 0) + item.get('score', 0)
        
        if url not in seen_urls:
            seen_urls[url] = {
                'first_seen': now,
                'last_engagement': engagement,
                'shown_in_dossier': True
            }
        else:
            seen_urls[url]['last_engagement'] = engagement
            seen_urls[url]['last_updated'] = now
    
    return seen_urls

if __name__ == '__main__':
    print("✅ Duplicate detection system created")
