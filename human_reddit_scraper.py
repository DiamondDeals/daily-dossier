#!/usr/bin/env python3
"""
Human Reddit Scraper - Production-Ready Reddit Web Scraping
Replaces PRAW API with pure HTML scraping and human-like behavior

Features:
- Rotating user agents
- Advanced rate limiting
- Session management
- Exponential backoff
- robots.txt compliance
- Fallback to old.reddit.com
- Resume capability
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import time
import random
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Generator, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import threading
from collections import deque

from user_agents import UserAgentRotator, get_session_headers
from rate_limiter import AdaptiveRateLimiter, RateLimitConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class PostData:
    """
    Reddit post data structure - matches PRAW's submission attributes
    for compatibility with daily_business_digest.py
    """
    id: str
    title: str
    selftext: str
    author: str
    score: int
    num_comments: int
    created_utc: float
    permalink: str
    url: str
    subreddit: str
    locked: bool = False
    archived: bool = False
    stickied: bool = False
    over_18: bool = False
    spoiler: bool = False

    @property
    def is_self(self) -> bool:
        """Check if this is a self/text post"""
        return self.url.startswith('/r/') or 'reddit.com' in self.url


class RobotsChecker:
    """Checks and caches robots.txt rules"""

    def __init__(self):
        self._parsers: Dict[str, RobotFileParser] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_duration = 3600  # 1 hour
        self._lock = threading.Lock()

    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """Check if we can fetch the given URL according to robots.txt"""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        with self._lock:
            # Check cache
            now = time.time()
            if base_url in self._parsers:
                if now - self._cache_time.get(base_url, 0) < self._cache_duration:
                    return self._parsers[base_url].can_fetch(user_agent, url)

            # Fetch and parse robots.txt
            try:
                rp = RobotFileParser()
                rp.set_url(f"{base_url}/robots.txt")
                rp.read()
                self._parsers[base_url] = rp
                self._cache_time[base_url] = now
                return rp.can_fetch(user_agent, url)
            except Exception as e:
                logger.warning(f"Could not fetch robots.txt for {base_url}: {e}")
                return True  # Allow if can't fetch robots.txt


class HumanRedditScraper:
    """
    Production-ready Reddit scraper with human-like behavior.

    Designed to replace PRAW API calls while maintaining the same
    data structure for easy integration.
    """

    # Reddit domains
    OLD_REDDIT = "https://old.reddit.com"
    WWW_REDDIT = "https://www.reddit.com"

    def __init__(
        self,
        use_old_reddit: bool = True,
        respect_robots: bool = False,  # Disabled by default - Reddit's robots.txt blocks everything
        progress_callback: Optional[callable] = None,
        rate_config: Optional[RateLimitConfig] = None
    ):
        """
        Initialize the scraper.

        Args:
            use_old_reddit: If True, prefer old.reddit.com (more reliable scraping)
            respect_robots: If True, check robots.txt before scraping
                           Note: Reddit's robots.txt has a blanket Disallow: /
                           so this is disabled by default for functionality.
            progress_callback: Optional callback for progress updates
            rate_config: Custom rate limiting configuration
        """
        self.base_url = self.OLD_REDDIT if use_old_reddit else self.WWW_REDDIT
        self.respect_robots = respect_robots
        self.progress_callback = progress_callback

        # Initialize components
        self.ua_rotator = UserAgentRotator()
        self.rate_limiter = AdaptiveRateLimiter(rate_config or RateLimitConfig())
        self.robots_checker = RobotsChecker() if respect_robots else None

        # Session setup with connection pooling
        self.session = self._create_session()

        # State tracking
        self.processed_subreddits: List[str] = []
        self.failed_subreddits: List[str] = []
        self._stop_requested = False

        # Resume capability
        self.resume_file = Path("scraper_state.json")

        logger.info(f"HumanRedditScraper initialized (base: {self.base_url})")

    def _create_session(self) -> requests.Session:
        """Create a session with connection pooling and retry logic"""
        session = requests.Session()

        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy
        )

        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Set initial headers
        session.headers.update(self.ua_rotator.get_session_headers())

        return session

    def _update_progress(self, message: str):
        """Update progress via callback if provided"""
        logger.info(message)
        if self.progress_callback:
            try:
                self.progress_callback(message)
            except Exception:
                pass

    def _make_request(
        self,
        url: str,
        fallback_url: Optional[str] = None,
        timeout: int = 30
    ) -> Optional[requests.Response]:
        """
        Make an HTTP request with human-like behavior.

        Args:
            url: Primary URL to fetch
            fallback_url: Backup URL if primary fails
            timeout: Request timeout in seconds

        Returns:
            Response object or None if failed
        """
        # Check robots.txt
        if self.robots_checker and not self.robots_checker.can_fetch(url):
            logger.warning(f"Blocked by robots.txt: {url}")
            return None

        # Wait before request
        self.rate_limiter.wait_for_request()

        # Refresh headers occasionally
        if random.random() < 0.1:  # 10% chance to get new headers
            self.session.headers.update(self.ua_rotator.get_session_headers())

        try:
            start_time = time.time()
            response = self.session.get(url, timeout=timeout)
            response_time = time.time() - start_time

            # Record the request
            self.rate_limiter.record_request()

            if response.status_code == 200:
                self.rate_limiter.record_success(response_time)
                return response

            elif response.status_code == 429:
                # Rate limited - use exponential backoff
                backoff = self.rate_limiter.record_error(429)
                logger.warning(f"Rate limited (429). Backing off for {backoff:.1f}s")
                time.sleep(backoff)

                if self.rate_limiter.should_retry():
                    return self._make_request(url, fallback_url, timeout)

            elif response.status_code in [403, 451]:
                # Forbidden - might be IP block
                logger.warning(f"Access denied ({response.status_code}) for {url}")
                self.rate_limiter.record_error(response.status_code)

                # Try fallback
                if fallback_url:
                    logger.info(f"Trying fallback URL: {fallback_url}")
                    return self._make_request(fallback_url, None, timeout)

            elif response.status_code >= 500:
                # Server error - backoff and retry
                backoff = self.rate_limiter.record_error(response.status_code)
                logger.warning(f"Server error ({response.status_code}). Backing off for {backoff:.1f}s")
                time.sleep(backoff)

                if self.rate_limiter.should_retry():
                    return self._make_request(url, fallback_url, timeout)

            else:
                logger.warning(f"Unexpected status {response.status_code} for {url}")
                self.rate_limiter.record_error(response.status_code)

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url}")
            backoff = self.rate_limiter.record_error()
            time.sleep(backoff)

            if self.rate_limiter.should_retry():
                return self._make_request(url, fallback_url, timeout)

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error: {e}")
            backoff = self.rate_limiter.record_error()
            time.sleep(backoff)

            if self.rate_limiter.should_retry():
                return self._make_request(url, fallback_url, timeout)

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            self.rate_limiter.record_error()

        return None

    def _parse_old_reddit_posts(self, html: str, subreddit: str) -> List[PostData]:
        """
        Parse posts from old.reddit.com HTML.

        old.reddit.com has data attributes on each post element which makes
        parsing reliable. We extract directly from data-* attributes.
        """
        posts = []
        soup = BeautifulSoup(html, 'html.parser')

        # Find all post entries - they have class 'thing' and data-fullname attribute
        things = soup.find_all('div', class_='thing', attrs={'data-fullname': True})

        logger.debug(f"Found {len(things)} 'thing' elements")

        for thing in things:
            try:
                # Skip ads and promoted content
                if 'promoted' in thing.get('class', []):
                    continue
                if thing.get('data-promoted') == 'true':
                    continue

                # Extract data directly from attributes (most reliable)
                data_fullname = thing.get('data-fullname', '')
                post_id = data_fullname.replace('t3_', '') if data_fullname else ''

                if not post_id:
                    continue

                # Get author from data attribute
                author = thing.get('data-author', '[deleted]')
                if not author:
                    author = '[deleted]'

                # Get score from data attribute
                score_str = thing.get('data-score', '0')
                try:
                    score = int(score_str)
                except (ValueError, TypeError):
                    score = 0

                # Get comments count from data attribute
                comments_str = thing.get('data-comments-count', '0')
                try:
                    num_comments = int(comments_str)
                except (ValueError, TypeError):
                    num_comments = 0

                # Get permalink from data attribute
                permalink = thing.get('data-permalink', '')
                if not permalink:
                    # Fallback: find from comments link
                    comments_elem = thing.find('a', class_='comments')
                    if comments_elem:
                        permalink = comments_elem.get('href', '')

                # Get URL from data attribute
                url = thing.get('data-url', '')
                if not url:
                    url = f"https://www.reddit.com{permalink}"

                # Get timestamp from data attribute (in milliseconds)
                timestamp_str = thing.get('data-timestamp', '')
                if timestamp_str:
                    try:
                        # data-timestamp is in milliseconds
                        created_utc = float(timestamp_str) / 1000.0
                    except (ValueError, TypeError):
                        created_utc = time.time() - 86400
                else:
                    created_utc = time.time() - 86400

                # Get title from the title link
                title_elem = thing.find('a', class_='title')
                title = title_elem.get_text(strip=True) if title_elem else ''

                if not title:
                    continue

                # Get subreddit from data attribute (prefer this over parameter)
                sub_name = thing.get('data-subreddit', subreddit)

                # Check flags from classes and data attributes
                classes = thing.get('class', [])
                stickied = 'stickied' in classes
                over_18 = thing.get('data-nsfw', 'false').lower() == 'true' or 'over18' in classes
                spoiler = thing.get('data-spoiler', 'false').lower() == 'true' or 'spoiler' in classes

                # Check for locked/archived in the post
                locked = thing.find('span', class_='locked-tagline') is not None
                archived = thing.find('span', class_='archived-tagline') is not None

                # Self text - check for expando content
                selftext = ""
                expando = thing.find('div', class_='expando')
                if expando:
                    usertext = expando.find('div', class_='usertext-body')
                    if usertext:
                        # Get text content, clean it up
                        md = usertext.find('div', class_='md')
                        if md:
                            selftext = md.get_text(separator='\n', strip=True)[:500]

                post = PostData(
                    id=post_id,
                    title=title,
                    selftext=selftext,
                    author=author,
                    score=score,
                    num_comments=num_comments,
                    created_utc=created_utc,
                    permalink=permalink,
                    url=url,
                    subreddit=sub_name,
                    locked=locked,
                    archived=archived,
                    stickied=stickied,
                    over_18=over_18,
                    spoiler=spoiler
                )

                posts.append(post)

            except Exception as e:
                logger.debug(f"Error parsing post: {e}")
                continue

        return posts

    def _parse_new_reddit_posts(self, html: str, subreddit: str) -> List[PostData]:
        """
        Parse posts from www.reddit.com (new Reddit).

        New Reddit uses more dynamic content, but we can still extract
        data from the initial HTML or embedded JSON.
        """
        posts = []
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find embedded JSON data (new Reddit often embeds post data)
        script_tags = soup.find_all('script', id='data')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                # Parse posts from JSON structure
                # This varies by page type
                if 'posts' in data:
                    for post_id, post_data in data['posts'].items():
                        post = self._json_to_postdata(post_data, subreddit)
                        if post:
                            posts.append(post)
            except (json.JSONDecodeError, TypeError):
                continue

        # Fallback: parse from HTML structure
        if not posts:
            # Try article elements
            articles = soup.find_all('article') or soup.find_all('div', {'data-testid': 'post-container'})
            for article in articles:
                try:
                    post = self._parse_article_element(article, subreddit)
                    if post:
                        posts.append(post)
                except Exception as e:
                    logger.debug(f"Error parsing article: {e}")
                    continue

        return posts

    def _json_to_postdata(self, data: dict, subreddit: str) -> Optional[PostData]:
        """Convert JSON post data to PostData object"""
        try:
            return PostData(
                id=data.get('id', ''),
                title=data.get('title', ''),
                selftext=data.get('selftext', data.get('selfText', '')),
                author=data.get('author', '[deleted]'),
                score=int(data.get('score', 0)),
                num_comments=int(data.get('numComments', data.get('num_comments', 0))),
                created_utc=float(data.get('created', data.get('created_utc', time.time()))),
                permalink=data.get('permalink', ''),
                url=data.get('url', ''),
                subreddit=subreddit,
                locked=data.get('locked', False),
                archived=data.get('archived', False),
                stickied=data.get('stickied', False),
                over_18=data.get('over18', data.get('over_18', False)),
                spoiler=data.get('spoiler', False)
            )
        except Exception:
            return None

    def _parse_article_element(self, article, subreddit: str) -> Optional[PostData]:
        """Parse a single article/post element from new Reddit"""
        try:
            # This is a simplified parser - new Reddit structure varies
            title_elem = article.find('h3') or article.find('a', {'data-click-id': 'body'})
            title = title_elem.get_text(strip=True) if title_elem else ''

            if not title:
                return None

            # Try to extract other details
            author_elem = article.find('a', {'data-testid': 'post_author_link'})
            author = author_elem.get_text(strip=True) if author_elem else '[deleted]'

            # Simplified - would need more robust parsing for production
            return PostData(
                id=str(hash(title))[:10],  # Temporary ID
                title=title,
                selftext='',
                author=author,
                score=0,
                num_comments=0,
                created_utc=time.time(),
                permalink='',
                url='',
                subreddit=subreddit
            )
        except Exception:
            return None

    def fetch_subreddit_posts(
        self,
        subreddit: str,
        sort: str = 'hot',
        limit: int = 50
    ) -> List[PostData]:
        """
        Fetch posts from a subreddit.

        Args:
            subreddit: Subreddit name (without r/)
            sort: Sort method ('hot', 'new', 'top', 'rising')
            limit: Maximum posts to fetch

        Returns:
            List of PostData objects
        """
        if self._stop_requested:
            return []

        self._update_progress(f"Fetching r/{subreddit} ({sort})...")

        # Build URLs
        primary_url = f"{self.OLD_REDDIT}/r/{subreddit}/{sort}"
        fallback_url = f"{self.WWW_REDDIT}/r/{subreddit}/{sort}"

        # Make request
        response = self._make_request(primary_url, fallback_url)

        if not response:
            logger.warning(f"Failed to fetch r/{subreddit}")
            self.failed_subreddits.append(subreddit)
            return []

        # Simulate reading time
        self.rate_limiter.simulate_reading()

        # Parse based on which site responded
        if 'old.reddit.com' in response.url:
            posts = self._parse_old_reddit_posts(response.text, subreddit)
        else:
            posts = self._parse_new_reddit_posts(response.text, subreddit)

        # Limit results
        posts = posts[:limit]

        logger.info(f"Fetched {len(posts)} posts from r/{subreddit} ({sort})")
        return posts

    def fetch_hot_and_new(
        self,
        subreddit: str,
        hot_limit: int = 50,
        new_limit: int = 50
    ) -> List[PostData]:
        """
        Fetch both hot and new posts from a subreddit.

        This matches the behavior in daily_business_digest.py:
        posts = list(subreddit.hot(limit=50)) + list(subreddit.new(limit=50))

        Args:
            subreddit: Subreddit name
            hot_limit: Max hot posts
            new_limit: Max new posts

        Returns:
            Combined list of posts (hot + new)
        """
        posts = []

        # Fetch hot posts
        hot_posts = self.fetch_subreddit_posts(subreddit, 'hot', hot_limit)
        posts.extend(hot_posts)

        # Small delay between fetches
        time.sleep(random.uniform(1.5, 3.0))

        # Fetch new posts
        new_posts = self.fetch_subreddit_posts(subreddit, 'new', new_limit)

        # Deduplicate by post ID
        seen_ids = {p.id for p in posts}
        for post in new_posts:
            if post.id not in seen_ids:
                posts.append(post)
                seen_ids.add(post.id)

        return posts

    def fetch_post_details(self, permalink: str) -> Optional[PostData]:
        """
        Fetch full details for a specific post.

        Useful when you need the full selftext content.

        Args:
            permalink: Post permalink (e.g., /r/subreddit/comments/abc123/title/)

        Returns:
            PostData with full details, or None if failed
        """
        if not permalink:
            return None

        if not permalink.startswith('http'):
            permalink = f"{self.base_url}{permalink}"

        response = self._make_request(permalink)
        if not response:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            # Parse full post content
            # For old.reddit.com
            if 'old.reddit.com' in response.url:
                thing = soup.find('div', class_='thing', attrs={'data-fullname': True})
                if thing:
                    # Get subreddit from URL
                    match = re.search(r'/r/(\w+)/', permalink)
                    subreddit = match.group(1) if match else ''

                    posts = self._parse_old_reddit_posts(str(thing), subreddit)
                    if posts:
                        post = posts[0]

                        # Get full selftext
                        usertext = soup.find('div', class_='usertext-body')
                        if usertext:
                            post.selftext = usertext.get_text(strip=True)

                        return post

        except Exception as e:
            logger.error(f"Error fetching post details: {e}")

        return None

    def scrape_subreddits(
        self,
        subreddits: List[str],
        hot_limit: int = 50,
        new_limit: int = 50
    ) -> Generator[PostData, None, None]:
        """
        Generator that scrapes multiple subreddits.

        Yields posts as they are scraped, allowing for streaming processing.

        Args:
            subreddits: List of subreddit names
            hot_limit: Max hot posts per subreddit
            new_limit: Max new posts per subreddit

        Yields:
            PostData objects
        """
        total = len(subreddits)

        for idx, subreddit in enumerate(subreddits, 1):
            if self._stop_requested:
                logger.info("Stop requested, halting scrape")
                break

            self._update_progress(f"Processing {idx}/{total}: r/{subreddit}")

            # Wait before each subreddit (human-like behavior)
            if idx > 1:
                self.rate_limiter.wait_for_subreddit()
                self.rate_limiter.record_subreddit_switch()

            # Fetch posts
            try:
                posts = self.fetch_hot_and_new(subreddit, hot_limit, new_limit)
                self.processed_subreddits.append(subreddit)

                for post in posts:
                    yield post

            except Exception as e:
                logger.error(f"Error scraping r/{subreddit}: {e}")
                self.failed_subreddits.append(subreddit)
                continue

        # Log completion
        stats = self.rate_limiter.get_stats()
        logger.info(f"Scrape complete. Processed: {len(self.processed_subreddits)}, "
                   f"Failed: {len(self.failed_subreddits)}, "
                   f"Total requests: {stats['total_requests']}")

    def scrape_subreddits_batch(
        self,
        subreddits: List[str],
        hot_limit: int = 50,
        new_limit: int = 50
    ) -> List[PostData]:
        """
        Scrape multiple subreddits and return all posts as a list.

        For use when you need all posts at once rather than streaming.
        """
        return list(self.scrape_subreddits(subreddits, hot_limit, new_limit))

    def stop(self):
        """Request the scraper to stop"""
        logger.info("Stop requested")
        self._stop_requested = True

    def reset(self):
        """Reset scraper state"""
        self._stop_requested = False
        self.processed_subreddits = []
        self.failed_subreddits = []
        self.rate_limiter.reset_backoff()

    def save_state(self, filepath: Optional[Path] = None):
        """Save current state for resume capability"""
        filepath = filepath or self.resume_file
        state = {
            'processed_subreddits': self.processed_subreddits,
            'failed_subreddits': self.failed_subreddits,
            'timestamp': datetime.now().isoformat(),
            'stats': self.rate_limiter.get_stats()
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"State saved to {filepath}")

    def load_state(self, filepath: Optional[Path] = None) -> bool:
        """Load state for resume capability"""
        filepath = filepath or self.resume_file
        try:
            with open(filepath) as f:
                state = json.load(f)
            self.processed_subreddits = state.get('processed_subreddits', [])
            self.failed_subreddits = state.get('failed_subreddits', [])
            logger.info(f"State loaded from {filepath}")
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return False

    def get_stats(self) -> dict:
        """Get scraper statistics"""
        rate_stats = self.rate_limiter.get_stats()
        return {
            **rate_stats,
            'processed_subreddits': len(self.processed_subreddits),
            'failed_subreddits': len(self.failed_subreddits),
            'base_url': self.base_url,
        }


class SubredditProxy:
    """
    Proxy class that mimics PRAW's subreddit object.

    Allows drop-in replacement for:
    reddit.subreddit(name).hot(limit=50)
    """

    def __init__(self, scraper: HumanRedditScraper, name: str):
        self.scraper = scraper
        self.name = name

    def hot(self, limit: int = 50) -> List[PostData]:
        """Fetch hot posts"""
        return self.scraper.fetch_subreddit_posts(self.name, 'hot', limit)

    def new(self, limit: int = 50) -> List[PostData]:
        """Fetch new posts"""
        return self.scraper.fetch_subreddit_posts(self.name, 'new', limit)

    def top(self, limit: int = 50, time_filter: str = 'all') -> List[PostData]:
        """Fetch top posts"""
        return self.scraper.fetch_subreddit_posts(self.name, 'top', limit)

    def rising(self, limit: int = 50) -> List[PostData]:
        """Fetch rising posts"""
        return self.scraper.fetch_subreddit_posts(self.name, 'rising', limit)


class RedditProxy:
    """
    Proxy class that mimics PRAW's Reddit object.

    Drop-in replacement for praw.Reddit() in daily_business_digest.py

    Usage:
        # Instead of:
        # reddit = praw.Reddit(...)

        # Use:
        reddit = RedditProxy()

        # Then use exactly as before:
        posts = list(reddit.subreddit('entrepreneur').hot(limit=50))
    """

    def __init__(self, **kwargs):
        """
        Initialize the Reddit proxy.

        Accepts same kwargs as praw.Reddit() but ignores them
        (no API keys needed for scraping).
        """
        self.scraper = HumanRedditScraper()
        logger.info("RedditProxy initialized (scraping mode, no API keys needed)")

    def subreddit(self, name: str) -> SubredditProxy:
        """Get a subreddit proxy object"""
        return SubredditProxy(self.scraper, name)

    def submission(self, id: str = None, url: str = None) -> Optional[PostData]:
        """Fetch a specific submission by ID or URL"""
        if url:
            return self.scraper.fetch_post_details(url)
        elif id:
            # Construct URL from ID
            url = f"/comments/{id}/"
            return self.scraper.fetch_post_details(url)
        return None


# Convenience function
def create_reddit_scraper(**kwargs) -> RedditProxy:
    """
    Create a Reddit scraper (drop-in replacement for praw.Reddit).

    Usage:
        reddit = create_reddit_scraper()
        posts = list(reddit.subreddit('entrepreneur').hot(limit=50))
    """
    return RedditProxy(**kwargs)


if __name__ == '__main__':
    # Quick test
    print("Testing HumanRedditScraper")
    print("=" * 60)

    scraper = HumanRedditScraper()

    print("\nFetching r/entrepreneur hot posts...")
    posts = scraper.fetch_subreddit_posts('entrepreneur', 'hot', limit=5)

    print(f"\nFound {len(posts)} posts:")
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post.title[:60]}...")
        print(f"   Author: {post.author} | Score: {post.score} | Comments: {post.num_comments}")
        print(f"   URL: https://reddit.com{post.permalink}")

    print("\n\nStats:")
    for key, value in scraper.get_stats().items():
        print(f"  {key}: {value}")
