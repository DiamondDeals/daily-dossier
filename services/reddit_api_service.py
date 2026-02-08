"""
Reddit API Service wrapper
Wraps the existing reddit_api_client.py with additional service functionality
"""

from reddit_api_client import RedditAPIClient, SearchQuery, PostData
from typing import List, Dict, Any, Optional, Callable
from utils.logging_config import get_logger

class RedditAPIService:
    """
    Service wrapper for Reddit API client
    Provides high-level interface for UI components
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.client = RedditAPIClient(config)
    
    def authenticate_user(self, username: str = None) -> bool:
        """Authenticate user with Reddit"""
        return self.client.authenticate_user(username)
    
    def search_for_opportunities(self, 
                               keywords: List[str], 
                               subreddits: List[str] = None,
                               limit: int = 100,
                               progress_callback: Callable = None) -> List[PostData]:
        """Search for business opportunities"""
        query_text = " OR ".join(keywords)
        search_query = SearchQuery(
            query=query_text,
            subreddits=subreddits,
            limit=limit,
            sort="relevance"
        )
        
        return self.client.search_posts(search_query, progress_callback)
    
    def get_real_time_posts(self, subreddits: List[str], limit: int = 50) -> List[PostData]:
        """Get real-time posts from specified subreddits"""
        all_posts = []
        
        for subreddit in subreddits:
            query = SearchQuery(
                query="",  # Empty query gets all posts
                subreddits=[subreddit],
                sort="new",
                limit=limit // len(subreddits)
            )
            posts = self.client.search_posts(query)
            all_posts.extend(posts)
        
        # Sort by creation time and return most recent
        all_posts.sort(key=lambda x: x.created_utc, reverse=True)
        return all_posts[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API client statistics"""
        return self.client.get_account_stats()
    
    def close(self):
        """Close the service"""
        self.client.close()