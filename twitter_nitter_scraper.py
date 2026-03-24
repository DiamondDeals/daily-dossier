#!/usr/bin/env python3
"""
Twitter Nitter Scraper - Free Twitter monitoring via Nitter instances
No API token required, uses RSS feeds
"""
import sys
import requests
import feedparser
import json
from datetime import datetime, timedelta
from pathlib import Path
import time

# Fix emoji output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class TwitterNitterScraper:
    def __init__(self):
        # Load account list
        config_path = Path(__file__).parent / 'twitter_monitoring_accounts.json'
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.accounts = config['accounts']

        # Nitter instances (public front-ends for Twitter)
        self.nitter_instances = [
            "https://nitter.net",
            "https://nitter.poast.org",
            "https://nitter.privacydev.net",
            "https://nitter.1d4.us"
        ]

        # Builder keywords (same as API version)
        self.builder_keywords = [
            "building", "built", "launched", "shipping", "released",
            "working on", "creating", "made", "developing",
            "product", "saas", "app", "tool", "platform",
            "feature", "update", "version", "beta",
            "#buildinginpublic", "build in public", "bip",
            "revenue", "mrr", "arr", "$", "customers", "users",
            "reached", "milestone", "growth",
            "learned", "lesson", "mistake", "what i wish",
            "advice", "tip", "strategy", "how i"
        ]

    def get_working_instance(self):
        """Find a working Nitter instance"""
        for instance in self.nitter_instances:
            try:
                response = requests.get(instance, timeout=5)
                if response.status_code == 200:
                    return instance
            except Exception:
                continue
        return None

    def fetch_user_tweets_rss(self, username, instance, max_results=10):
        """Fetch tweets via Nitter RSS feed"""
        try:
            rss_url = f"{instance}/{username}/rss"
            feed = feedparser.parse(rss_url)

            tweets = []
            for entry in feed.entries[:max_results]:
                tweet = {
                    'username': username,
                    'text': entry.get('description', ''),
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': entry.get('published_parsed', None)
                }

                # Only include tweets from last 48 hours
                if tweet['timestamp']:
                    tweet_date = datetime(*tweet['timestamp'][:6])
                    if datetime.now() - tweet_date < timedelta(hours=48):
                        tweets.append(tweet)

            return tweets

        except Exception:
            return []

    def score_tweet(self, tweet):
        """Score tweet based on builder keywords"""
        text = (tweet.get('text', '') + ' ' + tweet.get('title', '')).lower()

        score = 0
        matched_keywords = []

        for keyword in self.builder_keywords:
            if keyword in text:
                score += 1
                matched_keywords.append(keyword)

        return score, matched_keywords

    def scan_builders(self, max_accounts=30):
        """Scan Twitter builders using Nitter"""
        print("🔍 Scanning Twitter via Nitter (free scraping)...")

        # Find working Nitter instance
        instance = self.get_working_instance()
        if not instance:
            print("❌ No working Nitter instances available")
            return []

        print(f"✅ Using Nitter instance: {instance}\n")

        all_builds = []

        # Prioritize top builders (limit to avoid rate limiting)
        priority_accounts = [
            "levelsio", "dvassallo", "marc_louvion", "mckaywrigley",
            "rowancheung", "sama", "paulg", "naval", "patio11", "dhh",
            "jasonfried", "mijustin", "shl", "Suhail", "tdinh_me",
            "dannypostmaa", "swyx", "bentossell", "gregisenberg", "alexhormozi"
        ]

        accounts_to_scan = [acc for acc in priority_accounts if acc in self.accounts][:max_accounts]
        # If fewer than max_accounts from priority list, fill from full list
        if len(accounts_to_scan) < max_accounts:
            remaining = [a for a in self.accounts if a not in accounts_to_scan]
            accounts_to_scan += remaining[:max_accounts - len(accounts_to_scan)]

        for i, username in enumerate(accounts_to_scan, 1):
            print(f"[{i}/{len(accounts_to_scan)}] @{username}...", end=" ", flush=True)

            tweets = self.fetch_user_tweets_rss(username, instance)

            if not tweets:
                print("❌")
                time.sleep(1)
                continue

            found = 0
            for tweet in tweets:
                score, keywords = self.score_tweet(tweet)
                if score >= 2:
                    all_builds.append({
                        'username': username,
                        'text': tweet.get('text', '')[:200],
                        'url': tweet.get('url', ''),
                        'score': score,
                        'keywords': keywords[:3]
                    })
                    found += 1

            print(f"✅ {found}")
            time.sleep(1)

        # Sort by score
        all_builds.sort(key=lambda x: x['score'], reverse=True)

        print(f"\n✅ Found {len(all_builds)} builder updates")
        return all_builds[:25]


if __name__ == "__main__":
    scraper = TwitterNitterScraper()
    builds = scraper.scan_builders(max_accounts=20)

    print("\n📊 Top Builder Updates:\n")
    for i, build in enumerate(builds[:10], 1):
        print(f"{i}. @{build['username']}")
        print(f"   {build['text'][:100]}...")
        print(f"   Score: {build['score']} | Keywords: {', '.join(build['keywords'])}")
        print(f"   {build['url']}\n")
