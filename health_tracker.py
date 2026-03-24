#!/usr/bin/env python3
"""
Health Tracker - Monitor Pritikin Diet & health topics via Reddit + RSS
No Twitter API required - uses free sources only
"""
import sys
import feedparser
from datetime import datetime, timedelta
from reddit_json_client import RedditJSONClient

# Fix emoji output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class HealthTracker:
    def __init__(self):
        self.reddit_client = RedditJSONClient()

        # Health topics to track
        self.topics = {
            'pritikin': ['pritikin', 'pritikin diet', 'pritikin program'],
            'heart_health': ['heart disease', 'atherosclerosis', 'cholesterol', 'cardiac',
                             'heart attack', 'stent', 'blood pressure', 'hypertension',
                             'omega-3', 'omega 3', 'heart recovery', 'cardiac rehab'],
            'plant_based': ['plant based', 'whole food plant based', 'wfpb',
                            'oil free', 'no oil', 'vegan nutrition'],
            'diet_success': ['diet success', 'weight loss', 'health transformation',
                             'meal prep', 'healthy eating', 'clean eating']
        }

        # Health subreddits - expanded for better coverage
        self.health_subreddits = [
            'PlantBasedDiet', 'WholeFoodsPlantBased', 'nutrition',
            'HeartHealth', 'CardiacRecovery',
            'EatCheapAndHealthy', 'MealPrepSunday',
            'loseit', 'HealthyFood', 'veganfitness',
            'ScientificNutrition', 'mediterraneandiet'
        ]

        # RSS feeds specifically for health content (verified working March 2026)
        self.health_feeds = [
            {
                'name': 'NutritionFacts.org',
                'url': 'https://nutritionfacts.org/feed/',
                'category': 'Plant-Based Health'
            },
            {
                'name': 'Forks Over Knives',
                'url': 'https://www.forksoverknives.com/feed/',
                'category': 'Plant-Based Health'
            },
            {
                'name': 'Pritikin',
                'url': 'https://www.pritikin.com/feed/',
                'category': 'Pritikin'
            },
            {
                'name': 'AHA Circulation',
                'url': 'https://www.ahajournals.org/action/showFeed?type=etoc&feed=rss&jc=circ',
                'category': 'Heart Health'
            },
            {
                'name': 'ScienceDaily Heart',
                'url': 'https://www.sciencedaily.com/rss/health_medicine/heart_disease.xml',
                'category': 'Heart Health'
            },
            {
                'name': 'ScienceDaily Nutrition',
                'url': 'https://www.sciencedaily.com/rss/health_medicine/nutrition.xml',
                'category': 'Nutrition Research'
            }
        ]

    def scan_reddit_health(self):
        """Scan health subreddits for relevant discussions"""
        print(f"  Scanning {len(self.health_subreddits)} health subreddits...")

        all_posts = []

        for subreddit in self.health_subreddits:
            print(f"    r/{subreddit}...", end=" ", flush=True)

            try:
                posts = self.reddit_client.fetch_posts(subreddit, limit=25, sort='new')

                found = 0
                for post in posts:
                    health_post = self._analyze_health_reddit(post, subreddit)
                    if health_post:
                        all_posts.append(health_post)
                        found += 1

                print(f"{found}" if found > 0 else "0")

            except Exception as e:
                print(f"err")

        all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_posts

    def scan_rss_health(self, hours_back=48):
        """Scan health RSS feeds - 48h lookback for freshness"""
        print(f"  Scanning {len(self.health_feeds)} health RSS feeds...")

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        all_articles = []

        for feed_info in self.health_feeds:
            print(f"    {feed_info['name']}...", end=" ", flush=True)

            try:
                feed = feedparser.parse(feed_info['url'])
                found = 0

                for entry in feed.entries[:15]:
                    try:
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            pub_date = datetime(*entry.updated_parsed[:6])
                        else:
                            pub_date = datetime.now()
                    except:
                        pub_date = datetime.now()

                    if pub_date > cutoff_time:
                        title = entry.title if hasattr(entry, 'title') else 'Untitled'
                        url = entry.link if hasattr(entry, 'link') else ''
                        summary = entry.summary if hasattr(entry, 'summary') else ''

                        # Score based on topic relevance
                        text = (title + ' ' + summary).lower()
                        matched_topics = []
                        for topic, keywords in self.topics.items():
                            for keyword in keywords:
                                if keyword in text:
                                    matched_topics.append(topic)
                                    break

                        # Pritikin bonus
                        bonus = 20 if 'pritikin' in matched_topics else 0
                        score = len(matched_topics) * 10 + bonus + 5  # base score for being from a health feed

                        article = {
                            'platform': 'RSS',
                            'title': title,
                            'url': url,
                            'source': feed_info['name'],
                            'category': feed_info['category'],
                            'published': pub_date.isoformat(),
                            'topics': matched_topics if matched_topics else [feed_info['category'].lower()],
                            'score': score
                        }
                        all_articles.append(article)
                        found += 1

                print(f"{found}")

            except Exception as e:
                print(f"err")

        all_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_articles

    def scan_all(self):
        """Full health scan - Reddit + RSS, no Twitter needed"""
        print()
        reddit_posts = self.scan_reddit_health()
        rss_articles = self.scan_rss_health()

        # Combine and format for the dossier
        all_health = []

        for post in reddit_posts:
            all_health.append({
                'title': post.get('title', 'Untitled'),
                'url': post.get('url', ''),
                'source': f"r/{post.get('subreddit', 'unknown')}",
                'score': post.get('score', 0),
                'topics': post.get('topics', []),
                'platform': 'Reddit'
            })

        for article in rss_articles:
            all_health.append({
                'title': article.get('title', 'Untitled'),
                'url': article.get('url', ''),
                'source': article.get('source', 'unknown'),
                'score': article.get('score', 0),
                'topics': article.get('topics', []),
                'platform': 'RSS'
            })

        # Sort by score, prioritize Pritikin and heart health
        all_health.sort(key=lambda x: x.get('score', 0), reverse=True)

        return all_health

    def _analyze_health_reddit(self, post, subreddit):
        """Analyze Reddit post for health topic relevance"""
        text = (post.get('title', '') + ' ' + post.get('text', '')).lower()

        matched_topics = []
        for topic, keywords in self.topics.items():
            for keyword in keywords:
                if keyword in text:
                    matched_topics.append(topic)
                    break

        # For health subreddits, include high-engagement posts even without keyword match
        engagement = post.get('engagement_score', post.get('score', 0))
        if not matched_topics and engagement < 50:
            return None

        # If no keyword match but high engagement in a health sub, tag with subreddit name
        if not matched_topics:
            matched_topics = [subreddit.lower()]

        bonus = 20 if 'pritikin' in matched_topics else 0
        bonus += 10 if 'heart_health' in matched_topics else 0
        score = engagement + (len(matched_topics) * 10) + bonus

        return {
            'platform': 'Reddit',
            'title': post.get('title', 'Untitled'),
            'text': post.get('text', '')[:150],
            'author': post.get('author', 'unknown'),
            'subreddit': subreddit,
            'url': post.get('url', ''),
            'comments': post.get('num_comments', 0),
            'engagement_score': engagement,
            'topics': matched_topics,
            'score': score
        }


if __name__ == '__main__':
    print("=" * 70)
    print("HEALTH TRACKER - PRITIKIN DIET & WELLNESS MONITORING")
    print("=" * 70)

    tracker = HealthTracker()

    print("\nDaily Health & Wellness Scan")
    print("  Topics: Pritikin, heart health, plant-based, diet success")

    all_posts = tracker.scan_all()

    print(f"\nFound {len(all_posts)} health items total")

    if all_posts:
        print("\nTop 10:")
        for i, post in enumerate(all_posts[:10], 1):
            print(f"  {i}. [{post['source']}] {post['title'][:80]}")
            print(f"     Topics: {', '.join(post.get('topics', []))}")
