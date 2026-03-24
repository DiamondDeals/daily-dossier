#!/usr/bin/env python3
"""
Test Script for Human Reddit Scraper
Tests the scraper against r/entrepreneur to verify functionality

Run: python test_scraper.py
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from human_reddit_scraper import HumanRedditScraper, RedditProxy, PostData
from user_agents import UserAgentRotator
from rate_limiter import AdaptiveRateLimiter


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_post(post: PostData, index: int = 1):
    """Print formatted post information"""
    print(f"\n{index}. {post.title[:65]}{'...' if len(post.title) > 65 else ''}")
    print(f"   Author: u/{post.author}")
    print(f"   Score: {post.score} | Comments: {post.num_comments}")
    print(f"   Created: {datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M')}")
    print(f"   Stickied: {post.stickied} | Locked: {post.locked} | Archived: {post.archived}")
    print(f"   URL: https://reddit.com{post.permalink[:50]}...")
    if post.selftext:
        preview = post.selftext[:100].replace('\n', ' ')
        print(f"   Preview: {preview}...")


def test_user_agents():
    """Test user agent rotation"""
    print_header("TEST 1: User Agent Rotation")

    rotator = UserAgentRotator()

    print("\n3 Random User Agents:")
    for i in range(3):
        headers = rotator.get_random_profile()
        ua = headers['User-Agent']
        # Determine browser type
        if 'Firefox' in ua:
            browser = 'Firefox'
        elif 'Chrome' in ua and 'Edg' in ua:
            browser = 'Edge'
        elif 'Safari' in ua and 'Chrome' not in ua:
            browser = 'Safari'
        else:
            browser = 'Chrome'
        print(f"  {i+1}. [{browser}] {ua[:70]}...")

    print("\nSession Headers (should be consistent):")
    for i in range(2):
        headers = rotator.get_session_headers()
        print(f"  {i+1}. {headers['User-Agent'][:70]}...")

    print("\n✓ User agent rotation working")
    return True


def test_rate_limiter():
    """Test rate limiting functionality"""
    print_header("TEST 2: Rate Limiter")

    limiter = AdaptiveRateLimiter()

    print("\nTesting delay calculations:")
    for i in range(3):
        delay = limiter.get_request_delay()
        print(f"  Request {i+1}: delay = {delay:.2f}s")
        limiter.record_request()
        time.sleep(0.1)  # Small delay for testing

    print("\nTesting backoff on error:")
    backoff = limiter.record_error(429)
    print(f"  429 error: backoff = {backoff:.2f}s, throttled = {limiter.state.is_throttled}")

    limiter.reset_backoff()
    print(f"  After reset: backoff = {limiter.state.current_backoff:.2f}s")

    print("\nStatistics:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Rate limiter working")
    return True


def test_scraper_basic():
    """Test basic scraper functionality"""
    print_header("TEST 3: Basic Scraper - r/entrepreneur")

    scraper = HumanRedditScraper()

    print("\nFetching 5 HOT posts from r/entrepreneur...")
    start_time = time.time()

    posts = scraper.fetch_subreddit_posts('entrepreneur', 'hot', limit=5)

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds")

    if not posts:
        print("\n✗ No posts retrieved!")
        return False

    print(f"\nRetrieved {len(posts)} posts:")
    for i, post in enumerate(posts, 1):
        print_post(post, i)

    print("\n✓ Basic scraper test passed")
    return True


def test_scraper_new():
    """Test fetching new posts"""
    print_header("TEST 4: New Posts - r/entrepreneur")

    scraper = HumanRedditScraper()

    print("\nFetching 3 NEW posts from r/entrepreneur...")
    posts = scraper.fetch_subreddit_posts('entrepreneur', 'new', limit=3)

    if not posts:
        print("\n✗ No new posts retrieved!")
        return False

    print(f"\nRetrieved {len(posts)} new posts:")
    for i, post in enumerate(posts, 1):
        print_post(post, i)

    print("\n✓ New posts test passed")
    return True


def test_hot_and_new():
    """Test combined hot and new fetch"""
    print_header("TEST 5: Combined Hot + New")

    scraper = HumanRedditScraper()

    print("\nFetching hot and new posts from r/smallbusiness...")
    posts = scraper.fetch_hot_and_new('smallbusiness', hot_limit=3, new_limit=3)

    if not posts:
        print("\n✗ No posts retrieved!")
        return False

    print(f"\nRetrieved {len(posts)} total posts (deduplicated):")
    for i, post in enumerate(posts[:5], 1):
        print_post(post, i)

    print("\n✓ Hot + New test passed")
    return True


def test_reddit_proxy():
    """Test PRAW-compatible proxy interface"""
    print_header("TEST 6: PRAW-Compatible Proxy")

    print("\nCreating RedditProxy (drop-in replacement for praw.Reddit)...")
    reddit = RedditProxy()

    print("\nUsing PRAW-style API: reddit.subreddit('entrepreneur').hot(limit=3)")
    posts = list(reddit.subreddit('entrepreneur').hot(limit=3))

    if not posts:
        print("\n✗ No posts via proxy!")
        return False

    print(f"\nRetrieved {len(posts)} posts via proxy:")
    for i, post in enumerate(posts, 1):
        print_post(post, i)

    print("\n✓ PRAW proxy test passed")
    return True


def test_multiple_subreddits():
    """Test scraping multiple subreddits"""
    print_header("TEST 7: Multiple Subreddits")

    scraper = HumanRedditScraper()

    subreddits = ['freelance', 'productivity']  # Small list for testing

    print(f"\nScraping {len(subreddits)} subreddits...")
    print(f"Subreddits: {', '.join(subreddits)}")

    all_posts = []
    for post in scraper.scrape_subreddits(subreddits, hot_limit=2, new_limit=2):
        all_posts.append(post)
        if len(all_posts) <= 6:
            print(f"\n  [{post.subreddit}] {post.title[:50]}...")

    if not all_posts:
        print("\n✗ No posts from multiple subreddits!")
        return False

    print(f"\n\nTotal posts: {len(all_posts)}")
    print(f"Processed subreddits: {scraper.processed_subreddits}")
    print(f"Failed subreddits: {scraper.failed_subreddits}")

    print("\n✓ Multiple subreddits test passed")
    return True


def test_error_handling():
    """Test error handling for non-existent subreddit"""
    print_header("TEST 8: Error Handling")

    scraper = HumanRedditScraper()

    print("\nTesting fetch of non-existent subreddit...")
    posts = scraper.fetch_subreddit_posts('thisdoesnotexist12345xyz', 'hot', limit=5)

    print(f"Posts returned: {len(posts) if posts else 0}")
    print(f"Failed subreddits: {scraper.failed_subreddits}")

    print("\n✓ Error handling test passed")
    return True


def test_data_structure():
    """Test that data structure matches PRAW expectations"""
    print_header("TEST 9: Data Structure Compatibility")

    scraper = HumanRedditScraper()
    posts = scraper.fetch_subreddit_posts('entrepreneur', 'hot', limit=1)

    if not posts:
        print("\n✗ No posts to test!")
        return False

    post = posts[0]

    print("\nChecking PRAW-compatible attributes:")
    required_attrs = [
        'id', 'title', 'selftext', 'author', 'score',
        'num_comments', 'created_utc', 'permalink',
        'locked', 'archived', 'stickied'
    ]

    all_present = True
    for attr in required_attrs:
        has_attr = hasattr(post, attr)
        value = getattr(post, attr, 'N/A')
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + '...'
        status = "✓" if has_attr else "✗"
        print(f"  {status} {attr}: {value}")
        if not has_attr:
            all_present = False

    if all_present:
        print("\n✓ All required attributes present")
        return True
    else:
        print("\n✗ Missing some required attributes!")
        return False


def test_scraper_stats():
    """Test scraper statistics"""
    print_header("TEST 10: Scraper Statistics")

    scraper = HumanRedditScraper()

    # Do a few requests
    scraper.fetch_subreddit_posts('entrepreneur', 'hot', limit=2)

    print("\nScraper Statistics:")
    stats = scraper.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Statistics test passed")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  HUMAN REDDIT SCRAPER - TEST SUITE")
    print("=" * 70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    tests = [
        ("User Agent Rotation", test_user_agents),
        ("Rate Limiter", test_rate_limiter),
        ("Basic Scraper", test_scraper_basic),
        ("New Posts", test_scraper_new),
        ("Hot + New Combined", test_hot_and_new),
        ("PRAW Proxy", test_reddit_proxy),
        ("Multiple Subreddits", test_multiple_subreddits),
        ("Error Handling", test_error_handling),
        ("Data Structure", test_data_structure),
        ("Statistics", test_scraper_stats),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' failed with exception: {e}")
            results.append((name, False))

        # Delay between tests
        time.sleep(2)

    # Summary
    print_header("TEST RESULTS SUMMARY")

    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {name}")

    print(f"\n  Total: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED!")
    else:
        print(f"\n  ⚠️  {failed} test(s) failed")

    return failed == 0


def run_quick_test():
    """Run a quick single test"""
    print("\n" + "=" * 70)
    print("  QUICK TEST - r/entrepreneur")
    print("=" * 70)

    scraper = HumanRedditScraper()

    print("\nFetching hot posts...")
    posts = scraper.fetch_subreddit_posts('entrepreneur', 'hot', limit=10)

    if posts:
        print(f"\n✓ Successfully fetched {len(posts)} posts")
        print("\nSample posts:")
        for i, post in enumerate(posts[:3], 1):
            print_post(post, i)

        print("\n\nStats:")
        for key, value in scraper.get_stats().items():
            print(f"  {key}: {value}")

        return True
    else:
        print("\n✗ Failed to fetch posts")
        return False


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test Human Reddit Scraper')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick single test only')
    parser.add_argument('--full', '-f', action='store_true',
                       help='Run full test suite')
    args = parser.parse_args()

    if args.quick or (not args.full):
        # Default to quick test
        success = run_quick_test()
    else:
        # Full test suite
        success = run_all_tests()

    sys.exit(0 if success else 1)
