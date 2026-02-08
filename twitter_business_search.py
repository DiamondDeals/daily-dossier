#!/usr/bin/env python3
"""
Twitter Business Pain Point Search - REFINED
Focused on business/startup/entrepreneur accounts
"""
import requests
import json
from datetime import datetime

class TwitterBusinessSearch:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "BishopDailyDossier/1.0"
        }
    
    def search_business_problems(self, max_results=100):
        """
        Search for business problems/pain points in entrepreneur communities
        """
        # More targeted query focusing on business contexts
        query = """(
            "how do I automate" OR
            "manual process" OR  
            "spending too much time" OR
            "there has to be a better way" OR
            "repetitive task" OR
            "workflow problem" OR
            "need help automating" OR
            "too many manual steps"
        ) (
            from:businessinsider OR
            from:FastCompany OR
            #entrepreneur OR
            #startup OR
            #smallbusiness OR
            #solopreneur OR
            #SaaS
        ) lang:en -is:retweet -is:reply"""
        
        endpoint = f"{self.base_url}/tweets/search/recent"
        
        params = {
            "query": query,
            "max_results": min(max_results, 100),  # API limit is 100
            "tweet.fields": "created_at,public_metrics,author_id",
            "expansions": "author_id",
            "user.fields": "username,name,verified,public_metrics"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                print("⚠️ No tweets found matching criteria")
                return []
            
            # Parse results
            tweets = []
            users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
            
            for tweet in data['data']:
                parsed = self._parse_tweet(tweet, users)
                if parsed and not parsed['is_spam']:
                    tweets.append(parsed)
            
            # Sort by engagement + follower weight
            tweets.sort(key=lambda x: x['weighted_score'], reverse=True)
            
            return tweets
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("❌ Rate limit hit - you've used too much API credit")
                print("   Check usage at: https://developer.twitter.com/en/portal/dashboard")
            elif e.response.status_code == 403:
                print("❌ Access denied - check your API access level")
                print("   Free tier might not include search endpoint")
            else:
                print(f"❌ HTTP Error {e.response.status_code}: {e}")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def _parse_tweet(self, tweet, users):
        """Parse tweet with business context scoring"""
        try:
            author_id = tweet.get('author_id')
            user = users.get(author_id, {})
            user_metrics = user.get('public_metrics', {})
            
            # Get engagement metrics
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)
            
            # Base engagement score
            engagement_score = likes + (retweets * 2) + (replies * 3)
            
            # Weight by author's follower count (credibility signal)
            followers = user_metrics.get('followers_count', 0)
            follower_weight = min(followers / 1000, 10)  # Cap at 10x boost
            
            # Weighted score
            weighted_score = engagement_score * (1 + follower_weight)
            
            text = tweet.get('text', '')
            
            # Spam detection
            is_spam = self._is_spam(text, user)
            
            return {
                'text': text,
                'author': user.get('username', 'unknown'),
                'author_name': user.get('name', 'Unknown'),
                'verified': user.get('verified', False),
                'followers': followers,
                'created_at': tweet.get('created_at', ''),
                'likes': likes,
                'retweets': retweets,
                'replies': replies,
                'engagement_score': engagement_score,
                'weighted_score': int(weighted_score),
                'tweet_id': tweet.get('id'),
                'url': f"https://twitter.com/{user.get('username', 'i')}/status/{tweet.get('id')}",
                'is_spam': is_spam
            }
            
        except Exception as e:
            print(f"Error parsing tweet: {e}")
            return None
    
    def _is_spam(self, text, user):
        """Detect spam/promotional content"""
        spam_keywords = [
            'dm me', 'link in bio', 'check out my',
            'promo code', 'discount', 'limited time',
            'buy now', 'click here', 'follow for follow',
            'giveaway', 'contest', 'win free'
        ]
        
        text_lower = text.lower()
        
        for keyword in spam_keywords:
            if keyword in text_lower:
                return True
        
        # Too many hashtags = spam
        if text.count('#') > 5:
            return True
        
        # Too many mentions = spam
        if text.count('@') > 3:
            return True
        
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("TWITTER BUSINESS PAIN POINT SEARCH - REFINED VERSION")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    search = TwitterBusinessSearch(bearer_token)
    
    print("\n🔍 Searching for business automation pain points...")
    print("   Targeting: entrepreneur, startup, smallbusiness communities")
    print()
    
    tweets = search.search_business_problems(max_results=100)
    
    if tweets:
        print(f"✅ Found {len(tweets)} relevant business pain points")
        print("\n" + "=" * 70)
        print("TOP 10 BUSINESS PAIN POINTS (Weighted by engagement + followers)")
        print("=" * 70)
        
        for i, tweet in enumerate(tweets[:10], 1):
            verified = "✓" if tweet['verified'] else ""
            
            print(f"\n{i}. @{tweet['author']} {verified}")
            print(f"   👥 {tweet['followers']:,} followers")
            print(f"   📊 Engagement: {tweet['engagement_score']} | Weighted: {tweet['weighted_score']}")
            print(f"   💬 \"{tweet['text'][:150]}...\"")
            print(f"   🔗 {tweet['url']}")
        
        print("\n" + "=" * 70)
        print("✅ Business-focused Twitter search ready!")
        print("💡 These are validated pain points from real business accounts")
        print("=" * 70)
    else:
        print("\n⚠️ No results found. This could mean:")
        print("   1. Free tier API might not include search endpoint")
        print("   2. Need to upgrade to Basic tier ($100/month)")
        print("   3. Search endpoint requires elevated access")
        print("\n💡 Check your API access level at:")
        print("   https://developer.twitter.com/en/portal/products")
