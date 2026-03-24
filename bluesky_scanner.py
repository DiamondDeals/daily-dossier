#!/usr/bin/env python3
"""
Bluesky Scanner - Free public API, no auth needed
Replaces dead Nitter/Twitter scraping for builder content
Uses AT Protocol public endpoints (account feeds only - search API is blocked)
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


class BlueskyScanner:
    def __init__(self):
        self.base_url = "https://public.api.bsky.app"

        # Verified real accounts with meaningful follower counts
        # Each tuple: (handle, category)
        self.builder_accounts = [
            # AI / Tech
            ("emollick.bsky.social", "ai"),          # Ethan Mollick - AI researcher, 33k followers
            ("simonwillison.net", "ai"),              # Simon Willison - AI/LLM tools, 44k followers
            ("swyx.io", "ai"),                        # swyx - AI/dev, 8.7k followers
            ("caseynewton.bsky.social", "tech"),      # Casey Newton - tech journalist, 255k followers
            ("kottke.org", "tech"),                    # kottke.org - tech/culture, 30k followers
            ("om.co", "tech"),                        # Om Malik - tech/VC, 2.8k followers

            # Business / Entrepreneurs
            ("levels.io", "business"),                # Pieter Levels - indie maker, 10.8k followers
            ("jasonfried.bsky.social", "business"),   # Jason Fried - Basecamp, 4.7k followers
            ("sahilbloom.bsky.social", "business"),   # Sahil Bloom - business/growth, 11.5k followers
            ("codiesanchez.bsky.social", "business"), # Codie Sanchez - business, 995 followers
            ("gregisenberg.bsky.social", "business"), # Greg Isenberg - startups, 1.1k followers
            ("shl.bsky.social", "business"),          # Sahil Lavingia - Gumroad founder, 1.4k followers
            ("garyvee.com", "business"),              # Gary Vaynerchuk - marketing/business, 5.3k followers
            ("danshipper.bsky.social", "business"),   # Dan Shipper - Every.to, 3k followers
            ("balajis.bsky.social", "business"),      # Balaji Srinivasan - tech/crypto, 655 followers

            # Cybersecurity
            ("troyhunt.com", "cybersecurity"),        # Troy Hunt - Have I Been Pwned, 16k followers
            ("schneier.com", "cybersecurity"),        # Bruce Schneier - security expert, 1.1k followers

            # Major accounts (high-reach, diverse content)
            ("mcuban.bsky.social", "business"),       # Mark Cuban - investor/entrepreneur, 1.49M followers
            ("techcrunch.com", "tech"),               # TechCrunch - tech news, 209k followers
            ("wired.com", "tech"),                    # WIRED - tech/science, 406k followers
            ("theverge.com", "tech"),                 # The Verge - tech news, 296k followers
            ("arstechnica.com", "tech"),              # Ars Technica - tech deep dives, 114k followers

            # Science / Health
            ("neildegrassetyson.com", "science"),     # Neil deGrasse Tyson - science, 282k followers
            ("nature.com", "science"),                # Nature journal, 88k followers
            ("erictopol.bsky.social", "health"),      # Eric Topol - medicine/AI, 169k followers
            ("hubermanlab.com", "health"),            # Andrew Huberman - neuroscience/health, 3k followers
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
            "startup", "founder", "entrepreneur", "business",
            "ai", "llm", "gpt", "claude", "model", "agent",
            "security", "vulnerability", "breach", "hack",
            "cybersecurity", "privacy", "encryption"
        ]

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
        """Scan Bluesky for builder content from verified accounts"""
        print("  Scanning Bluesky for builder content...")

        all_builds = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=72)  # 3 days
        accounts_to_check = self.builder_accounts[:max_accounts]

        print(f"    Checking {len(accounts_to_check)} verified accounts...")
        success = 0
        failed = 0

        for handle, category in accounts_to_check:
            try:
                feed = self.get_author_feed(handle, limit=10)
                if not feed:
                    failed += 1
                    continue

                success += 1
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

                    # Accept posts with keyword match or decent engagement
                    if score >= 1 or parsed['engagement'] >= 5:
                        # Score: keyword relevance matters MORE than raw engagement
                        # A relevant AI/business post should beat a viral joke
                        # Keyword score * 50 so 3 keywords = 150 points
                        # Engagement capped at 100 so viral posts don't dominate
                        final_score = (score * 50) + min(parsed['engagement'], 100)

                        all_builds.append({
                            'username': parsed['handle'],
                            'display_name': parsed['author'],
                            'text': parsed['text'][:250],
                            'url': parsed['url'],
                            'likes': parsed['likes'],
                            'reposts': parsed['reposts'],
                            'replies': parsed['replies'],
                            'score': final_score,
                            'keywords': keywords[:5],
                            'category': category,
                            'source': 'account'
                        })

                time.sleep(0.3)
            except Exception:
                failed += 1
                continue

        # Deduplicate by URL
        seen_urls = set()
        unique_builds = []
        for build in all_builds:
            if build['url'] and build['url'] not in seen_urls:
                seen_urls.add(build['url'])
                unique_builds.append(build)

        # Sort by score
        unique_builds.sort(key=lambda x: x['score'], reverse=True)

        # Cap at 2 posts per author so no one dominates the feed
        author_counts = {}
        diverse_builds = []
        for build in unique_builds:
            author = build['username']
            author_counts[author] = author_counts.get(author, 0) + 1
            if author_counts[author] <= 2:
                diverse_builds.append(build)

        print(f"    Accounts: {success} OK, {failed} failed")
        print(f"    Found {len(diverse_builds)} builder updates (last 7 days, max 2/author)")
        return diverse_builds[:30]


if __name__ == "__main__":
    scanner = BlueskyScanner()
    builds = scanner.scan_builders(max_accounts=20)

    print(f"\nTop Builder Updates ({len(builds)}):\n")
    for i, build in enumerate(builds[:15], 1):
        print(f"{i}. @{build['username']} ({build['display_name']})")
        print(f"   {build['text'][:120]}...")
        print(f"   Likes: {build['likes']} | Reposts: {build['reposts']} | Score: {build['score']}")
        print(f"   {build['url']}\n")
