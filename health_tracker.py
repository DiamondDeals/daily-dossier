#!/usr/bin/env python3
"""
Health Tracker - Monitor Pritikin Diet & health topics across platforms
For Drew's health journey (<#C0ACZ9XR9E1>)
"""
import requests
from reddit_json_client import RedditJSONClient

class HealthTracker:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "BishopDailyDossier/1.0"
        }
        self.reddit_client = RedditJSONClient()
        
        # Health topics to track
        self.topics = {
            'pritikin': ['pritikin', 'pritikin diet', 'pritikin program'],
            'heart_health': ['heart disease', 'atherosclerosis', 'cholesterol', 'cardiac'],
            'plant_based': ['plant based', 'whole food plant based', 'wfpb'],
            'diet_success': ['diet success', 'weight loss', 'health transformation']
        }
        
        # Health subreddits
        self.health_subreddits = [
            'nutrition', 'diet', 'loseit', 'healthyfood',
            'EatCheapAndHealthy', 'PlantBasedDiet', 'WholeFoodsPlantBased',
            'fitness', 'Health', 'HealthyFood'
        ]
    
    def scan_twitter_health(self, account_list=None):
        """
        Monitor specific health/wellness accounts for Pritikin mentions
        Since search API requires paid tier, we monitor accounts instead
        """
        if account_list is None:
            # Health/wellness accounts to monitor
            account_list = [
                'drterrysimpson',  # Mentioned in Pritikin tweet
                'NutritionFacts',  # Dr. Greger
                'ColinTCampbell',  # Plant-based nutrition
                'DrNealBarnard',   # PCRM
                'DrFuhrman',       # Nutritarian diet
                'drmcdougall',     # McDougall Program
                'chrislakin'       # Mentioned in success story tweet
            ]
        
        print(f"🔍 Scanning {len(account_list)} health accounts for Pritikin/diet discussions...")
        print()
        
        all_health_posts = []
        
        for username in account_list:
            print(f"  @{username}...", end=" ", flush=True)
            
            try:
                # Get user ID
                user_endpoint = f"{self.base_url}/users/by/username/{username}"
                user_response = requests.get(user_endpoint, headers=self.headers, timeout=10)
                
                if user_response.status_code != 200:
                    print("❌")
                    continue
                
                user_id = user_response.json()['data']['id']
                
                # Get tweets
                tweets_endpoint = f"{self.base_url}/users/{user_id}/tweets"
                params = {
                    "max_results": 10,
                    "tweet.fields": "created_at,public_metrics",
                    "exclude": "retweets,replies"
                }
                
                tweets_response = requests.get(tweets_endpoint, headers=self.headers, params=params, timeout=10)
                
                if tweets_response.status_code != 200:
                    print("❌")
                    continue
                
                tweets = tweets_response.json().get('data', [])
                
                # Check for health keywords
                found = 0
                for tweet in tweets:
                    health_post = self._analyze_health_tweet(tweet, username)
                    if health_post:
                        all_health_posts.append(health_post)
                        found += 1
                
                print(f"✅ {found}")
                
            except Exception as e:
                print(f"❌ {e}")
        
        # Sort by engagement + relevance
        all_health_posts.sort(key=lambda x: x['score'], reverse=True)
        
        return all_health_posts
    
    def scan_reddit_health(self):
        """Scan health subreddits for relevant discussions"""
        print(f"\n🔍 Scanning {len(self.health_subreddits)} health subreddits...")
        print()
        
        all_posts = []
        
        for subreddit in self.health_subreddits:
            print(f"  r/{subreddit}...", end=" ", flush=True)
            
            try:
                posts = self.reddit_client.fetch_posts(subreddit, limit=25, sort='hot')
                
                found = 0
                for post in posts:
                    health_post = self._analyze_health_reddit(post, subreddit)
                    if health_post:
                        all_posts.append(health_post)
                        found += 1
                
                print(f"✅ {found}" if found > 0 else "○")
                
            except Exception as e:
                print("❌")
        
        # Sort by engagement
        all_posts.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return all_posts
    
    def _analyze_health_tweet(self, tweet, username):
        """Analyze tweet for health topic relevance"""
        text = tweet.get('text', '').lower()
        
        # Check topics
        matched_topics = []
        for topic, keywords in self.topics.items():
            for keyword in keywords:
                if keyword in text:
                    matched_topics.append(topic)
                    break
        
        if not matched_topics:
            return None
        
        # Get engagement
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        engagement = likes + (retweets * 2) + (replies * 3)
        
        # Bonus for Pritikin
        bonus = 20 if 'pritikin' in matched_topics else 0
        
        score = engagement + (len(matched_topics) * 10) + bonus
        
        return {
            'platform': 'Twitter',
            'text': tweet.get('text', ''),
            'author': username,
            'url': f"https://twitter.com/{username}/status/{tweet.get('id')}",
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'engagement': engagement,
            'topics': matched_topics,
            'score': score
        }
    
    def _analyze_health_reddit(self, post, subreddit):
        """Analyze Reddit post for health topic relevance"""
        text = (post['title'] + ' ' + post['text']).lower()
        
        # Check topics
        matched_topics = []
        for topic, keywords in self.topics.items():
            for keyword in keywords:
                if keyword in text:
                    matched_topics.append(topic)
                    break
        
        if not matched_topics:
            return None
        
        # Bonus for Pritikin
        bonus = 20 if 'pritikin' in matched_topics else 0
        
        score = post['engagement_score'] + (len(matched_topics) * 10) + bonus
        
        return {
            'platform': 'Reddit',
            'title': post['title'],
            'text': post['text'][:150],
            'author': post['author'],
            'subreddit': subreddit,
            'url': post['url'],
            'score': post['score'],
            'comments': post['num_comments'],
            'engagement_score': post['engagement_score'],
            'topics': matched_topics,
            'score': score
        }
    
    def generate_report(self, twitter_posts, reddit_posts, top_n=10):
        """Generate health tracking report"""
        report = []
        report.append("## 🏥 Health & Wellness Tracker\n")
        
        # Pritikin-specific findings
        pritikin_twitter = [p for p in twitter_posts if 'pritikin' in p['topics']]
        pritikin_reddit = [p for p in reddit_posts if 'pritikin' in p['topics']]
        
        if pritikin_twitter or pritikin_reddit:
            report.append("### 🎯 Pritikin Diet Discussions\n")
            
            for post in pritikin_twitter[:3]:
                report.append(f"**Twitter: @{post['author']}**")
                report.append(f"- \"{post['text'][:120]}...\"")
                report.append(f"- {post['url']}\n")
            
            for post in pritikin_reddit[:3]:
                report.append(f"**Reddit: r/{post['subreddit']}**")
                report.append(f"- {post['title']}")
                report.append(f"- {post['url']}\n")
        
        # Top general health discussions
        all_posts = twitter_posts + reddit_posts
        all_posts.sort(key=lambda x: x['score'], reverse=True)
        
        if all_posts:
            report.append("### 📊 Top Health Discussions\n")
            
            for i, post in enumerate(all_posts[:top_n], 1):
                platform_emoji = "🐦" if post['platform'] == 'Twitter' else "📊"
                topics_str = ', '.join([f"#{t}" for t in post['topics']])
                
                report.append(f"**{i}. {platform_emoji} {post.get('title', post.get('text', '')[:60])}...**")
                
                if post['platform'] == 'Twitter':
                    report.append(f"- @{post['author']} • {topics_str}")
                    report.append(f"- ❤️{post['likes']} 🔁{post['retweets']} 💬{post['replies']}")
                else:
                    report.append(f"- r/{post['subreddit']} • {topics_str}")
                    report.append(f"- ↑{post['score']} 💬{post['comments']}")
                
                report.append(f"- {post['url']}\n")
        else:
            report.append("*No health discussions found today*\n")
        
        # Stats
        report.append(f"\n**Stats:** {len(twitter_posts)} Twitter + {len(reddit_posts)} Reddit")
        
        return '\n'.join(report)

if __name__ == '__main__':
    print("=" * 70)
    print("HEALTH TRACKER - PRITIKIN DIET & WELLNESS MONITORING")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    tracker = HealthTracker(bearer_token)
    
    print("\n🏥 Daily Health & Wellness Scan")
    print("   Topics: Pritikin, heart health, plant-based, diet success")
    print()
    
    # Scan Twitter
    twitter_posts = tracker.scan_twitter_health()
    
    # Scan Reddit
    reddit_posts = tracker.scan_reddit_health()
    
    # Generate report
    print("\n" + "=" * 70)
    print(tracker.generate_report(twitter_posts, reddit_posts))
    print("=" * 70)
    
    print(f"\n✅ Health tracking complete!")
    print(f"   Found: {len(twitter_posts)} Twitter + {len(reddit_posts)} Reddit posts")
