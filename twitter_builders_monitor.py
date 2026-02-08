#!/usr/bin/env python3
"""
Twitter Builders Monitor - Focus on #buildinginpublic, products, SaaS
Tracks what the 112 successful founders are BUILDING
"""
import requests
import json
from datetime import datetime
import time

class TwitterBuildersMonitor:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "BishopDailyDossier/1.0"
        }
        
        # Load account list
        with open('twitter_monitoring_accounts.json', 'r') as f:
            config = json.load(f)
            self.accounts = config['accounts']
        
        # Builder/product keywords
        self.builder_keywords = [
            # Building/launching
            "building", "built", "launched", "shipping", "released",
            "working on", "creating", "made", "developing",
            
            # Product/SaaS
            "product", "saas", "app", "tool", "platform",
            "feature", "update", "version", "beta",
            
            # Building in public
            "#buildinginpublic", "build in public", "bip",
            
            # Revenue/metrics (public builders)
            "revenue", "mrr", "arr", "$", "customers", "users",
            "reached", "milestone", "growth",
            
            # Lessons/insights
            "learned", "lesson", "mistake", "what i wish",
            "advice", "tip", "strategy", "how i"
        ]
    
    def get_user_tweets(self, username, max_results=10):
        """Get recent tweets from username"""
        try:
            # Get user ID
            user_endpoint = f"{self.base_url}/users/by/username/{username}"
            user_response = requests.get(user_endpoint, headers=self.headers, timeout=10)
            user_response.raise_for_status()
            user_id = user_response.json()['data']['id']
            
            # Get tweets
            tweets_endpoint = f"{self.base_url}/users/{user_id}/tweets"
            params = {
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics",
                "exclude": "retweets,replies"
            }
            
            tweets_response = requests.get(tweets_endpoint, headers=self.headers, params=params, timeout=10)
            tweets_response.raise_for_status()
            
            return tweets_response.json().get('data', [])
            
        except Exception as e:
            return []
    
    def scan_builders(self, max_accounts=30, tweets_per_account=10):
        """Scan for building/shipping/product updates"""
        print(f"🔍 Scanning {max_accounts} builder accounts...")
        print()
        
        all_builds = []
        
        for i, username in enumerate(self.accounts[:max_accounts], 1):
            print(f"[{i}/{max_accounts}] @{username}...", end=" ", flush=True)
            
            tweets = self.get_user_tweets(username, tweets_per_account)
            
            if not tweets:
                print("❌")
                continue
            
            # Find builder/product tweets
            found = 0
            for tweet in tweets:
                build = self._analyze_tweet(tweet, username)
                if build:
                    all_builds.append(build)
                    found += 1
            
            print(f"✅ {found}")
            time.sleep(0.5)  # Rate limiting
        
        # Sort by total score
        all_builds.sort(key=lambda x: x['total_score'], reverse=True)
        
        return all_builds
    
    def _analyze_tweet(self, tweet, username):
        """Analyze tweet for building/product content"""
        text = tweet.get('text', '').lower()
        
        # Check for builder keywords
        matched = []
        for keyword in self.builder_keywords:
            if keyword in text:
                matched.append(keyword)
        
        # Must have at least one keyword
        if not matched:
            return None
        
        # Get engagement
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        engagement_score = likes + (retweets * 2) + (replies * 3)
        
        # Bonus for #buildinginpublic or revenue mentions
        bonus = 0
        if '#buildinginpublic' in text or 'build in public' in text:
            bonus += 20
        if any(x in text for x in ['$', 'revenue', 'mrr', 'arr']):
            bonus += 15
        if any(x in text for x in ['launched', 'shipping', 'released']):
            bonus += 10
        
        keyword_score = len(matched) * 5
        total_score = keyword_score + engagement_score + bonus
        
        return {
            'text': tweet.get('text', ''),
            'author': username,
            'url': f"https://twitter.com/{username}/status/{tweet.get('id')}",
            'created_at': tweet.get('created_at', ''),
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'engagement_score': engagement_score,
            'matched_keywords': matched,
            'keyword_count': len(matched),
            'bonus': bonus,
            'total_score': total_score,
            'category': self._categorize(text, matched)
        }
    
    def _categorize(self, text, keywords):
        """Categorize the type of build/update"""
        if '#buildinginpublic' in text or 'build in public' in text:
            return "🏗️ Building in Public"
        elif any(x in text for x in ['launched', 'shipping', 'released']):
            return "🚀 Launch/Release"
        elif any(x in text for x in ['$', 'revenue', 'mrr', 'arr', 'customers']):
            return "💰 Revenue/Growth"
        elif any(x in text for x in ['learned', 'lesson', 'mistake']):
            return "📚 Lesson/Insight"
        elif any(x in text for x in ['product', 'feature', 'update']):
            return "✨ Product Update"
        else:
            return "🛠️ Building"

if __name__ == '__main__':
    print("=" * 70)
    print("TWITTER BUILDERS MONITOR - WHAT SUCCESSFUL FOUNDERS ARE BUILDING")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    monitor = TwitterBuildersMonitor(bearer_token)
    
    print(f"\n📋 Monitoring {len(monitor.accounts)} successful builder accounts")
    print()
    
    builds = monitor.scan_builders(max_accounts=30, tweets_per_account=10)
    
    print("\n" + "=" * 70)
    print(f"✅ FOUND {len(builds)} BUILDING UPDATES")
    print("=" * 70)
    
    if builds:
        print("\nTOP 15 BUILDING UPDATES (By engagement + category bonus)")
        print("=" * 70)
        
        for i, build in enumerate(builds[:15], 1):
            print(f"\n{i}. {build['category']} • @{build['author']}")
            print(f"   📊 Score: {build['total_score']} (engagement: {build['engagement_score']} + bonus: {build['bonus']})")
            print(f"   💬 \"{build['text'][:150]}...\"")
            print(f"   📈 ❤️{build['likes']} 🔁{build['retweets']} 💬{build['replies']}")
            print(f"   🔗 {build['url']}")
    
    print("\n" + "=" * 70)
    print("✅ Now tracking what successful founders are BUILDING!")
    print("=" * 70)
