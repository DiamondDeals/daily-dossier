#!/usr/bin/env python3
"""
Bluesky Scanner - Free public API, no auth needed
Replaces dead Nitter/Twitter scraping for builder content
Uses AT Protocol public endpoints
"""
import sys
import requests
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time

# Fix emoji output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class BlueskySanner:
    def __init__(self):
        self.base_url = "https://public.api.bsky.app"

        # Builder/entrepreneur accounts on Bluesky
        self.builder_accounts = [
            "levelsio.bsky.social",
            "swyx.bsky.social",
            "dhh.bsky.social",
            "jasonfried.bsky.social",
            "paulg.bsky.social",
            "naval.bsky.social",
            "patio11.bsky.social",
            "gregisenberg.bsky.social",
            "marclouvion.bsky.social",
            "dannypostmaa.bsky.social",
            "shl.bsky.social",
            "tdinh.bsky.social",
            "bentossell.bsky.social",
            "rowancheung.bsky.social",
            "alexhormozi.bsky.social",
            "codiesanchez.bsky.social",
            "justinwelsh.bsky.social",
            "lennyrachitsky.bsky.social",
            "sahilbloom.bsky.social",
            "jarydhermannseolondon.bsky.social",
        ]

        # Builder keywords for scoring
        self.builder_keywords = [
            "building", "built", "launched", "shipping", "released",
            "working on", "creating", "made", "developing",
            "product", "saas", "app", "tool", "platform",
            "feature", "update", "version", "beta",
            "buildinginpublic", "build in public",
            "revenue", "mrr", "arr", "customers", "users",
            "reached", "milestone", "growth",
            "learned", "lesson", "mistake", "what i wish",
            "advice", "tip", "strategy", "how i",
            "startup", "founder", "entrepreneur", "business"
        ]

    def search_posts(self, query, limit=25, hours_back=168):
        """Search Bluesky posts using public API"""
        try:
            since = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
            url = f"{self.base_url}/xrpc/app.bsky.feed.searchPosts"
            params = {
                'q': query,
                'limit': min(limit, 25),
                'sort': 'latest',
                'since': since
            }
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json().get('posts', [])
            return []
        except Exception:
            return []

    def get_author_feed(self, handle, limit=10):
        """Get recent posts from a specific Bluesky user"""
        try:
            url = f"{self.base_url}/xrpc/app.bsky.feed.getAuthorFeed"
            params = {
                'actor': handle,
                'limit': limit,
                'filter': 'posts_no_replies'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('feed', [])
            return []
        except Exception:
            return []

    def score_post(self, text):
        """Score a post based on builder keywords"""
        text_lower = text.lower()
        score = 0
        matched = []

        for keyword in self.builder_keywords:
            if keyword in text_lower:
                score += 1
                matched.append(keyword)

        return score, matched

    def _parse_post(self, feed_item):
        """Extract useful data from a Bluesky feed item"""
        post = feed_item.get('post', feed_item)
        record = post.get('record', {})
        author = post.get('author', {})

        text = record.get('text', '')
        created_at = record.get('createdAt', '')

        # Parse timestamp
        try:
            if created_at:
                pub_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                pub_date = datetime.now(timezone.utc)
        except:
            pub_date = datetime.now(timezone.utc)

        # Engagement metrics
        like_count = post.get('likeCount', 0)
        repost_count = post.get('repostCount', 0)
        reply_count = post.get('replyCount', 0)

        handle = author.get('handle', 'unknown')
        display_name = author.get('displayName', handle)
        uri = post.get('uri', '')

        # Convert AT URI to web URL
        # at://did:plc:xxx/app.bsky.feed.post/yyy -> https://bsky.app/profile/handle/post/yyy
        post_id = uri.split('/')[-1] if '/' in uri else ''
        web_url = f"https://bsky.app/profile/{handle}/post/{post_id}" if post_id else ''

        return {
            'text': text,
            'author': display_name,
            'handle': handle,
            'url': web_url,
            'published': pub_date.isoformat(),
            'likes': like_count,
            'reposts': repost_count,
            'replies': reply_count,
            'engagement': like_count + (repost_count * 2) + (reply_count * 3)
        }

    def scan_builders(self, max_accounts=20):
        """Scan Bluesky for builder content"""
        print("  Scanning Bluesky for builder content...")

        all_builds = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=168)  # 7 days

        # 1. Search for building-in-public content
        search_queries = [
            "buildinginpublic",
            "launched today",
            "shipped feature",
            "startup revenue MRR",
            "just launched saas"
        ]

        for query in search_queries:
            print(f"    Search: '{query}'...", end=" ", flush=True)
            posts = self.search_posts(query, limit=15)
            found = 0

            for post_data in posts:
                parsed = self._parse_post(post_data)
                score, keywords = self.score_post(parsed['text'])

                if score >= 2:
                    try:
                        pub_date = datetime.fromisoformat(parsed['published'])
                        if pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)
                        if pub_date < cutoff:
                            continue
                    except:
                        pass

                    all_builds.append({
                        'username': parsed['handle'],
                        'display_name': parsed['author'],
                        'text': parsed['text'][:250],
                        'url': parsed['url'],
                        'likes': parsed['likes'],
                        'reposts': parsed['reposts'],
                        'replies': parsed['replies'],
                        'score': score + parsed['engagement'],
                        'keywords': keywords[:5],
                        'source': 'search'
                    })
                    found += 1

            print(f"{found}")
            time.sleep(0.5)

        # 2. Check known builder accounts
        print(f"    Checking {min(max_accounts, len(self.builder_accounts))} builder accounts...")
        accounts_to_check = self.builder_accounts[:max_accounts]

        for handle in accounts_to_check:
            try:
                feed = self.get_author_feed(handle, limit=5)
                for item in feed:
                    parsed = self._parse_post(item)

                    # Filter out old posts
                    try:
                        pub_date = datetime.fromisoformat(parsed['published'])
                        if pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)
                        if pub_date < cutoff:
                            continue
                    except:
                        pass

                    score, keywords = self.score_post(parsed['text'])

                    if score >= 1 and parsed['engagement'] >= 3:
                        all_builds.append({
                            'username': parsed['handle'],
                            'display_name': parsed['author'],
                            'text': parsed['text'][:250],
                            'url': parsed['url'],
                            'likes': parsed['likes'],
                            'reposts': parsed['reposts'],
                            'replies': parsed['replies'],
                            'score': score + parsed['engagement'],
                            'keywords': keywords[:5],
                            'source': 'account'
                        })

                time.sleep(0.3)
            except Exception:
                continue

        # Deduplicate by URL
        seen_urls = set()
        unique_builds = []
        for build in all_builds:
            if build['url'] not in seen_urls:
                seen_urls.add(build['url'])
                unique_builds.append(build)

        # Sort by score
        unique_builds.sort(key=lambda x: x['score'], reverse=True)

        print(f"    Found {len(unique_builds)} builder updates")
        return unique_builds[:30]


if __name__ == "__main__":
    scanner = BlueskySanner()
    builds = scanner.scan_builders(max_accounts=15)

    print(f"\nTop Builder Updates ({len(builds)}):\n")
    for i, build in enumerate(builds[:15], 1):
        print(f"{i}. @{build['username']} ({build['display_name']})")
        print(f"   {build['text'][:120]}...")
        print(f"   Likes: {build['likes']} | Reposts: {build['reposts']} | Score: {build['score']}")
        print(f"   {build['url']}\n")
