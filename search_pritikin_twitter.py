#!/usr/bin/env python3
"""
Search Twitter for Pritikin Diet discussions
"""
import requests

# Load bearer token
with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
    for line in f:
        if line.startswith('BEARER_TOKEN='):
            bearer_token = line.split('=', 1)[1].strip()
            break

base_url = "https://api.twitter.com/2"
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "User-Agent": "BishopDailyDossier/1.0"
}

print("=" * 70)
print("SEARCHING TWITTER FOR PRITIKIN DIET")
print("=" * 70)
print()

# Search query
query = "pritikin diet OR pritikin program lang:en -is:retweet"

endpoint = f"{base_url}/tweets/search/recent"
params = {
    "query": query,
    "max_results": 100,
    "tweet.fields": "created_at,public_metrics,author_id",
    "expansions": "author_id",
    "user.fields": "username,name"
}

try:
    response = requests.get(endpoint, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    if 'data' not in data or not data['data']:
        print("⚠️ No tweets found about Pritikin Diet")
        print("\nThis could mean:")
        print("1. Free tier API doesn't include search (needs Basic tier $100/mo)")
        print("2. Very few people tweeting about it")
        print("\nManual search: https://twitter.com/search?q=pritikin%20diet")
    else:
        tweets = data['data']
        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
        
        print(f"✅ Found {len(tweets)} tweets about Pritikin Diet\n")
        print("=" * 70)
        
        for i, tweet in enumerate(tweets[:10], 1):
            author_id = tweet.get('author_id')
            user = users.get(author_id, {})
            username = user.get('username', 'unknown')
            
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            
            print(f"\n{i}. @{username}")
            print(f"   ❤️ {likes} likes")
            print(f"   💬 \"{tweet.get('text', '')[:150]}...\"")
            print(f"   🔗 https://twitter.com/{username}/status/{tweet.get('id')}")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("⚠️ Twitter search requires paid tier ($100/month Basic)")
        print("   Free tier can only:")
        print("   - Monitor specific accounts")
        print("   - Post tweets")
        print("   - Get user timelines")
        print("\nManual search: https://twitter.com/search?q=pritikin%20diet")
    else:
        print(f"❌ Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
