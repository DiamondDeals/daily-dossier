"""
Example Usage of Reddit API Integration
Demonstrates OAuth2 authentication, multi-account management, rate limiting,
content fetching, and business lead detection.
"""

import asyncio
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from reddit_api_client import RedditAPIClient, SearchQuery
from async_reddit_client import AsyncRedditAPIClient
from auth.reddit_auth import RedditAuthenticator
from config.reddit_config import get_config, reload_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_authentication():
    """Example: Authenticate Reddit accounts"""
    print("\n=== Reddit Authentication Example ===")
    
    try:
        authenticator = RedditAuthenticator()
        
        # Web OAuth flow (recommended for production)
        print("Starting web authentication flow...")
        token = authenticator.authenticate_web_flow(
            scopes=["read", "identity", "history", "mysubreddits"],
            auto_open_browser=True,
            timeout=300
        )
        
        print(f"Successfully authenticated: {token.username}")
        print(f"Token expires: {token.expires_at}")
        print(f"Scopes: {', '.join(token.scopes)}")
        
        # List stored users
        stored_users = authenticator.list_stored_users()
        print(f"Stored users: {stored_users}")
        
        return True
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return False


def example_basic_search():
    """Example: Basic Reddit search with business analysis"""
    print("\n=== Basic Search Example ===")
    
    try:
        config = get_config()
        client = RedditAPIClient(config)
        
        # Authenticate (assumes you have stored tokens)
        authenticator = RedditAuthenticator()
        stored_users = authenticator.list_stored_users()
        
        if not stored_users:
            print("No authenticated users found. Please run authentication example first.")
            return
        
        # Use first stored user
        if not client.authenticate_user(stored_users[0], use_web_flow=False):
            print("Failed to authenticate user")
            return
        
        # Create search query
        query = SearchQuery(
            query="manual data entry automation",
            subreddits=["entrepreneur", "smallbusiness", "productivity", "excel"],
            sort="top",
            time_filter="month",
            limit=25,
            min_score=5,
            include_nsfw=False
        )
        
        print(f"Searching for: '{query.query}'")
        print(f"In subreddits: {', '.join(query.subreddits)}")
        
        # Perform search
        def progress_callback(current, total):
            print(f"Progress: {current}/{total} subreddits searched")
        
        posts = client.search_posts(query, progress_callback)
        
        # Display results
        print(f"\nFound {len(posts)} posts")
        
        # Show top 5 business opportunities
        top_posts = sorted(posts, key=lambda x: x.business_score, reverse=True)[:5]
        
        for i, post in enumerate(top_posts, 1):
            print(f"\n{i}. Business Score: {post.business_score:.2f}")
            print(f"   Title: {post.title}")
            print(f"   Subreddit: r/{post.subreddit}")
            print(f"   Score: {post.score} | Comments: {post.num_comments}")
            print(f"   Urgency: {post.urgency_level} | Value: {post.potential_value}")
            print(f"   Problem Indicators: {', '.join(post.problem_indicators[:3])}")
            print(f"   URL: {post.permalink}")
        
        # Export results
        if posts:
            csv_file = client.export_results(posts, "business_leads", "csv")
            json_file = client.export_results(posts, "business_leads", "json")
            md_file = client.export_results(posts, "business_leads", "markdown")
            
            print(f"\nResults exported to:")
            print(f"  CSV: {csv_file}")
            print(f"  JSON: {json_file}")
            print(f"  Markdown: {md_file}")
        
        # Show statistics
        stats = client.get_account_stats()
        print(f"\nAPI Statistics:")
        print(f"  Requests made: {stats['api_stats']['requests_made']}")
        print(f"  Posts analyzed: {stats['api_stats']['posts_analyzed']}")
        print(f"  Business leads found: {stats['api_stats']['business_leads_found']}")
        print(f"  Error rate: {stats['api_stats']['errors']}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return False


async def example_async_concurrent_search():
    """Example: Async concurrent search across multiple queries"""
    print("\n=== Async Concurrent Search Example ===")
    
    try:
        config = get_config()
        
        async with AsyncRedditAPIClient(config) as client:
            # Authenticate users (assumes you have stored tokens)
            authenticator = RedditAuthenticator()
            stored_users = authenticator.list_stored_users()
            
            if not stored_users:
                print("No authenticated users found. Please run authentication example first.")
                return
            
            # Add multiple accounts for load balancing
            for username in stored_users[:3]:  # Use up to 3 accounts
                success = await client.authenticate_user(username)
                if success:
                    print(f"Added account: {username}")
            
            # Create multiple search queries
            queries = [
                SearchQuery(
                    query="manual data entry",
                    subreddits=["excel", "productivity"],
                    limit=20,
                    min_score=3
                ),
                SearchQuery(
                    query="repetitive tasks automation",
                    subreddits=["entrepreneur", "smallbusiness"],
                    limit=20,
                    min_score=5
                ),
                SearchQuery(
                    query="workflow bottleneck",
                    subreddits=["sysadmin", "workflow"],
                    limit=15,
                    min_score=2
                ),
                SearchQuery(
                    query="time consuming process",
                    subreddits=["productivity", "freelance"],
                    limit=15,
                    min_score=3
                )
            ]
            
            print(f"Starting concurrent search with {len(queries)} queries...")
            
            # Progress tracking
            def progress_callback(completed, total):
                print(f"Queries completed: {completed}/{total}")
            
            # Perform concurrent searches
            start_time = datetime.now()
            results = await client.search_posts_concurrent(queries, progress_callback)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            print(f"Concurrent search completed in {duration:.2f} seconds")
            
            # Process results
            all_posts = []
            for query_name, posts in results.items():
                print(f"\nQuery '{query_name}': {len(posts)} posts found")
                
                if posts:
                    top_post = max(posts, key=lambda x: x.business_score)
                    print(f"  Top result: {top_post.title} (Score: {top_post.business_score:.2f})")
                
                all_posts.extend(posts)
            
            # Show overall statistics
            if all_posts:
                total_posts = len(all_posts)
                high_value_posts = [p for p in all_posts if p.business_score > 3.0]
                
                print(f"\nOverall Results:")
                print(f"  Total posts analyzed: {total_posts}")
                print(f"  High-value leads (score > 3.0): {len(high_value_posts)}")
                print(f"  Average business score: {sum(p.business_score for p in all_posts) / total_posts:.2f}")
                
                # Export combined results
                export_file = await client.export_results_async(
                    all_posts, 
                    "async_concurrent_search",
                    "json"
                )
                print(f"  Results exported to: {export_file}")
            
            # Performance statistics
            perf_stats = await client.get_performance_stats()
            print(f"\nPerformance Statistics:")
            print(f"  Requests per second: {perf_stats['requests_per_second']:.2f}")
            print(f"  Posts per second: {perf_stats['posts_per_second']:.2f}")
            print(f"  Concurrent requests peak: {perf_stats['concurrent_requests']}")
            print(f"  Error rate: {perf_stats['error_rate']:.2%}")
        
        return True
        
    except Exception as e:
        logger.error(f"Async search failed: {e}")
        return False


async def example_real_time_monitoring():
    """Example: Real-time monitoring of new posts"""
    print("\n=== Real-time Monitoring Example ===")
    
    try:
        config = get_config()
        
        async with AsyncRedditAPIClient(config) as client:
            # Authenticate
            authenticator = RedditAuthenticator()
            stored_users = authenticator.list_stored_users()
            
            if stored_users:
                await client.authenticate_user(stored_users[0])
            
            # Monitor specific subreddits for business opportunities
            query = SearchQuery(
                query="automation OR workflow OR manual",
                subreddits=["entrepreneur", "smallbusiness", "productivity"],
                sort="new",
                limit=50
            )
            
            print("Starting real-time monitoring...")
            print("Watching for new business opportunities...")
            
            processed_ids = set()
            high_value_posts = []
            
            # Stream new posts
            async for post in client.stream_search_results(query):
                # Avoid duplicates
                if post.id in processed_ids:
                    continue
                processed_ids.add(post.id)
                
                # Only show high-value opportunities
                if post.business_score > 2.0:
                    print(f"\n🔥 HIGH-VALUE OPPORTUNITY DETECTED!")
                    print(f"Score: {post.business_score:.2f} | Urgency: {post.urgency_level}")
                    print(f"Title: {post.title}")
                    print(f"Subreddit: r/{post.subreddit}")
                    print(f"Problem indicators: {', '.join(post.problem_indicators[:2])}")
                    print(f"URL: {post.permalink}")
                    
                    high_value_posts.append(post)
                    
                    # Stop after finding 5 high-value opportunities
                    if len(high_value_posts) >= 5:
                        print("\nFound 5 high-value opportunities. Stopping monitoring.")
                        break
                
                # Show progress for all posts
                print(f".", end="", flush=True)
            
            # Summary
            if high_value_posts:
                print(f"\n\nMonitoring Summary:")
                print(f"High-value opportunities found: {len(high_value_posts)}")
                
                avg_score = sum(p.business_score for p in high_value_posts) / len(high_value_posts)
                print(f"Average business score: {avg_score:.2f}")
                
                # Export opportunities
                export_file = await client.export_results_async(
                    high_value_posts,
                    "real_time_opportunities",
                    "json"
                )
                print(f"Opportunities exported to: {export_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Real-time monitoring failed: {e}")
        return False


def example_multi_account_management():
    """Example: Multi-account management and load balancing"""
    print("\n=== Multi-Account Management Example ===")
    
    try:
        authenticator = RedditAuthenticator()
        config = get_config()
        client = RedditAPIClient(config)
        
        # List available accounts
        stored_users = authenticator.list_stored_users()
        print(f"Available accounts: {stored_users}")
        
        if len(stored_users) < 2:
            print("Need at least 2 authenticated accounts for this example")
            return False
        
        # Add multiple accounts
        for username in stored_users:
            success = client.account_manager.add_account(username)
            print(f"Added account {username}: {'✓' if success else '✗'}")
        
        # Show account statistics
        print(f"\nActive accounts: {len(client.account_manager.active_accounts)}")
        print(f"Current account: {client.account_manager.current_account}")
        
        # Demonstrate account switching
        for username in stored_users[:3]:
            if client.account_manager.switch_account(username):
                print(f"Switched to account: {username}")
                
                # Make a test request to show load distribution
                query = SearchQuery(query="test automation", limit=5)
                posts = client.search_posts(query)
                print(f"  Found {len(posts)} posts")
        
        # Show usage statistics
        stats = client.get_account_stats()
        print(f"\nAccount Statistics:")
        for username, account_stats in stats['account_stats'].items():
            print(f"  {username}:")
            print(f"    Requests: {account_stats['requests_made']}")
            print(f"    Errors: {account_stats['errors']}")
            print(f"    Last used: {account_stats['last_used']}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Multi-account management failed: {e}")
        return False


def example_advanced_business_analysis():
    """Example: Advanced business opportunity analysis"""
    print("\n=== Advanced Business Analysis Example ===")
    
    try:
        config = get_config()
        client = RedditAPIClient(config)
        
        # Authenticate
        authenticator = RedditAuthenticator()
        stored_users = authenticator.list_stored_users()
        
        if stored_users:
            client.authenticate_user(stored_users[0], use_web_flow=False)
        
        # Search for comprehensive business problems
        query = SearchQuery(
            query="manual OR repetitive OR time-consuming OR bottleneck OR automate",
            subreddits=["entrepreneur", "smallbusiness", "productivity", "excel", "workflow"],
            sort="top",
            time_filter="week",
            limit=100,
            min_score=10
        )
        
        print("Performing comprehensive business analysis...")
        posts = client.search_posts(query)
        
        if not posts:
            print("No posts found")
            return False
        
        # Advanced analysis
        print(f"\nAnalyzing {len(posts)} posts...")
        
        # Categorize by urgency
        urgency_counts = {"high": 0, "medium": 0, "low": 0}
        value_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
        
        for post in posts:
            urgency_counts[post.urgency_level] += 1
            value_counts[post.potential_value] += 1
        
        print(f"\nUrgency Distribution:")
        for level, count in urgency_counts.items():
            percentage = (count / len(posts)) * 100
            print(f"  {level.capitalize()}: {count} ({percentage:.1f}%)")
        
        print(f"\nValue Distribution:")
        for level, count in value_counts.items():
            percentage = (count / len(posts)) * 100
            print(f"  {level.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Top opportunities by different criteria
        print(f"\n=== TOP OPPORTUNITIES ===")
        
        # Highest business score
        top_score = sorted(posts, key=lambda x: x.business_score, reverse=True)[:3]
        print(f"\nHighest Business Score:")
        for i, post in enumerate(top_score, 1):
            print(f"  {i}. {post.title[:60]}...")
            print(f"     Score: {post.business_score:.2f} | r/{post.subreddit}")
        
        # Most urgent
        urgent_posts = [p for p in posts if p.urgency_level == "high"]
        if urgent_posts:
            top_urgent = sorted(urgent_posts, key=lambda x: x.business_score, reverse=True)[:3]
            print(f"\nMost Urgent Opportunities:")
            for i, post in enumerate(top_urgent, 1):
                print(f"  {i}. {post.title[:60]}...")
                print(f"     Score: {post.business_score:.2f} | r/{post.subreddit}")
        
        # High-value potential
        high_value_posts = [p for p in posts if p.potential_value == "high"]
        if high_value_posts:
            top_value = sorted(high_value_posts, key=lambda x: x.business_score, reverse=True)[:3]
            print(f"\nHighest Value Potential:")
            for i, post in enumerate(top_value, 1):
                print(f"  {i}. {post.title[:60]}...")
                print(f"     Score: {post.business_score:.2f} | r/{post.subreddit}")
        
        # Keyword analysis
        all_keywords = []
        for post in posts:
            all_keywords.extend(post.problem_indicators)
        
        if all_keywords:
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            print(f"\nTop Problem Indicators:")
            for keyword, count in keyword_counts.most_common(10):
                print(f"  {keyword}: {count} occurrences")
        
        # Export detailed analysis
        csv_file = client.export_results(posts, "advanced_business_analysis", "csv")
        json_file = client.export_results(posts, "advanced_business_analysis", "json")
        
        print(f"\nDetailed analysis exported to:")
        print(f"  CSV: {csv_file}")
        print(f"  JSON: {json_file}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Advanced analysis failed: {e}")
        return False


async def main():
    """Main example runner"""
    print("Reddit API Integration - Complete Example Suite")
    print("=" * 50)
    
    examples = [
        ("Authentication", example_authentication),
        ("Basic Search", example_basic_search),
        ("Async Concurrent Search", example_async_concurrent_search),
        ("Real-time Monitoring", example_real_time_monitoring),
        ("Multi-Account Management", example_multi_account_management),
        ("Advanced Business Analysis", example_advanced_business_analysis)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    try:
        choice = input("\nEnter example number (1-6) or 'all' to run all: ").strip().lower()
        
        if choice == 'all':
            for name, func in examples:
                print(f"\n{'='*20} {name} {'='*20}")
                if asyncio.iscoroutinefunction(func):
                    success = await func()
                else:
                    success = func()
                
                if success:
                    print(f"✓ {name} completed successfully")
                else:
                    print(f"✗ {name} failed")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            idx = int(choice) - 1
            name, func = examples[idx]
            
            print(f"\n{'='*20} {name} {'='*20}")
            if asyncio.iscoroutinefunction(func):
                success = await func()
            else:
                success = func()
            
            if success:
                print(f"✓ {name} completed successfully")
            else:
                print(f"✗ {name} failed")
        
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\nExample interrupted by user")
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())