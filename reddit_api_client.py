"""
Reddit API Client with PRAW Integration
Comprehensive Reddit API client supporting OAuth2, multi-account management,
rate limiting, content fetching, and business lead detection.
"""

try:
    import praw
    import prawcore
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

try:
    import asyncpraw
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
from typing import Dict, List, Optional, Any, Union, Iterator, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
import time
import sqlite3
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import backoff
from cachetools import TTLCache, LRUCache
import re
from collections import defaultdict, Counter
import structlog
from functools import wraps
import inspect

try:
    from auth.reddit_auth import RedditAuthenticator, AuthToken
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

try:
    from config.reddit_config import get_config, RedditConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

@dataclass
class PostData:
    """Reddit post data structure"""
    id: str
    title: str
    text: str
    author: str
    subreddit: str
    created_utc: float
    score: int
    num_comments: int
    url: str
    permalink: str
    is_self: bool
    is_video: bool
    over_18: bool
    stickied: bool
    locked: bool
    archived: bool
    spoiler: bool
    distinguished: Optional[str]
    link_flair_text: Optional[str]
    author_flair_text: Optional[str]
    upvote_ratio: float
    total_awards_received: int
    gilded: int
    
    # Business logic fields
    business_score: float = 0.0
    problem_indicators: List[str] = None
    automation_keywords: List[str] = None
    urgency_level: str = "low"
    potential_value: str = "unknown"
    
    def __post_init__(self):
        if self.problem_indicators is None:
            self.problem_indicators = []
        if self.automation_keywords is None:
            self.automation_keywords = []

@dataclass
class CommentData:
    """Reddit comment data structure"""
    id: str
    body: str
    author: str
    created_utc: float
    score: int
    is_submitter: bool
    stickied: bool
    distinguished: Optional[str]
    parent_id: str
    link_id: str
    subreddit: str
    depth: int = 0
    replies: List['CommentData'] = None
    
    # Business logic fields
    business_score: float = 0.0
    problem_indicators: List[str] = None
    
    def __post_init__(self):
        if self.replies is None:
            self.replies = []
        if self.problem_indicators is None:
            self.problem_indicators = []

@dataclass
class SearchQuery:
    """Search query configuration"""
    query: str
    subreddits: List[str] = None
    sort: str = "relevance"  # relevance, hot, top, new, comments
    time_filter: str = "all"  # all, year, month, week, day, hour
    limit: int = 100
    include_nsfw: bool = False
    min_score: int = 0
    max_age_days: Optional[int] = None
    author_filter: Optional[str] = None
    domain_filter: Optional[str] = None
    
    def __post_init__(self):
        if self.subreddits is None:
            self.subreddits = []

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, config: RedditConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Request tracking
        self.requests_per_minute = []
        self.requests_per_hour = []
        self.burst_requests = []
        
        # Locks for thread safety
        self._lock = threading.Lock()
        
        # Rate limit counters
        self.minute_window = timedelta(minutes=1)
        self.hour_window = timedelta(hours=1)
        self.burst_window = timedelta(seconds=10)
        
        # Backoff tracking
        self.backoff_until: Optional[datetime] = None
        self.consecutive_429s = 0
        
    def can_make_request(self) -> Tuple[bool, Optional[float]]:
        """
        Check if a request can be made
        
        Returns:
            (can_make_request, wait_time_seconds)
        """
        with self._lock:
            now = datetime.now()
            
            # Check if in backoff period
            if self.backoff_until and now < self.backoff_until:
                wait_time = (self.backoff_until - now).total_seconds()
                return False, wait_time
            
            # Clean old requests
            self._cleanup_old_requests(now)
            
            # Check per-minute limit
            if len(self.requests_per_minute) >= self.config.api_limits.requests_per_minute:
                oldest_request = min(self.requests_per_minute)
                wait_time = (oldest_request + self.minute_window - now).total_seconds()
                return False, max(0, wait_time)
            
            # Check per-hour limit
            if len(self.requests_per_hour) >= self.config.api_limits.requests_per_hour:
                oldest_request = min(self.requests_per_hour)
                wait_time = (oldest_request + self.hour_window - now).total_seconds()
                return False, max(0, wait_time)
            
            # Check burst limit
            if len(self.burst_requests) >= self.config.api_limits.burst_limit:
                oldest_request = min(self.burst_requests)
                wait_time = (oldest_request + self.burst_window - now).total_seconds()
                return False, max(0, wait_time)
            
            return True, 0.0
    
    def record_request(self) -> None:
        """Record a successful request"""
        with self._lock:
            now = datetime.now()
            self.requests_per_minute.append(now)
            self.requests_per_hour.append(now)
            self.burst_requests.append(now)
            self.consecutive_429s = 0
    
    def record_rate_limit(self, retry_after: Optional[int] = None) -> None:
        """Record a rate limit (429) response"""
        with self._lock:
            now = datetime.now()
            self.consecutive_429s += 1
            
            if retry_after:
                self.backoff_until = now + timedelta(seconds=retry_after)
            else:
                # Exponential backoff
                backoff_seconds = min(
                    300,  # Max 5 minutes
                    self.config.api_limits.cooldown_seconds * 
                    (self.config.api_limits.backoff_factor ** self.consecutive_429s)
                )
                self.backoff_until = now + timedelta(seconds=backoff_seconds)
            
            self.logger.warning(
                "Rate limited",
                consecutive_429s=self.consecutive_429s,
                backoff_until=self.backoff_until.isoformat()
            )
    
    def _cleanup_old_requests(self, now: datetime) -> None:
        """Clean up old request records"""
        # Clean minute window
        cutoff_minute = now - self.minute_window
        self.requests_per_minute = [
            req for req in self.requests_per_minute if req > cutoff_minute
        ]
        
        # Clean hour window
        cutoff_hour = now - self.hour_window
        self.requests_per_hour = [
            req for req in self.requests_per_hour if req > cutoff_hour
        ]
        
        # Clean burst window
        cutoff_burst = now - self.burst_window
        self.burst_requests = [
            req for req in self.burst_requests if req > cutoff_burst
        ]
    
    def wait_if_needed(self) -> None:
        """Wait if rate limiting requires it"""
        can_request, wait_time = self.can_make_request()
        if not can_request and wait_time > 0:
            self.logger.info(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)

class BusinessLogicEngine:
    """Advanced business lead detection and scoring"""
    
    def __init__(self, keywords_file: str = "keywords.json"):
        self.keywords_file = Path(keywords_file)
        self.keywords = self._load_keywords()
        self.logger = structlog.get_logger(__name__)
        
        # Scoring weights
        self.weights = {
            'keyword_match': 1.0,
            'multiple_keywords': 1.5,
            'urgency_indicators': 2.0,
            'scale_indicators': 1.8,
            'manual_process': 2.2,
            'time_waste': 1.7,
            'automation_request': 2.5,
            'business_process': 1.3,
            'engagement': 0.8,
            'title_bonus': 1.2
        }
        
        # Urgency indicators
        self.urgency_patterns = {
            'high': [
                r'\basap\b', r'\burgent\b', r'\bcrisis\b', r'\bemergency\b',
                r'\bcrashing\b', r'\bfailing\b', r'\bbroken\b', r'\bdown\b'
            ],
            'medium': [
                r'\bsoon\b', r'\bquickly\b', r'\brushing\b', r'\bhurry\b',
                r'\bdeadline\b', r'\bpressure\b', r'\bstressed\b'
            ],
            'high_value': [
                r'\$\d+k\b', r'\$\d+,\d+', r'\bmillion\b', r'\bbillion\b',
                r'\bprofit\b', r'\brevenue\b', r'\bcost\s*saving\b'
            ]
        }
        
        # Scale indicators
        self.scale_patterns = [
            r'\bhundreds?\s+of\b', r'\bthousands?\s+of\b', r'\bmillions?\s+of\b',
            r'\bmultiple\s+times\b', r'\beveryday\b', r'\bdaily\b', r'\bweekly\b',
            r'\bscale\b', r'\bbulk\b', r'\bmass\b', r'\blarge\s+volume\b'
        ]
    
    def _load_keywords(self) -> List[str]:
        """Load business problem keywords"""
        try:
            if self.keywords_file.exists():
                with open(self.keywords_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load keywords: {e}")
        
        # Fallback keywords
        return [
            "manual data entry", "copy and paste", "repetitive task",
            "automation", "streamline", "workflow", "bottleneck",
            "time-consuming", "manual process", "integrate systems"
        ]
    
    def analyze_post(self, post: PostData) -> PostData:
        """Analyze post for business opportunities"""
        combined_text = f"{post.title} {post.text}".lower()
        
        # Find keyword matches
        matched_keywords = []
        problem_indicators = []
        
        for keyword in self.keywords:
            if keyword.lower() in combined_text:
                matched_keywords.append(keyword)
                problem_indicators.append(keyword)
        
        # Calculate base score
        base_score = len(matched_keywords) * self.weights['keyword_match']
        
        # Multiple keyword bonus
        if len(matched_keywords) > 1:
            base_score *= self.weights['multiple_keywords']
        
        # Title bonus
        title_keywords = sum(1 for kw in self.keywords if kw.lower() in post.title.lower())
        if title_keywords > 0:
            base_score *= self.weights['title_bonus']
        
        # Urgency analysis
        urgency_level = self._analyze_urgency(combined_text)
        if urgency_level == 'high':
            base_score *= self.weights['urgency_indicators']
        elif urgency_level == 'medium':
            base_score *= 1.3
        
        # Scale analysis
        if self._has_scale_indicators(combined_text):
            base_score *= self.weights['scale_indicators']
        
        # Manual process indicators
        if self._has_manual_process_indicators(combined_text):
            base_score *= self.weights['manual_process']
        
        # Time waste indicators
        if self._has_time_waste_indicators(combined_text):
            base_score *= self.weights['time_waste']
        
        # Direct automation requests
        if self._has_automation_request(combined_text):
            base_score *= self.weights['automation_request']
        
        # Engagement factor
        engagement_score = (post.score + post.num_comments) / 100
        engagement_factor = min(2.0, max(0.5, engagement_score))
        base_score *= engagement_factor * self.weights['engagement']
        
        # Update post data
        post.business_score = round(base_score, 2)
        post.problem_indicators = problem_indicators
        post.automation_keywords = matched_keywords
        post.urgency_level = urgency_level
        post.potential_value = self._assess_potential_value(combined_text)
        
        return post
    
    def _analyze_urgency(self, text: str) -> str:
        """Analyze urgency level from text"""
        for level, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level if level != 'high_value' else 'high'
        return 'low'
    
    def _has_scale_indicators(self, text: str) -> bool:
        """Check for scale indicators"""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in self.scale_patterns)
    
    def _has_manual_process_indicators(self, text: str) -> bool:
        """Check for manual process indicators"""
        manual_patterns = [
            r'\bmanual\b', r'\bby\s+hand\b', r'\bone\s+by\s+one\b',
            r'\bindividually\b', r'\brepetitive\b', r'\btedious\b'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in manual_patterns)
    
    def _has_time_waste_indicators(self, text: str) -> bool:
        """Check for time waste indicators"""
        time_patterns = [
            r'\btakes\s+hours\b', r'\btime-consuming\b', r'\bwasting\s+time\b',
            r'\beating\s+up\s+time\b', r'\bspending\s+all\s+day\b'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in time_patterns)
    
    def _has_automation_request(self, text: str) -> bool:
        """Check for direct automation requests"""
        automation_patterns = [
            r'\bautomat\w*\b', r'\bscript\b', r'\btool\b', r'\bsoftware\b',
            r'\bapp\b', r'\bprogram\b', r'\bsolution\b', r'\bintegrat\w*\b'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in automation_patterns)
    
    def _assess_potential_value(self, text: str) -> str:
        """Assess potential business value"""
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.urgency_patterns['high_value']):
            return 'high'
        elif self._has_scale_indicators(text) and self._has_manual_process_indicators(text):
            return 'medium'
        elif len([kw for kw in self.keywords if kw.lower() in text]) >= 3:
            return 'medium'
        else:
            return 'low'

class MultiAccountManager:
    """Multi-account Reddit API management"""
    
    def __init__(self, authenticator: RedditAuthenticator):
        self.authenticator = authenticator
        self.active_accounts: Dict[str, praw.Reddit] = {}
        self.account_stats: Dict[str, Dict] = defaultdict(lambda: {
            'requests_made': 0,
            'last_used': None,
            'rate_limited': False,
            'errors': 0
        })
        self.current_account = None
        self.logger = structlog.get_logger(__name__)
        self._lock = threading.Lock()
    
    def add_account(self, username: str, force_refresh: bool = False) -> bool:
        """Add account to manager"""
        try:
            token = self.authenticator.load_token(username)
            if not token:
                self.logger.error(f"No token found for user: {username}")
                return False
            
            if force_refresh or not self.authenticator.validate_token(token):
                if token.refresh_token:
                    token = self.authenticator.refresh_token(token)
                else:
                    self.logger.error(f"Invalid token for user {username} and no refresh token")
                    return False
            
            # Create Reddit instance
            config = get_config()
            if token.access_token == "password_flow":
                # Password flow
                reddit = praw.Reddit(
                    client_id=config.credentials.client_id,
                    client_secret=config.credentials.client_secret,
                    username=username,
                    password="",  # We don't store passwords
                    user_agent=config.credentials.user_agent
                )
            else:
                # OAuth flow
                reddit = praw.Reddit(
                    client_id=config.credentials.client_id,
                    client_secret=config.credentials.client_secret,
                    refresh_token=token.refresh_token,
                    user_agent=config.credentials.user_agent
                )
            
            # Test the connection
            reddit.user.me()
            
            with self._lock:
                self.active_accounts[username] = reddit
                if not self.current_account:
                    self.current_account = username
            
            self.logger.info(f"Added account: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add account {username}: {e}")
            return False
    
    def switch_account(self, username: str) -> bool:
        """Switch to different account"""
        with self._lock:
            if username not in self.active_accounts:
                if not self.add_account(username):
                    return False
            
            self.current_account = username
            self.logger.info(f"Switched to account: {username}")
            return True
    
    def get_current_reddit(self) -> Optional[praw.Reddit]:
        """Get current Reddit instance"""
        if not self.current_account:
            return None
        return self.active_accounts.get(self.current_account)
    
    def get_least_used_account(self) -> Optional[str]:
        """Get account with least usage"""
        if not self.active_accounts:
            return None
        
        return min(
            self.active_accounts.keys(),
            key=lambda x: self.account_stats[x]['requests_made']
        )
    
    def record_request(self, username: str = None) -> None:
        """Record API request for account"""
        username = username or self.current_account
        if username:
            self.account_stats[username]['requests_made'] += 1
            self.account_stats[username]['last_used'] = datetime.now()
    
    def record_error(self, username: str = None) -> None:
        """Record error for account"""
        username = username or self.current_account
        if username:
            self.account_stats[username]['errors'] += 1

class RedditAPIClient:
    """Main Reddit API client with comprehensive features"""
    
    def __init__(self, config: Optional[RedditConfig] = None):
        self.config = config or get_config()
        self.authenticator = RedditAuthenticator()
        self.account_manager = MultiAccountManager(self.authenticator)
        self.rate_limiter = RateLimiter(self.config)
        self.business_logic = BusinessLogicEngine()
        self.logger = structlog.get_logger(__name__)
        
        # Caching
        self.post_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute TTL
        self.subreddit_cache = LRUCache(maxsize=100)
        
        # Thread pool for parallel operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.app_settings['thread_pool_size']
        )
        
        # Statistics tracking
        self.stats = {
            'requests_made': 0,
            'posts_analyzed': 0,
            'business_leads_found': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'rate_limits': 0,
            'errors': 0
        }
    
    def authenticate_user(self, username: str = None, use_web_flow: bool = True) -> bool:
        """Authenticate a user account"""
        try:
            if use_web_flow:
                token = self.authenticator.authenticate_web_flow()
                username = token.username
            elif username:
                # Check if token already exists
                token = self.authenticator.load_token(username)
                if not token:
                    self.logger.error(f"No token found for {username}")
                    return False
            else:
                self.logger.error("Username required for non-web authentication")
                return False
            
            return self.account_manager.add_account(username)
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def search_posts(
        self, 
        query: SearchQuery, 
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[PostData]:
        """Search for posts with business logic analysis"""
        all_posts = []
        
        try:
            reddit = self.account_manager.get_current_reddit()
            if not reddit:
                raise ValueError("No authenticated Reddit instance available")
            
            # Search in specified subreddits or site-wide
            if query.subreddits:
                total_subreddits = len(query.subreddits)
                for i, subreddit_name in enumerate(query.subreddits):
                    if progress_callback:
                        progress_callback(i, total_subreddits)
                    
                    posts = self._search_subreddit(reddit, subreddit_name, query)
                    all_posts.extend(posts)
            else:
                # Site-wide search
                posts = self._search_site_wide(reddit, query)
                all_posts.extend(posts)
            
            # Apply filters
            filtered_posts = self._apply_filters(all_posts, query)
            
            # Analyze for business opportunities
            analyzed_posts = []
            for post in filtered_posts:
                analyzed_post = self.business_logic.analyze_post(post)
                analyzed_posts.append(analyzed_post)
                
                if analyzed_post.business_score > 1.0:
                    self.stats['business_leads_found'] += 1
            
            self.stats['posts_analyzed'] += len(analyzed_posts)
            
            # Sort by business score
            analyzed_posts.sort(key=lambda x: x.business_score, reverse=True)
            
            return analyzed_posts
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            self.stats['errors'] += 1
            raise
    
    def _search_subreddit(self, reddit: praw.Reddit, subreddit_name: str, query: SearchQuery) -> List[PostData]:
        """Search within a specific subreddit"""
        posts = []
        
        try:
            self.rate_limiter.wait_if_needed()
            
            subreddit = reddit.subreddit(subreddit_name)
            
            # Choose search method based on sort
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
            
            self.rate_limiter.record_request()
            self.account_manager.record_request()
            self.stats['requests_made'] += 1
            
            # Process submissions
            for submission in submissions:
                post_data = self._submission_to_post_data(submission)
                posts.append(post_data)
            
        except prawcore.exceptions.TooManyRequests as e:
            self.logger.warning(f"Rate limited on subreddit {subreddit_name}")
            self.rate_limiter.record_rate_limit(getattr(e, 'retry_after', None))
            self.stats['rate_limits'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to search subreddit {subreddit_name}: {e}")
            self.account_manager.record_error()
            self.stats['errors'] += 1
        
        return posts
    
    def _search_site_wide(self, reddit: praw.Reddit, query: SearchQuery) -> List[PostData]:
        """Search across all of Reddit"""
        posts = []
        
        try:
            self.rate_limiter.wait_if_needed()
            
            submissions = reddit.subreddit("all").search(
                query.query,
                sort=query.sort,
                time_filter=query.time_filter,
                limit=query.limit
            )
            
            self.rate_limiter.record_request()
            self.account_manager.record_request()
            self.stats['requests_made'] += 1
            
            for submission in submissions:
                post_data = self._submission_to_post_data(submission)
                posts.append(post_data)
                
        except prawcore.exceptions.TooManyRequests as e:
            self.logger.warning("Rate limited on site-wide search")
            self.rate_limiter.record_rate_limit(getattr(e, 'retry_after', None))
            self.stats['rate_limits'] += 1
            
        except Exception as e:
            self.logger.error(f"Site-wide search failed: {e}")
            self.account_manager.record_error()
            self.stats['errors'] += 1
        
        return posts
    
    def _submission_to_post_data(self, submission) -> PostData:
        """Convert PRAW submission to PostData"""
        # Get post text
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
            is_video=submission.is_video,
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
        """Apply search filters to posts"""
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
            
            # Author filter
            if query.author_filter and query.author_filter.lower() not in post.author.lower():
                continue
            
            # Domain filter (for link posts)
            if query.domain_filter and query.domain_filter.lower() not in post.url.lower():
                continue
            
            filtered_posts.append(post)
        
        return filtered_posts
    
    def get_post_comments(self, post_id: str, max_depth: int = 3) -> List[CommentData]:
        """Get comments for a post with business analysis"""
        comments = []
        
        try:
            reddit = self.account_manager.get_current_reddit()
            if not reddit:
                raise ValueError("No authenticated Reddit instance available")
            
            self.rate_limiter.wait_if_needed()
            
            submission = reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            self.rate_limiter.record_request()
            self.account_manager.record_request()
            self.stats['requests_made'] += 1
            
            # Process comments recursively
            for comment in submission.comments:
                comment_data = self._process_comment(comment, max_depth)
                if comment_data:
                    comments.append(comment_data)
            
        except Exception as e:
            self.logger.error(f"Failed to get comments for post {post_id}: {e}")
            self.stats['errors'] += 1
        
        return comments
    
    def _process_comment(self, comment, max_depth: int, current_depth: int = 0) -> Optional[CommentData]:
        """Process a comment and its replies"""
        if current_depth > max_depth:
            return None
        
        try:
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
            
            # Analyze for business opportunities
            if comment.body and len(comment.body) > 50:  # Only analyze substantial comments
                # Simple business scoring for comments
                business_keywords = [kw for kw in self.business_logic.keywords if kw.lower() in comment.body.lower()]
                comment_data.business_score = len(business_keywords) * 0.5
                comment_data.problem_indicators = business_keywords
            
            # Process replies
            if hasattr(comment, 'replies') and current_depth < max_depth:
                for reply in comment.replies:
                    reply_data = self._process_comment(reply, max_depth, current_depth + 1)
                    if reply_data:
                        comment_data.replies.append(reply_data)
            
            return comment_data
            
        except Exception as e:
            self.logger.warning(f"Failed to process comment {getattr(comment, 'id', 'unknown')}: {e}")
            return None
    
    def get_account_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'api_stats': self.stats.copy(),
            'account_stats': dict(self.account_manager.account_stats),
            'active_accounts': list(self.account_manager.active_accounts.keys()),
            'current_account': self.account_manager.current_account,
            'cache_stats': {
                'post_cache_size': len(self.post_cache),
                'subreddit_cache_size': len(self.subreddit_cache)
            },
            'rate_limiter_status': {
                'can_make_request': self.rate_limiter.can_make_request(),
                'backoff_until': self.rate_limiter.backoff_until.isoformat() if self.rate_limiter.backoff_until else None
            }
        }
    
    def export_results(
        self, 
        posts: List[PostData], 
        filename: str,
        format: str = "csv",
        include_analysis: bool = True
    ) -> Path:
        """Export search results to file"""
        export_dir = Path(self.config.app_settings['export_directory'])
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "csv":
            return self._export_csv(posts, export_dir / f"{filename}_{timestamp}.csv", include_analysis)
        elif format.lower() == "json":
            return self._export_json(posts, export_dir / f"{filename}_{timestamp}.json", include_analysis)
        elif format.lower() == "markdown":
            return self._export_markdown(posts, export_dir / f"{filename}_{timestamp}.md", include_analysis)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_csv(self, posts: List[PostData], filepath: Path, include_analysis: bool) -> Path:
        """Export posts to CSV"""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'title', 'text', 'author', 'subreddit', 'created_utc',
                'score', 'num_comments', 'url', 'permalink', 'upvote_ratio'
            ]
            
            if include_analysis:
                fieldnames.extend([
                    'business_score', 'problem_indicators', 'automation_keywords',
                    'urgency_level', 'potential_value'
                ])
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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
                    'url': post.url,
                    'permalink': post.permalink,
                    'upvote_ratio': post.upvote_ratio
                }
                
                if include_analysis:
                    row.update({
                        'business_score': post.business_score,
                        'problem_indicators': '; '.join(post.problem_indicators),
                        'automation_keywords': '; '.join(post.automation_keywords),
                        'urgency_level': post.urgency_level,
                        'potential_value': post.potential_value
                    })
                
                writer.writerow(row)
        
        self.logger.info(f"Exported {len(posts)} posts to CSV: {filepath}")
        return filepath
    
    def _export_json(self, posts: List[PostData], filepath: Path, include_analysis: bool) -> Path:
        """Export posts to JSON"""
        data = []
        for post in posts:
            post_dict = asdict(post)
            if not include_analysis:
                # Remove analysis fields
                for field in ['business_score', 'problem_indicators', 'automation_keywords', 'urgency_level', 'potential_value']:
                    post_dict.pop(field, None)
            data.append(post_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Exported {len(posts)} posts to JSON: {filepath}")
        return filepath
    
    def _export_markdown(self, posts: List[PostData], filepath: Path, include_analysis: bool) -> Path:
        """Export posts to Markdown"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Reddit Search Results\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total posts: {len(posts)}\n\n")
            
            for i, post in enumerate(posts, 1):
                f.write(f"## {i}. {post.title}\n\n")
                f.write(f"**Subreddit:** r/{post.subreddit}  \n")
                f.write(f"**Author:** u/{post.author}  \n")
                f.write(f"**Score:** {post.score} | **Comments:** {post.num_comments}  \n")
                f.write(f"**Created:** {datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M')}  \n")
                f.write(f"**URL:** {post.permalink}\n\n")
                
                if include_analysis and post.business_score > 0:
                    f.write(f"**Business Score:** {post.business_score}  \n")
                    f.write(f"**Urgency Level:** {post.urgency_level}  \n")
                    f.write(f"**Potential Value:** {post.potential_value}  \n")
                    if post.problem_indicators:
                        f.write(f"**Problem Indicators:** {', '.join(post.problem_indicators)}  \n")
                    f.write("\n")
                
                if post.text:
                    text_preview = post.text[:300] + "..." if len(post.text) > 300 else post.text
                    f.write(f"**Content:**\n{text_preview}\n\n")
                
                f.write("---\n\n")
        
        self.logger.info(f"Exported {len(posts)} posts to Markdown: {filepath}")
        return filepath
    
    def close(self):
        """Clean up resources"""
        self.thread_pool.shutdown(wait=True)
        self.logger.info("Reddit API client closed")