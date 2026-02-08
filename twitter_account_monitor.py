#!/usr/bin/env python3
"""
Twitter Account Monitor - Free Tier Approach
Monitors specific business/entrepreneur accounts for pain points
No search endpoint needed!
"""
import requests
import json
from datetime import datetime

class TwitterAccountMonitor:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "BishopDailyDossier/1.0"
        }
        
        # High-value accounts to monitor (entrepreneurs, founders, business owners)
        self.target_accounts = [
            # Startup/Entrepreneur influencers
            "paulg",           # Paul Graham (Y Combinator)
            "levelsio",        # Pieter Levels (Indie hacker)
            "naval",           # Naval Ravikant
            "sama",            # Sam Altman
            "dhh",             # DHH (Basecamp)
            "jason",           # Jason Fried (Basecamp)
            "Patrick_OShag",   # Patrick O'Shaughnessy
            "alexisohanian",   # Alexis Ohanian (Reddit co-founder)
            "hnshah",          # Hiten Shah (SaaS founder)
            "Suhail",          # Suhail Doshi (Mixpanel)
            
            # SaaS/Tech founders
            "zapier",          # Zapier account
            "NotionHQ",        # Notion
            "SlackHQ",         # Slack
            "airtable",        # Airtable
            "figma",           # Figma
            
            # Business/productivity
            "salesforce",      # Salesforce
            "HubSpot",         # HubSpot
            "buffer",          # Buffer
            
            # Entrepreneur communities
            "FoundersPodcast", # Founders podcast
            "IndieHackers",    # Indie Hackers
        ]
        
        # Business problem keywords to detect
        self.pain_keywords = [
            "manual process", "manually", "repetitive task", "spending hours",
            "there must be a better way", "there has to be", "automate",
            "automation", "workflow", "bottleneck", "time consuming",
            "inefficient", "tedious", "overwhelming", "frustrated",
            "struggle with", "challenge", "problem", "issue", "pain point"
        ]
    
    def get_user_id(self, username):
        """Get user ID from username"""
        endpoint = f"{self.base_url}/users/by/username/{username}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['data']['id']
        except Exception as e:
            print(f"Error getting ID for @{username}: {e}")
            return None
    
    def get_recent_tweets(self, user_id, max_results=10):
        """Get recent tweets from a user"""
        endpoint = f"{self.base_url}/users/{user_id}/tweets"
        
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,conversation_id",
            "exclude": "retweets,replies"  # Only original tweets
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            print(f"Error fetching tweets for user {user_id}: {e}")
            return []
    
    def scan_for_pain_points(self, max_accounts=10, tweets_per_account=10):
        """
        Scan target accounts for business pain points
        """
        print(f"🔍 Scanning {max_accounts} business accounts for pain points...")
        print()
        
        all_pain_points = []
        
        for i, username in enumerate(self.target_accounts[:max_accounts], 1):
            print(f"[{i}/{max_accounts}] Checking @{username}...", end=" ")
            
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                print("❌ Failed")
                continue
            
            # Get recent tweets
            tweets = self.get_recent_tweets(user_id, tweets_per_account)
            
            if not tweets:
                print("⚠️ No tweets")
                continue
            
            # Scan tweets for pain points
            found = 0
            for tweet in tweets:
                pain_point = self._analyze_tweet(tweet, username)
                if pain_point:
                    all_pain_points.append(pain_point)
                    found += 1
            
            print(f"✅ Found {found} pain points")
        
        # Sort by engagement + keyword matches
        all_pain_points.sort(key=lambda x: x['total_score'], reverse=True)
        
        return all_pain_points
    
    def _analyze_tweet(self, tweet, username):
        """Analyze tweet for business pain points"""
        text = tweet.get('text', '').lower()
        
        # Check for pain point keywords
        matched_keywords = []
        for keyword in self.pain_keywords:
            if keyword in text:
                matched_keywords.append(keyword)
        
        # Must have at least one keyword
        if not matched_keywords:
            return None
        
        # Get engagement metrics
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        engagement_score = likes + (retweets * 2) + (replies * 3)
        
        # Calculate total score (keywords + engagement)
        keyword_score = len(matched_keywords) * 10
        total_score = keyword_score + engagement_score
        
        return {
            'text': tweet.get('text', ''),
            'author': username,
            'url': f"https://twitter.com/{username}/status/{tweet.get('id')}",
            'created_at': tweet.get('created_at', ''),
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'engagement_score': engagement_score,
            'matched_keywords': matched_keywords,
            'keyword_count': len(matched_keywords),
            'total_score': total_score
        }

if __name__ == '__main__':
    print("=" * 70)
    print("TWITTER ACCOUNT MONITOR - BUSINESS PAIN POINT DETECTOR")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    monitor = TwitterAccountMonitor(bearer_token)
    
    print(f"\n📋 Monitoring {len(monitor.target_accounts)} high-value business accounts")
    print("   (Scanning 10 accounts, 10 tweets each)")
    print()
    
    pain_points = monitor.scan_for_pain_points(max_accounts=10, tweets_per_account=10)
    
    print("\n" + "=" * 70)
    print(f"✅ FOUND {len(pain_points)} BUSINESS PAIN POINTS")
    print("=" * 70)
    
    if pain_points:
        print("\nTOP 10 BY TOTAL SCORE (Keywords + Engagement)")
        print("=" * 70)
        
        for i, point in enumerate(pain_points[:10], 1):
            print(f"\n{i}. @{point['author']}")
            print(f"   📊 Score: {point['total_score']} ({point['keyword_count']} keywords + {point['engagement_score']} engagement)")
            print(f"   🔑 Keywords: {', '.join(point['matched_keywords'][:3])}")
            print(f"   💬 \"{point['text'][:120]}...\"")
            print(f"   📈 ❤️{point['likes']} 🔁{point['retweets']} 💬{point['replies']}")
            print(f"   🔗 {point['url']}")
    else:
        print("\n⚠️ No pain points found in recent tweets")
        print("   Try again later or increase the number of accounts monitored")
    
    print("\n" + "=" * 70)
    print("✅ Twitter account monitoring ready!")
    print("💡 This approach uses FREE tier API - no $100/month upgrade needed")
    print("=" * 70)
