#!/usr/bin/env python3
"""
Twitter Business Pain Point Detector
Searches Twitter for business problems and automation opportunities
"""
import requests
import json
from datetime import datetime, timedelta

class TwitterPainDetector:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "BishopDailyDossier/1.0"
        }
    
    def search_pain_points(self, query, max_results=100):
        """
        Search Twitter for business pain points
        """
        endpoint = f"{self.base_url}/tweets/search/recent"
        
        # Tweet fields to fetch
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,author_id,conversation_id",
            "expansions": "author_id",
            "user.fields": "username,name,verified"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse results
            tweets = []
            users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
            
            for tweet in data.get('data', []):
                parsed = self._parse_tweet(tweet, users)
                if parsed and not parsed['is_promotion']:
                    tweets.append(parsed)
            
            # Sort by engagement
            tweets.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            return tweets
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("❌ Rate limit hit - wait before next request")
            else:
                print(f"❌ HTTP Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error searching Twitter: {e}")
            return []
    
    def _parse_tweet(self, tweet, users):
        """Parse tweet data into structured format"""
        try:
            author_id = tweet.get('author_id')
            user = users.get(author_id, {})
            
            # Get public metrics
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)
            
            # Calculate engagement (replies are 3x valuable - indicate pain point discussion)
            engagement_score = likes + (retweets * 2) + (replies * 3)
            
            # Tweet text
            text = tweet.get('text', '')
            
            # Detect promotional content
            is_promotion = self._is_promotion(text, user)
            
            return {
                'text': text,
                'author': user.get('username', 'unknown'),
                'author_name': user.get('name', 'Unknown'),
                'verified': user.get('verified', False),
                'created_at': tweet.get('created_at', ''),
                'likes': likes,
                'retweets': retweets,
                'replies': replies,
                'engagement_score': engagement_score,
                'tweet_id': tweet.get('id'),
                'url': f"https://twitter.com/{user.get('username', 'i')}/status/{tweet.get('id')}",
                'is_promotion': is_promotion
            }
            
        except Exception as e:
            print(f"Error parsing tweet: {e}")
            return None
    
    def _is_promotion(self, text, user):
        """Detect if tweet is promotional (offering services)"""
        promo_keywords = [
            'dm me', 'reach out', 'contact me', 'book a call',
            'free consultation', 'my service', 'i offer',
            'check out my', 'follow me', 'subscribe',
            'buy now', 'limited time', 'special offer',
            'discount code', 'promo code'
        ]
        
        text_lower = text.lower()
        
        for keyword in promo_keywords:
            if keyword in text_lower:
                return True
        
        # Check for excessive hashtags (often promotional)
        if text.count('#') > 3:
            return True
        
        return False
    
    def build_query(self, keywords, exclude_keywords=None):
        """
        Build Twitter search query
        Combines keywords with OR, excludes certain terms
        """
        # Combine keywords
        query_parts = [f'"{kw}"' for kw in keywords[:10]]  # Max 10 for query length
        query = ' OR '.join(query_parts)
        
        # Exclude promotional terms
        if exclude_keywords:
            for exclude in exclude_keywords:
                query += f' -"{exclude}"'
        
        # English only, no retweets
        query += " lang:en -is:retweet"
        
        return query

if __name__ == '__main__':
    print("=" * 70)
    print("TWITTER BUSINESS PAIN POINT DETECTOR - TEST")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    detector = TwitterPainDetector(bearer_token)
    
    # Search for business automation pain points
    keywords = [
        "manual process",
        "repetitive task",
        "spending hours",
        "there must be a better way",
        "automate this"
    ]
    
    exclude = ["hiring", "looking for", "dm me", "my service"]
    
    query = detector.build_query(keywords, exclude)
    
    print(f"\n🔍 Search Query: {query[:100]}...")
    print("\n⏳ Searching Twitter...\n")
    
    tweets = detector.search_pain_points(query, max_results=50)
    
    print(f"✅ Found {len(tweets)} relevant tweets (promotions filtered)")
    print("\n" + "=" * 70)
    print("TOP 10 BUSINESS PAIN POINTS BY ENGAGEMENT")
    print("=" * 70)
    
    for i, tweet in enumerate(tweets[:10], 1):
        verified = "✓" if tweet['verified'] else ""
        print(f"\n{i}. @{tweet['author']} {verified}")
        print(f"   📊 Engagement: {tweet['engagement_score']} (❤️{tweet['likes']} 🔁{tweet['retweets']} 💬{tweet['replies']})")
        print(f"   💬 \"{tweet['text'][:120]}...\"")
        print(f"   🔗 {tweet['url']}")
    
    print("\n" + "=" * 70)
    print("✅ Twitter integration ready!")
    print("💰 API Credit: $25 (monitor usage at developer.twitter.com)")
    print("=" * 70)
