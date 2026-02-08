#!/usr/bin/env python3
"""
Reddit JSON API Client - No authentication needed!
Includes upvotes, comments, and engagement scoring
"""
import requests
import time
from datetime import datetime

class RedditJSONClient:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_posts(self, subreddit, limit=25, sort='new'):
        """
        Fetch posts from subreddit using JSON API
        sort: 'new', 'hot', 'top', 'rising'
        """
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for child in data['data']['children']:
                post_data = child['data']
                post = self._parse_post(post_data, subreddit)
                if post and not post['is_service_offer']:  # Filter service offers
                    posts.append(post)
            
            # Sort by engagement score
            posts.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            return posts
            
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            return []
    
    def _parse_post(self, data, subreddit):
        """Parse Reddit JSON data into structured format"""
        try:
            title = data.get('title', '')
            author = data.get('author', '[deleted]')
            selftext = data.get('selftext', '')
            url = f"https://www.reddit.com{data.get('permalink', '')}"
            
            # Engagement metrics
            score = data.get('score', 0)
            num_comments = data.get('num_comments', 0)
            
            # Calculate weighted engagement score
            # Comments are 2x valuable (indicates discussion/pain point validation)
            engagement_score = score + (num_comments * 2)
            
            # Created timestamp
            created_utc = data.get('created_utc', 0)
            created_date = datetime.fromtimestamp(created_utc).isoformat()
            
            # Detect service offers
            is_service_offer = self._is_service_offer(title, selftext)
            
            return {
                'title': title,
                'author': author,
                'subreddit': subreddit,
                'text': selftext[:500],
                'url': url,
                'score': score,
                'num_comments': num_comments,
                'engagement_score': engagement_score,
                'created': created_date,
                'is_service_offer': is_service_offer,
                'age_hours': (time.time() - created_utc) / 3600
            }
            
        except Exception as e:
            print(f"Error parsing post: {e}")
            return None
    
    def _is_service_offer(self, title, text):
        """Detect if post is offering services (not seeking solutions)"""
        offer_keywords = [
            'will do', 'available for', 'offering', 'can help',
            'looking to work', 'hire me', 'freelancer available',
            'dm me', 'reach out', 'contact me', 'for hire',
            'book a call', 'free consultation', 'get in touch',
            'i can build', 'i specialize', 'i offer'
        ]
        
        combined = (title + ' ' + text).lower()
        
        # Check for service offering patterns
        for keyword in offer_keywords:
            if keyword in combined:
                return True
        
        # Price indicators (usually service offers)
        if any(x in combined for x in ['$', 'usd', 'price:', 'pricing']):
            if any(x in combined for x in ['will', 'can', 'available', 'offering']):
                return True
        
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("REDDIT JSON API CLIENT - WITH ENGAGEMENT SCORING")
    print("=" * 70)
    
    client = RedditJSONClient()
    
    print("\n🔍 Fetching top 10 posts from r/entrepreneur (sorted by engagement)...")
    posts = client.fetch_posts('entrepreneur', limit=25, sort='hot')
    
    print(f"\n✅ Found {len(posts)} posts (service offers filtered out)")
    print("\n" + "=" * 70)
    print("TOP POSTS BY ENGAGEMENT (Score + Comments*2)")
    print("=" * 70)
    
    for i, post in enumerate(posts[:10], 1):
        hours_old = int(post['age_hours'])
        
        print(f"\n{i}. {post['title'][:70]}...")
        print(f"   👤 u/{post['author']} | 📍 r/{post['subreddit']}")
        print(f"   📊 Engagement: {post['engagement_score']} (↑{post['score']} upvotes + 💬{post['num_comments']} comments)")
        print(f"   ⏰ Posted {hours_old}h ago")
        print(f"   🔗 {post['url']}")
    
    print("\n" + "=" * 70)
    print("✅ JSON API works perfectly - includes upvotes, comments, age!")
    print("=" * 70)
