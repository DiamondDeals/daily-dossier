"""
Async Reddit API Client
High-performance asynchronous Reddit API client for concurrent operations
"""

import asyncio
import asyncpraw
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Any, AsyncIterator, Callable, Tuple
from datetime import datetime, timedelta
import json
import logging
import time
from pathlib import Path
import structlog
from contextlib import asynccontextmanager
from dataclasses import asdict
import backoff
from collections import defaultdict

from reddit_api_client import PostData, CommentData, SearchQuery, BusinessLogicEngine
from auth.reddit_auth import RedditAuthenticator, AuthToken
from config.reddit_config import get_config, RedditConfig

class AsyncRateLimiter:
    """Async rate limiter with token bucket algorithm"""
    
    def __init__(self, config: RedditConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Token bucket parameters
        self.max_tokens = config.api_limits.burst_limit
        self.refill_rate = config.api_limits.requests_per_minute / 60  # tokens per second
        self.tokens = self.max_tokens
        self.last_refill = time.time()
        
        # Async locks
        self._lock = asyncio.Lock()
        
        # Backoff tracking
        self.backoff_until: Optional[datetime] = None
        self.consecutive_429s = 0
    
    async def acquire(self) -> None:
        """Acquire a token for API request"""
        async with self._lock:
            now = time.time()
            
            # Check if in backoff period
            if self.backoff_until and datetime.now() < self.backoff_until:
                wait_time = (self.backoff_until - datetime.now()).total_seconds()
                self.logger.info(f"Rate limited: waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.backoff_until = None
            
            # Refill tokens
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.refill_rate
                self.logger.info(f"No tokens available: waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.tokens = 1
            
            # Consume token
            self.tokens -= 1
    
    async def record_rate_limit(self, retry_after: Optional[int] = None) -> None:
        """Record a rate limit response"""
        async with self._lock:
            self.consecutive_429s += 1
            
            if retry_after:
                self.backoff_until = datetime.now() + timedelta(seconds=retry_after)
            else:
                backoff_seconds = min(
                    300,
                    self.config.api_limits.cooldown_seconds * 
                    (self.config.api_limits.backoff_factor ** self.consecutive_429s)
                )
                self.backoff_until = datetime.now() + timedelta(seconds=backoff_seconds)
            
            self.logger.warning(
                "Async rate limited",
                consecutive_429s=self.consecutive_429s,
                backoff_until=self.backoff_until.isoformat()
            )

class AsyncMultiAccountManager:
    """Async multi-account management with load balancing"""
    
    def __init__(self, authenticator: RedditAuthenticator):
        self.authenticator = authenticator
        self.active_accounts: Dict[str, asyncpraw.Reddit] = {}
        self.rate_limiters: Dict[str, AsyncRateLimiter] = {}
        self.account_stats: Dict[str, Dict] = defaultdict(lambda: {
            'requests_made': 0,
            'last_used': None,
            'rate_limited': False,
            'errors': 0
        })
        self.logger = structlog.get_logger(__name__)
        self._lock = asyncio.Lock()
    
    async def add_account(self, username: str, force_refresh: bool = False) -> bool:
        """Add account to async manager"""
        try:
            token = self.authenticator.load_token(username)
            if not token:
                self.logger.error(f"No token found for user: {username}")
                return False
            
            if force_refresh or not self.authenticator.validate_token(token):
                if token.refresh_token:
                    token = self.authenticator.refresh_token(token)
                else:
                    self.logger.error(f"Invalid token for user {username}")
                    return False
            
            # Create async Reddit instance
            config = get_config()
            if token.access_token == "password_flow":
                reddit = asyncpraw.Reddit(
                    client_id=config.credentials.client_id,
                    client_secret=config.credentials.client_secret,
                    username=username,
                    password="",  # We don't store passwords
                    user_agent=config.credentials.user_agent
                )
            else:
                reddit = asyncpraw.Reddit(
                    client_id=config.credentials.client_id,
                    client_secret=config.credentials.client_secret,
                    refresh_token=token.refresh_token,
                    user_agent=config.credentials.user_agent
                )
            
            # Test connection
            user = await reddit.user.me()
            
            async with self._lock:
                self.active_accounts[username] = reddit
                self.rate_limiters[username] = AsyncRateLimiter(config)
            
            self.logger.info(f"Added async account: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add async account {username}: {e}")
            return False
    
    async def get_best_account(self) -> Tuple[str, asyncpraw.Reddit, AsyncRateLimiter]:
        """Get the best available account for requests"""
        async with self._lock:
            if not self.active_accounts:
                raise ValueError("No active accounts available")
            
            # Find account with least recent usage and not rate limited
            best_account = None
            best_score = float('inf')
            
            for username, reddit in self.active_accounts.items():
                stats = self.account_stats[username]
                rate_limiter = self.rate_limiters[username]
                
                # Skip if rate limited
                if (rate_limiter.backoff_until and 
                    datetime.now() < rate_limiter.backoff_until):
                    continue
                
                # Calculate score (lower is better)
                score = stats['requests_made']
                if stats['last_used']:
                    time_since_use = (datetime.now() - stats['last_used']).total_seconds()
                    score = score * max(0.1, 1 - time_since_use / 3600)  # Favor recently unused accounts
                
                if score < best_score:
                    best_score = score
                    best_account = username
            
            if not best_account:
                # All accounts are rate limited, use the one with earliest recovery
                earliest_recovery = None
                for username, rate_limiter in self.rate_limiters.items():
                    if (rate_limiter.backoff_until and 
                        (earliest_recovery is None or rate_limiter.backoff_until < earliest_recovery)):
                        earliest_recovery = rate_limiter.backoff_until
                        best_account = username
            
            if not best_account:
                best_account = list(self.active_accounts.keys())[0]
            
            return (
                best_account,
                self.active_accounts[best_account],
                self.rate_limiters[best_account]
            )
    
    async def record_request(self, username: str) -> None:
        """Record API request for account"""
        self.account_stats[username]['requests_made'] += 1
        self.account_stats[username]['last_used'] = datetime.now()
    
    async def record_error(self, username: str) -> None:
        """Record error for account"""
        self.account_stats[username]['errors'] += 1
    
    async def close_all(self) -> None:
        """Close all Reddit instances"""
        for reddit in self.active_accounts.values():
            await reddit.close()

class AsyncRedditAPIClient:
    """High-performance async Reddit API client"""
    
    def __init__(self, config: Optional[RedditConfig] = None):
        self.config = config or get_config()
        self.authenticator = RedditAuthenticator()
        self.account_manager = AsyncMultiAccountManager(self.authenticator)
        self.business_logic = BusinessLogicEngine()
        self.logger = structlog.get_logger(__name__)
        
        # Connection management
        self.session: Optional[aiohttp.ClientSession] = None
        self.max_concurrent = self.config.app_settings['max_concurrent_requests']
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'posts_analyzed': 0,
            'business_leads_found': 0,
            'errors': 0,
            'concurrent_requests': 0,
            'start_time': datetime.now()
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self) -> None:
        """Initialize async client"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.app_settings['request_timeout_seconds']),
            connector=aiohttp.TCPConnector(limit=100)
        )
        self.logger.info("Async Reddit client initialized")
    
    async def authenticate_user(self, username: str) -> bool:
        """Authenticate user account"""
        return await self.account_manager.add_account(username)
    
    async def search_posts_concurrent(
        self,
        queries: List[SearchQuery],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, List[PostData]]:
        """Search multiple queries concurrently"""
        tasks = []
        
        for query in queries:
            task = asyncio.create_task(
                self._search_single_query(query),
                name=f"search_{query.query[:20]}"
            )
            tasks.append((query.query, task))
        
        results = {}
        completed = 0
        
        for query_name, task in tasks:
            try:
                posts = await task
                results[query_name] = posts
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(queries))
                    
            except Exception as e:
                self.logger.error(f"Query '{query_name}' failed: {e}")
                results[query_name] = []
                self.stats['errors'] += 1
        
        return results
    
    async def _search_single_query(self, query: SearchQuery) -> List[PostData]:
        """Search for posts with a single query"""
        async with self.semaphore:
            self.stats['concurrent_requests'] += 1
            
            try:
                username, reddit, rate_limiter = await self.account_manager.get_best_account()
                
                await rate_limiter.acquire()
                
                all_posts = []
                
                if query.subreddits:
                    # Search specific subreddits
                    tasks = []
                    for subreddit_name in query.subreddits:
                        task = asyncio.create_task(
                            self._search_subreddit_async(reddit, subreddit_name, query, username, rate_limiter)
                        )
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, Exception):
                            self.logger.error(f"Subreddit search failed: {result}")
                            self.stats['errors'] += 1
                        else:
                            all_posts.extend(result)
                else:
                    # Site-wide search
                    posts = await self._search_site_wide_async(reddit, query, username, rate_limiter)
                    all_posts.extend(posts)
                
                # Apply filters
                filtered_posts = self._apply_filters(all_posts, query)
                
                # Analyze for business opportunities concurrently
                analyzed_posts = await self._analyze_posts_concurrent(filtered_posts)
                
                # Sort by business score
                analyzed_posts.sort(key=lambda x: x.business_score, reverse=True)
                
                self.stats['posts_analyzed'] += len(analyzed_posts)
                self.stats['business_leads_found'] += sum(
                    1 for post in analyzed_posts if post.business_score > 1.0
                )
                
                return analyzed_posts
                
            finally:
                self.stats['concurrent_requests'] -= 1
    
    async def _search_subreddit_async(
        self,
        reddit: asyncpraw.Reddit,
        subreddit_name: str,
        query: SearchQuery,
        username: str,
        rate_limiter: AsyncRateLimiter
    ) -> List[PostData]:
        """Async subreddit search"""
        posts = []
        
        try:
            await rate_limiter.acquire()
            
            subreddit = await reddit.subreddit(subreddit_name)
            
            # Choose search method
            if query.sort == "hot":
                submissions = subreddit.hot(limit=query.limit)
            elif query.sort == "new":
                submissions = subreddit.new(limit=query.limit)
            elif query.sort == "top":
                submissions = subreddit.top(time_filter=query.time_filter, limit=query.limit)
            else:
                submissions = subreddit.search(
                    query.query,
                    sort=query.sort,
                    time_filter=query.time_filter,
                    limit=query.limit
                )
            
            await self.account_manager.record_request(username)
            self.stats['requests_made'] += 1
            
            async for submission in submissions:
                post_data = await self._submission_to_post_data_async(submission)
                posts.append(post_data)
                
        except Exception as e:
            if "429" in str(e):
                await rate_limiter.record_rate_limit()
            
            self.logger.error(f"Async subreddit search failed for {subreddit_name}: {e}")
            await self.account_manager.record_error(username)
        
        return posts
    
    async def _search_site_wide_async(
        self,
        reddit: asyncpraw.Reddit,
        query: SearchQuery,
        username: str,
        rate_limiter: AsyncRateLimiter
    ) -> List[PostData]:
        """Async site-wide search"""
        posts = []
        
        try:
            await rate_limiter.acquire()
            
            subreddit = await reddit.subreddit("all")
            submissions = subreddit.search(
                query.query,
                sort=query.sort,
                time_filter=query.time_filter,
                limit=query.limit
            )
            
            await self.account_manager.record_request(username)
            self.stats['requests_made'] += 1
            
            async for submission in submissions:
                post_data = await self._submission_to_post_data_async(submission)
                posts.append(post_data)
                
        except Exception as e:
            if "429" in str(e):
                await rate_limiter.record_rate_limit()
            
            self.logger.error(f"Async site-wide search failed: {e}")
            await self.account_manager.record_error(username)
        
        return posts
    
    async def _submission_to_post_data_async(self, submission) -> PostData:
        """Convert async submission to PostData"""
        # Load submission attributes
        await submission.load()
        
        text = ""
        if hasattr(submission, 'selftext') and submission.selftext:
            text = submission.selftext
        
        return PostData(
            id=submission.id,
            title=submission.title,
            text=text,
            author=str(submission.author) if submission.author else "[deleted]",
            subreddit=str(submission.subreddit),
            created_utc=submission.created_utc,
            score=submission.score,
            num_comments=submission.num_comments,
            url=submission.url,
            permalink=f"https://reddit.com{submission.permalink}",
            is_self=submission.is_self,
            is_video=getattr(submission, 'is_video', False),
            over_18=submission.over_18,
            stickied=submission.stickied,
            locked=submission.locked,
            archived=submission.archived,
            spoiler=submission.spoiler,
            distinguished=submission.distinguished,
            link_flair_text=submission.link_flair_text,
            author_flair_text=submission.author_flair_text,
            upvote_ratio=submission.upvote_ratio,
            total_awards_received=getattr(submission, 'total_awards_received', 0),
            gilded=submission.gilded
        )
    
    def _apply_filters(self, posts: List[PostData], query: SearchQuery) -> List[PostData]:
        """Apply search filters (same as sync version)"""
        filtered_posts = []
        
        for post in posts:
            # NSFW filter
            if not query.include_nsfw and post.over_18:
                continue
            
            # Minimum score filter
            if post.score < query.min_score:
                continue
            
            # Age filter
            if query.max_age_days:
                post_age = (datetime.now() - datetime.fromtimestamp(post.created_utc)).days
                if post_age > query.max_age_days:
                    continue
            
            filtered_posts.append(post)
        
        return filtered_posts
    
    async def _analyze_posts_concurrent(self, posts: List[PostData]) -> List[PostData]:
        """Analyze posts for business opportunities concurrently"""
        if not posts:
            return []
        
        # Create analysis tasks
        tasks = []
        chunk_size = max(1, len(posts) // self.max_concurrent)
        
        for i in range(0, len(posts), chunk_size):
            chunk = posts[i:i + chunk_size]
            task = asyncio.create_task(self._analyze_post_chunk(chunk))
            tasks.append(task)
        
        # Wait for all analysis to complete
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        analyzed_posts = []
        for chunk_results in results:
            analyzed_posts.extend(chunk_results)
        
        return analyzed_posts
    
    async def _analyze_post_chunk(self, posts: List[PostData]) -> List[PostData]:
        """Analyze a chunk of posts"""
        analyzed_posts = []
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        for post in posts:
            analyzed_post = await loop.run_in_executor(
                None, 
                self.business_logic.analyze_post, 
                post
            )
            analyzed_posts.append(analyzed_post)
        
        return analyzed_posts
    
    async def get_post_comments_async(
        self,
        post_ids: List[str],
        max_depth: int = 3
    ) -> Dict[str, List[CommentData]]:
        """Get comments for multiple posts concurrently"""
        tasks = []
        
        for post_id in post_ids:
            task = asyncio.create_task(
                self._get_single_post_comments(post_id, max_depth),
                name=f"comments_{post_id}"
            )
            tasks.append((post_id, task))
        
        results = {}
        
        for post_id, task in tasks:
            try:
                comments = await task
                results[post_id] = comments
            except Exception as e:
                self.logger.error(f"Failed to get comments for {post_id}: {e}")
                results[post_id] = []
                self.stats['errors'] += 1
        
        return results
    
    async def _get_single_post_comments(
        self,
        post_id: str,
        max_depth: int
    ) -> List[CommentData]:
        """Get comments for a single post"""
        async with self.semaphore:
            try:
                username, reddit, rate_limiter = await self.account_manager.get_best_account()
                
                await rate_limiter.acquire()
                
                submission = await reddit.submission(id=post_id)
                await submission.load()
                await submission.comments.replace_more(limit=0)
                
                await self.account_manager.record_request(username)
                self.stats['requests_made'] += 1
                
                comments = []
                
                for comment in submission.comments:
                    comment_data = await self._process_comment_async(comment, max_depth)
                    if comment_data:
                        comments.append(comment_data)
                
                return comments
                
            except Exception as e:
                if "429" in str(e):
                    await rate_limiter.record_rate_limit()
                
                self.logger.error(f"Failed to get comments for {post_id}: {e}")
                await self.account_manager.record_error(username)
                return []
    
    async def _process_comment_async(
        self,
        comment,
        max_depth: int,
        current_depth: int = 0
    ) -> Optional[CommentData]:
        """Process comment asynchronously"""
        if current_depth > max_depth:
            return None
        
        try:
            await comment.load()
            
            comment_data = CommentData(
                id=comment.id,
                body=comment.body,
                author=str(comment.author) if comment.author else "[deleted]",
                created_utc=comment.created_utc,
                score=comment.score,
                is_submitter=comment.is_submitter,
                stickied=comment.stickied,
                distinguished=comment.distinguished,
                parent_id=comment.parent_id,
                link_id=comment.link_id,
                subreddit=str(comment.subreddit),
                depth=current_depth
            )
            
            # Business analysis
            if comment.body and len(comment.body) > 50:
                business_keywords = [
                    kw for kw in self.business_logic.keywords 
                    if kw.lower() in comment.body.lower()
                ]
                comment_data.business_score = len(business_keywords) * 0.5
                comment_data.problem_indicators = business_keywords
            
            # Process replies
            if hasattr(comment, 'replies') and current_depth < max_depth:
                reply_tasks = []
                for reply in comment.replies:
                    task = asyncio.create_task(
                        self._process_comment_async(reply, max_depth, current_depth + 1)
                    )
                    reply_tasks.append(task)
                
                reply_results = await asyncio.gather(*reply_tasks, return_exceptions=True)
                
                for result in reply_results:
                    if isinstance(result, CommentData):
                        comment_data.replies.append(result)
            
            return comment_data
            
        except Exception as e:
            self.logger.warning(f"Failed to process comment: {e}")
            return None
    
    async def stream_search_results(
        self,
        query: SearchQuery
    ) -> AsyncIterator[PostData]:
        """Stream search results as they become available"""
        username, reddit, rate_limiter = await self.account_manager.get_best_account()
        
        try:
            if query.subreddits:
                for subreddit_name in query.subreddits:
                    await rate_limiter.acquire()
                    
                    subreddit = await reddit.subreddit(subreddit_name)
                    
                    if query.sort == "new":
                        submissions = subreddit.new(limit=query.limit)
                    elif query.sort == "hot":
                        submissions = subreddit.hot(limit=query.limit)
                    else:
                        submissions = subreddit.search(
                            query.query,
                            sort=query.sort,
                            limit=query.limit
                        )
                    
                    await self.account_manager.record_request(username)
                    
                    async for submission in submissions:
                        post_data = await self._submission_to_post_data_async(submission)
                        
                        # Apply filters
                        if self._post_passes_filters(post_data, query):
                            # Analyze business potential
                            analyzed_post = await asyncio.get_event_loop().run_in_executor(
                                None, 
                                self.business_logic.analyze_post,
                                post_data
                            )
                            yield analyzed_post
            
        except Exception as e:
            if "429" in str(e):
                await rate_limiter.record_rate_limit()
            
            self.logger.error(f"Stream search failed: {e}")
            await self.account_manager.record_error(username)
    
    def _post_passes_filters(self, post: PostData, query: SearchQuery) -> bool:
        """Check if post passes query filters"""
        if not query.include_nsfw and post.over_18:
            return False
        if post.score < query.min_score:
            return False
        if query.max_age_days:
            post_age = (datetime.now() - datetime.fromtimestamp(post.created_utc)).days
            if post_age > query.max_age_days:
                return False
        return True
    
    async def export_results_async(
        self,
        posts: List[PostData],
        filename: str,
        format: str = "json"
    ) -> Path:
        """Export results asynchronously"""
        export_dir = Path(self.config.app_settings['export_directory'])
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = export_dir / f"{filename}_{timestamp}.{format}"
        
        if format.lower() == "json":
            data = [asdict(post) for post in posts]
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        
        elif format.lower() == "csv":
            import csv
            import io
            
            # Build CSV in memory first
            output = io.StringIO()
            fieldnames = [
                'id', 'title', 'text', 'author', 'subreddit', 'created_utc',
                'score', 'num_comments', 'business_score', 'urgency_level'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for post in posts:
                row = {
                    'id': post.id,
                    'title': post.title,
                    'text': post.text[:500] + '...' if len(post.text) > 500 else post.text,
                    'author': post.author,
                    'subreddit': post.subreddit,
                    'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'business_score': post.business_score,
                    'urgency_level': post.urgency_level
                }
                writer.writerow(row)
            
            # Write to file
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(output.getvalue())
        
        self.logger.info(f"Async exported {len(posts)} posts to: {filepath}")
        return filepath
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'runtime_seconds': runtime,
            'requests_per_second': self.stats['requests_made'] / max(1, runtime),
            'posts_per_second': self.stats['posts_analyzed'] / max(1, runtime),
            'concurrent_requests': self.stats['concurrent_requests'],
            'total_requests': self.stats['requests_made'],
            'total_posts_analyzed': self.stats['posts_analyzed'],
            'business_leads_found': self.stats['business_leads_found'],
            'error_rate': self.stats['errors'] / max(1, self.stats['requests_made']),
            'active_accounts': len(self.account_manager.active_accounts),
            'account_stats': dict(self.account_manager.account_stats)
        }
    
    async def close(self) -> None:
        """Close async client"""
        await self.account_manager.close_all()
        
        if self.session:
            await self.session.close()
        
        self.logger.info("Async Reddit client closed")


# Utility functions for async operations
async def batch_search_multiple_clients(
    clients: List[AsyncRedditAPIClient],
    queries: List[SearchQuery],
    max_concurrent_clients: int = 3
) -> Dict[str, List[PostData]]:
    """Use multiple clients to search concurrently"""
    semaphore = asyncio.Semaphore(max_concurrent_clients)
    
    async def search_with_client(client: AsyncRedditAPIClient, query: SearchQuery):
        async with semaphore:
            return await client._search_single_query(query)
    
    tasks = []
    for i, query in enumerate(queries):
        client = clients[i % len(clients)]
        task = asyncio.create_task(
            search_with_client(client, query),
            name=f"client_{i % len(clients)}_query_{query.query[:20]}"
        )
        tasks.append((query.query, task))
    
    results = {}
    for query_name, task in tasks:
        try:
            posts = await task
            results[query_name] = posts
        except Exception as e:
            logging.error(f"Multi-client query '{query_name}' failed: {e}")
            results[query_name] = []
    
    return results

@asynccontextmanager
async def async_reddit_client_pool(
    usernames: List[str],
    config: Optional[RedditConfig] = None
) -> List[AsyncRedditAPIClient]:
    """Context manager for a pool of async Reddit clients"""
    clients = []
    
    try:
        for username in usernames:
            client = AsyncRedditAPIClient(config)
            await client.initialize()
            await client.authenticate_user(username)
            clients.append(client)
        
        yield clients
        
    finally:
        for client in clients:
            await client.close()

# Example usage
async def main():
    """Example usage of async Reddit client"""
    config = get_config()
    
    async with AsyncRedditAPIClient(config) as client:
        # Add accounts
        await client.authenticate_user("username1")
        await client.authenticate_user("username2")
        
        # Create search queries
        queries = [
            SearchQuery(
                query="automation workflow",
                subreddits=["entrepreneur", "smallbusiness"],
                limit=50
            ),
            SearchQuery(
                query="manual data entry",
                subreddits=["excel", "productivity"],
                limit=50
            )
        ]
        
        # Search concurrently
        results = await client.search_posts_concurrent(queries)
        
        # Export results
        for query_name, posts in results.items():
            if posts:
                filepath = await client.export_results_async(
                    posts, 
                    f"async_search_{query_name.replace(' ', '_')}"
                )
                print(f"Exported {len(posts)} posts to {filepath}")
        
        # Get performance stats
        stats = await client.get_performance_stats()
        print(f"Performance: {stats}")

if __name__ == "__main__":
    asyncio.run(main())