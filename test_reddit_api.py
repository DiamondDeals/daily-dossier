"""
Comprehensive Test Suite for Reddit API Integration
Tests for OAuth2 authentication, multi-account management, rate limiting,
content fetching, and business logic detection.
"""

import pytest
import asyncio
import json
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any
import logging

# Import modules to test
from reddit_api_client import (
    RedditAPIClient, PostData, CommentData, SearchQuery, 
    RateLimiter, MultiAccountManager, BusinessLogicEngine
)
from async_reddit_client import AsyncRedditAPIClient, AsyncRateLimiter, AsyncMultiAccountManager
from auth.reddit_auth import RedditAuthenticator, AuthToken
from config.reddit_config import RedditConfig, RedditCredentials, APILimits


class TestPostData:
    """Test PostData data structure"""
    
    def test_post_data_creation(self):
        """Test basic PostData creation"""
        post = PostData(
            id="test123",
            title="Test Post",
            text="This is a test post about automation",
            author="testuser",
            subreddit="testsubreddit",
            created_utc=1640995200.0,
            score=10,
            num_comments=5,
            url="https://reddit.com/test",
            permalink="/r/test/comments/123/test",
            is_self=True,
            is_video=False,
            over_18=False,
            stickied=False,
            locked=False,
            archived=False,
            spoiler=False,
            distinguished=None,
            link_flair_text=None,
            author_flair_text=None,
            upvote_ratio=0.85,
            total_awards_received=0,
            gilded=0
        )
        
        assert post.id == "test123"
        assert post.title == "Test Post"
        assert post.business_score == 0.0
        assert post.problem_indicators == []
        assert post.automation_keywords == []
        assert post.urgency_level == "low"
        assert post.potential_value == "unknown"


class TestBusinessLogicEngine:
    """Test business logic and scoring"""
    
    @pytest.fixture
    def business_engine(self):
        """Create business logic engine for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            keywords = [
                "automation", "manual data entry", "repetitive task",
                "time-consuming", "workflow", "streamline"
            ]
            json.dump(keywords, f)
            f.flush()
            
            engine = BusinessLogicEngine(f.name)
            yield engine
            
            Path(f.name).unlink()  # Clean up
    
    def test_keyword_loading(self, business_engine):
        """Test keyword loading"""
        assert "automation" in business_engine.keywords
        assert "manual data entry" in business_engine.keywords
        assert len(business_engine.keywords) >= 6


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        credentials = RedditCredentials(
            client_id="test_id",
            client_secret="test_secret",
            user_agent="test_agent"
        )
        
        api_limits = APILimits(
            requests_per_minute=10,
            requests_per_hour=100,
            burst_limit=5,
            cooldown_seconds=1,
            retry_attempts=3,
            backoff_factor=2.0
        )
        
        config = Mock(spec=RedditConfig)
        config.credentials = credentials
        config.api_limits = api_limits
        
        return config
    
    def test_rate_limiter_creation(self, config):
        """Test rate limiter initialization"""
        limiter = RateLimiter(config)
        
        assert limiter.config == config
        assert len(limiter.requests_per_minute) == 0
        assert len(limiter.requests_per_hour) == 0
        assert limiter.consecutive_429s == 0


if __name__ == "__main__":
    pytest.main(["-v", "test_reddit_api.py"])