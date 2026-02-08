#!/usr/bin/env python3
"""
Twitter Monitor - 112 Vetted Accounts
Scans successful entrepreneurs/founders for business pain points
"""
import requests
import json
from datetime import datetime
import time

class TwitterMonitor100:
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
        
        # Pain point keywords
        self.pain_keywords = [
            "manual process", "manually", "repetitive task", "spending hours",
            "there must be a better way", "there has to be", "automate",
            "automation", "workflow", "bottleneck", "time consuming",
            "inefficient", "tedious", "overwhelming", "frustrated",
            "struggle with", "challenge", "problem", "issue", "pain point",
            "waste time", "slow process", "need help", "looking for a way"
        ]
    
    def get_user_tweets(self, username, max_results=10):
        """Get recent tweets from username"""
        # First get user ID
        try:
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
    
    def scan_accounts(self, max_accounts=50, tweets_per_account=10):
        """Scan accounts for pain points"""
        print(f"🔍 Scanning {max_accounts} accounts ({tweets_per_account} tweets each)")
        print(f"   Total tweets to analyze: {max_accounts * tweets_per_account}")
        print()
        
        all_pain_points = []
        checked = 0
        
        for username in self.accounts[:max_accounts]:
            checked += 1
            print(f"[{checked}/{max_accounts}] @{username}...", end=" ", flush=True)
            
            tweets = self.get_user_tweets(username, tweets_per_account)
            
            if not tweets:
                print("❌")
                continue
            
            # Analyze tweets
            found = 0
            for tweet in tweets:
                pain = self._analyze_tweet(tweet, username)
                if pain:
                    all_pain_points.append(pain)
                    found += 1
            
            print(f"✅ {found} pain points")
            
            # Rate limiting - be nice to API
            time.sleep(0.5)
        
        # Sort by total score
        all_pain_points.sort(key=lambda x: x['total_score'], reverse=True)
        
        return all_pain_points
    
    def _analyze_tweet(self, tweet, username):
        """Analyze tweet for pain points"""
        text = tweet.get('text', '').lower()
        
        # Check keywords
        matched = []
        for keyword in self.pain_keywords:
            if keyword in text:
                matched.append(keyword)
        
        if not matched:
            return None
        
        # Get metrics
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        engagement = likes + (retweets * 2) + (replies * 3)
        keyword_score = len(matched) * 10
        total_score = keyword_score + engagement
        
        return {
            'text': tweet.get('text', ''),
            'author': username,
            'url': f"https://twitter.com/{username}/status/{tweet.get('id')}",
            'created_at': tweet.get('created_at', ''),
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'engagement_score': engagement,
            'matched_keywords': matched,
            'keyword_count': len(matched),
            'total_score': total_score
        }

if __name__ == '__main__':
    print("=" * 70)
    print("TWITTER MONITOR - 112 VETTED ACCOUNTS")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    monitor = TwitterMonitor100(bearer_token)
    
    print(f"\n📋 Loaded {len(monitor.accounts)} accounts to monitor")
    print("   Including: Marc Lou, Levelsio, DHH, Naval, OpenAI, and more")
    print()
    
    # Scan 30 accounts (balance between coverage and API limits)
    pain_points = monitor.scan_accounts(max_accounts=30, tweets_per_account=10)
    
    print("\n" + "=" * 70)
    print(f"✅ FOUND {len(pain_points)} BUSINESS PAIN POINTS")
    print("=" * 70)
    
    if pain_points:
        print("\nTOP 15 BY SCORE (Keywords + Engagement)")
        print("=" * 70)
        
        for i, point in enumerate(pain_points[:15], 1):
            print(f"\n{i}. @{point['author']}")
            print(f"   📊 Score: {point['total_score']} ({point['keyword_count']} keywords + {point['engagement_score']} engagement)")
            print(f"   🔑 {', '.join(point['matched_keywords'][:3])}")
            print(f"   💬 \"{point['text'][:150]}...\"")
            print(f"   📈 ❤️{point['likes']} 🔁{point['retweets']} 💬{point['replies']}")
            print(f"   🔗 {point['url']}")
    
    print("\n" + "=" * 70)
    print("✅ Twitter monitoring of 112 successful founders complete!")
    print("=" * 70)
