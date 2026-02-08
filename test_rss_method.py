#!/usr/bin/env python3
"""
Test Reddit RSS feed method - NO authentication needed!
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

print("=" * 60)
print("REDDIT RSS FEED TEST - NO API CREDENTIALS NEEDED!")
print("=" * 60)

# Test with r/entrepreneur RSS feed
rss_url = "https://www.reddit.com/r/entrepreneur/new/.rss"

print(f"\n🔍 Fetching: {rss_url}")
print()

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(rss_url, headers=headers, timeout=10)
    response.raise_for_status()
    
    print(f"✅ Successfully fetched RSS feed!")
    print(f"Status code: {response.status_code}")
    print()
    
    # Parse XML
    root = ET.fromstring(response.content)
    
    # Find all entries (posts)
    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    
    print(f"📝 Found {len(entries)} posts in r/entrepreneur")
    print("=" * 60)
    
    # Display first 5 posts
    for i, entry in enumerate(entries[:5], 1):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        author = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name').text
        link = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        
        # Get content/description
        content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
        content = content_elem.text[:200] if content_elem is not None else "No content"
        
        print(f"\n{i}. {title}")
        print(f"   Author: u/{author}")
        print(f"   Posted: {published}")
        print(f"   Link: {link}")
        print(f"   Preview: {content}...")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ RSS METHOD WORKS - NO AUTHENTICATION NEEDED!")
    print("=" * 60)
    print("\nThis method can scrape:")
    print("✅ Any subreddit: reddit.com/r/SUBREDDIT/.rss")
    print("✅ Search results: reddit.com/search.rss?q=query")
    print("✅ User posts: reddit.com/user/USERNAME/.rss")
    print("✅ All without API credentials!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Type: {type(e).__name__}")
