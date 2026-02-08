"""
PersonalizedReddit Database Implementation
SQLite database manager with connection pooling, migrations, and ORM utilities
"""

import sqlite3
import json
import logging
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Generator
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """AI analysis types"""
    KEYWORD_MATCH = "keyword_match"
    SENTIMENT = "sentiment"
    BUSINESS_OPPORTUNITY = "business_opportunity"
    LEAD_SCORE = "lead_score"
    CATEGORY = "category"


class LeadPotential(Enum):
    """Business lead potential levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class QualificationStatus(Enum):
    """Lead qualification status"""
    UNQUALIFIED = "unqualified"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    IN_PROGRESS = "in_progress"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@dataclass
class RedditAccount:
    """Reddit account model"""
    id: Optional[int] = None
    username: str = ""
    password_hash: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    account_type: str = "personal"
    is_active: bool = True
    is_primary: bool = False
    rate_limit_remaining: int = 60
    rate_limit_reset: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Subreddit:
    """Subreddit model"""
    id: Optional[int] = None
    name: str = ""
    display_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    public_description: Optional[str] = None
    subscribers: int = 0
    active_users: int = 0
    category: Optional[str] = None
    is_nsfw: bool = False
    is_quarantined: bool = False
    subreddit_type: str = "public"
    created_utc: Optional[datetime] = None
    icon_img: Optional[str] = None
    banner_img: Optional[str] = None
    url: Optional[str] = None
    is_favorite: bool = False
    is_monitored: bool = True
    last_scraped: Optional[datetime] = None
    scrape_frequency_hours: int = 24
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class RedditPost:
    """Reddit post model"""
    id: Optional[int] = None
    reddit_id: str = ""
    subreddit_id: int = 0
    account_id: Optional[int] = None
    title: str = ""
    selftext: Optional[str] = None
    selftext_html: Optional[str] = None
    url: Optional[str] = None
    permalink: Optional[str] = None
    author: Optional[str] = None
    author_flair_text: Optional[str] = None
    domain: Optional[str] = None
    score: int = 0
    upvote_ratio: float = 0.0
    num_comments: int = 0
    gilded: int = 0
    awards_count: int = 0
    distinguished: Optional[str] = None
    stickied: bool = False
    over_18: bool = False
    spoiler: bool = False
    locked: bool = False
    archived: bool = False
    removed: bool = False
    deleted: bool = False
    post_hint: Optional[str] = None
    thumbnail: Optional[str] = None
    preview_data: Optional[str] = None
    media_data: Optional[str] = None
    link_flair_text: Optional[str] = None
    created_utc: datetime = datetime.now()
    edited_utc: Optional[datetime] = None
    retrieved_at: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    is_processed: bool = False
    processing_status: str = "pending"
    # New analytics fields
    engagement_rate: float = 0.0
    velocity_score: float = 0.0
    trending_score: float = 0.0
    is_archived: bool = False
    archive_reason: Optional[str] = None
    archived_at: Optional[datetime] = None


@dataclass
class PostAnalysis:
    """Post analysis results model"""
    id: Optional[int] = None
    post_id: int = 0
    analysis_type: str = ""
    analysis_version: str = "1.0"
    score: float = 0.0
    confidence: float = 0.0
    result_data: Optional[str] = None
    keywords_matched: Optional[str] = None
    sentiment_score: float = 0.0
    sentiment_label: Optional[str] = None
    business_score: float = 0.0
    lead_potential: str = "low"
    category_predicted: Optional[str] = None
    category_confidence: float = 0.0
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime = datetime.now()


@dataclass
class BusinessLead:
    """Business lead model"""
    id: Optional[int] = None
    post_id: int = 0
    account_id: Optional[int] = None
    lead_title: str = ""
    lead_description: Optional[str] = None
    business_problem: Optional[str] = None
    potential_solution: Optional[str] = None
    industry_category: Optional[str] = None
    company_size_estimate: Optional[str] = None
    urgency_level: int = 1
    budget_estimate: Optional[str] = None
    contact_method: Optional[str] = None
    contact_info: Optional[str] = None
    reddit_author: Optional[str] = None
    author_history_summary: Optional[str] = None
    lead_score: float = 0.0
    qualification_status: str = "unqualified"
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    estimated_value: Optional[float] = None
    probability_percent: int = 0
    source_data: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class DatabaseManager:
    """SQLite database manager with connection pooling and migrations"""
    
    def __init__(self, db_path: str = "personalizedreddit.db", max_connections: int = 5):
        self.db_path = Path(db_path)
        self.max_connections = max_connections
        self._connection_pool = []
        self._pool_lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema and configurations"""
        with self.get_connection() as conn:
            # Set optimal pragma settings
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")
            conn.execute("PRAGMA temp_store = MEMORY")
            
            # Check if database is initialized
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            )
            if not cursor.fetchone():
                self._create_initial_schema(conn)
            
            # Run any pending migrations
            self._run_migrations(conn)
    
    def _create_initial_schema(self, conn: sqlite3.Connection):
        """Create initial database schema"""
        schema_path = Path(__file__).parent / "database_schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
        else:
            logger.warning("Schema file not found, creating minimal structure")
            # Create minimal required tables
            conn.executescript("""
                CREATE TABLE schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rollback_script TEXT,
                    checksum TEXT
                );
                
                INSERT INTO schema_migrations (version, description) 
                VALUES ('001_initial_minimal', 'Minimal schema for bootstrap');
            """)
    
    def _run_migrations(self, conn: sqlite3.Connection):
        """Run pending database migrations"""
        # Get current version
        cursor = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 1"
        )
        current_version = cursor.fetchone()
        current_version = current_version[0] if current_version else None
        
        # Load and run migrations
        migrations_path = Path(__file__).parent / "migrations.sql"
        if migrations_path.exists() and current_version:
            logger.info(f"Current database version: {current_version}")
            # Migration logic would go here
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection from pool"""
        conn = None
        try:
            with self._pool_lock:
                if self._connection_pool:
                    conn = self._connection_pool.pop()
                else:
                    conn = sqlite3.connect(
                        self.db_path,
                        timeout=30.0,
                        check_same_thread=False
                    )
                    conn.row_factory = sqlite3.Row
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                with self._pool_lock:
                    if len(self._connection_pool) < self.max_connections:
                        self._connection_pool.append(conn)
                    else:
                        conn.close()
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = True) -> List[sqlite3.Row]:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return []
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute query with multiple parameter sets"""
        with self.get_connection() as conn:
            conn.executemany(query, params_list)
            conn.commit()


class RedditDataManager:
    """High-level interface for Reddit data operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    # Reddit Account Management
    def create_account(self, account: RedditAccount) -> int:
        """Create a new Reddit account"""
        query = """
            INSERT INTO reddit_accounts 
            (username, password_hash, access_token, refresh_token, token_expires_at, 
             account_type, is_active, is_primary, rate_limit_remaining)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """
        params = (
            account.username, account.password_hash, account.access_token,
            account.refresh_token, account.token_expires_at, account.account_type,
            account.is_active, account.is_primary, account.rate_limit_remaining
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            account_id = cursor.fetchone()[0]
            conn.commit()
            return account_id
    
    def get_account(self, username: str) -> Optional[RedditAccount]:
        """Get account by username"""
        query = "SELECT * FROM reddit_accounts WHERE username = ? AND is_active = 1"
        results = self.db.execute_query(query, (username,))
        
        if results:
            row = results[0]
            return RedditAccount(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                access_token=row['access_token'],
                refresh_token=row['refresh_token'],
                token_expires_at=datetime.fromisoformat(row['token_expires_at']) if row['token_expires_at'] else None,
                account_type=row['account_type'],
                is_active=bool(row['is_active']),
                is_primary=bool(row['is_primary']),
                rate_limit_remaining=row['rate_limit_remaining'],
                rate_limit_reset=datetime.fromisoformat(row['rate_limit_reset']) if row['rate_limit_reset'] else None,
                last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
        return None
    
    def update_rate_limit(self, account_id: int, remaining: int, reset_time: datetime):
        """Update rate limit information"""
        query = """
            UPDATE reddit_accounts 
            SET rate_limit_remaining = ?, rate_limit_reset = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.db.execute_query(query, (remaining, reset_time.isoformat(), account_id), fetch=False)
    
    # Subreddit Management
    def create_subreddit(self, subreddit: Subreddit) -> int:
        """Create or update subreddit"""
        query = """
            INSERT OR REPLACE INTO subreddits 
            (name, display_name, title, description, public_description, subscribers, 
             active_users, category, is_nsfw, subreddit_type, created_utc, icon_img, 
             banner_img, url, is_favorite, is_monitored, scrape_frequency_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """
        params = (
            subreddit.name, subreddit.display_name, subreddit.title,
            subreddit.description, subreddit.public_description, subreddit.subscribers,
            subreddit.active_users, subreddit.category, subreddit.is_nsfw,
            subreddit.subreddit_type, subreddit.created_utc, subreddit.icon_img,
            subreddit.banner_img, subreddit.url, subreddit.is_favorite,
            subreddit.is_monitored, subreddit.scrape_frequency_hours
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            subreddit_id = cursor.fetchone()[0]
            conn.commit()
            return subreddit_id
    
    def get_monitored_subreddits(self) -> List[Subreddit]:
        """Get all monitored subreddits"""
        query = """
            SELECT * FROM subreddits 
            WHERE is_monitored = 1 
            ORDER BY subscribers DESC
        """
        results = self.db.execute_query(query)
        
        subreddits = []
        for row in results:
            subreddit = Subreddit(
                id=row['id'],
                name=row['name'],
                display_name=row['display_name'],
                title=row['title'],
                description=row['description'],
                subscribers=row['subscribers'],
                is_monitored=bool(row['is_monitored']),
                last_scraped=datetime.fromisoformat(row['last_scraped']) if row['last_scraped'] else None,
                scrape_frequency_hours=row['scrape_frequency_hours']
            )
            subreddits.append(subreddit)
        
        return subreddits
    
    def update_subreddit_scraped(self, subreddit_id: int):
        """Update last scraped timestamp"""
        query = """
            UPDATE subreddits 
            SET last_scraped = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.db.execute_query(query, (subreddit_id,), fetch=False)
    
    # Post Management
    def create_post(self, post: RedditPost) -> int:
        """Create a new Reddit post"""
        query = """
            INSERT OR REPLACE INTO reddit_posts
            (reddit_id, subreddit_id, account_id, title, selftext, selftext_html, url, permalink, 
             author, author_flair_text, domain, score, upvote_ratio, num_comments, gilded, 
             awards_count, distinguished, stickied, over_18, spoiler, locked, archived, 
             removed, deleted, post_hint, thumbnail, preview_data, media_data, 
             link_flair_text, created_utc, edited_utc, is_processed, processing_status,
             engagement_rate, velocity_score, trending_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """
        
        params = (
            post.reddit_id, post.subreddit_id, post.account_id, post.title,
            post.selftext, post.selftext_html, post.url, post.permalink,
            post.author, post.author_flair_text, post.domain, post.score,
            post.upvote_ratio, post.num_comments, post.gilded, post.awards_count,
            post.distinguished, post.stickied, post.over_18, post.spoiler,
            post.locked, post.archived, post.removed, post.deleted,
            post.post_hint, post.thumbnail, post.preview_data, post.media_data,
            post.link_flair_text, post.created_utc, post.edited_utc,
            post.is_processed, post.processing_status, post.engagement_rate,
            post.velocity_score, post.trending_score
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            post_id = cursor.fetchone()[0]
            conn.commit()
            return post_id
    
    def get_unprocessed_posts(self, limit: int = 100) -> List[RedditPost]:
        """Get posts that need AI processing"""
        query = """
            SELECT p.*, s.name as subreddit_name
            FROM reddit_posts p
            JOIN subreddits s ON p.subreddit_id = s.id
            WHERE p.is_processed = 0 AND p.processing_status = 'pending'
            ORDER BY p.created_utc DESC
            LIMIT ?
        """
        results = self.db.execute_query(query, (limit,))
        
        posts = []
        for row in results:
            post = RedditPost(
                id=row['id'],
                reddit_id=row['reddit_id'],
                subreddit_id=row['subreddit_id'],
                title=row['title'],
                selftext=row['selftext'],
                author=row['author'],
                score=row['score'],
                num_comments=row['num_comments'],
                created_utc=datetime.fromisoformat(row['created_utc']),
                is_processed=bool(row['is_processed']),
                processing_status=row['processing_status']
            )
            posts.append(post)
        
        return posts
    
    def mark_post_processed(self, post_id: int):
        """Mark post as processed"""
        query = """
            UPDATE reddit_posts 
            SET is_processed = 1, processing_status = 'completed', last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.db.execute_query(query, (post_id,), fetch=False)
    
    # Analysis Management
    def create_analysis(self, analysis: PostAnalysis) -> int:
        """Create post analysis result"""
        query = """
            INSERT INTO post_analysis
            (post_id, analysis_type, analysis_version, score, confidence, result_data,
             keywords_matched, sentiment_score, sentiment_label, business_score,
             lead_potential, category_predicted, category_confidence, processing_time_ms, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """
        
        params = (
            analysis.post_id, analysis.analysis_type, analysis.analysis_version,
            analysis.score, analysis.confidence, analysis.result_data,
            analysis.keywords_matched, analysis.sentiment_score, analysis.sentiment_label,
            analysis.business_score, analysis.lead_potential, analysis.category_predicted,
            analysis.category_confidence, analysis.processing_time_ms, analysis.model_used
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            analysis_id = cursor.fetchone()[0]
            conn.commit()
            return analysis_id
    
    def get_post_analyses(self, post_id: int) -> List[PostAnalysis]:
        """Get all analyses for a post"""
        query = "SELECT * FROM post_analysis WHERE post_id = ? ORDER BY created_at DESC"
        results = self.db.execute_query(query, (post_id,))
        
        analyses = []
        for row in results:
            analysis = PostAnalysis(
                id=row['id'],
                post_id=row['post_id'],
                analysis_type=row['analysis_type'],
                score=row['score'],
                confidence=row['confidence'],
                result_data=row['result_data'],
                keywords_matched=row['keywords_matched'],
                sentiment_score=row['sentiment_score'],
                sentiment_label=row['sentiment_label'],
                business_score=row['business_score'],
                lead_potential=row['lead_potential'],
                category_predicted=row['category_predicted'],
                category_confidence=row['category_confidence'],
                processing_time_ms=row['processing_time_ms'],
                model_used=row['model_used'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
            analyses.append(analysis)
        
        return analyses
    
    # Business Lead Management
    def create_lead(self, lead: BusinessLead) -> int:
        """Create business lead"""
        query = """
            INSERT INTO business_leads
            (post_id, account_id, lead_title, lead_description, business_problem,
             potential_solution, industry_category, company_size_estimate, urgency_level,
             budget_estimate, contact_method, contact_info, reddit_author,
             author_history_summary, lead_score, qualification_status, follow_up_date,
             notes, tags, estimated_value, probability_percent, source_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """
        
        params = (
            lead.post_id, lead.account_id, lead.lead_title, lead.lead_description,
            lead.business_problem, lead.potential_solution, lead.industry_category,
            lead.company_size_estimate, lead.urgency_level, lead.budget_estimate,
            lead.contact_method, lead.contact_info, lead.reddit_author,
            lead.author_history_summary, lead.lead_score, lead.qualification_status,
            lead.follow_up_date, lead.notes, lead.tags, lead.estimated_value,
            lead.probability_percent, lead.source_data
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            lead_id = cursor.fetchone()[0]
            conn.commit()
            return lead_id
    
    def get_high_quality_leads(self, min_score: float = 0.7, limit: int = 50) -> List[Dict]:
        """Get high-quality business leads with context"""
        query = """
            SELECT 
                bl.*, p.title as post_title, p.author as post_author, 
                p.score as post_score, s.name as subreddit_name, p.created_utc as post_date
            FROM business_leads bl
            JOIN reddit_posts p ON bl.post_id = p.id
            JOIN subreddits s ON p.subreddit_id = s.id
            WHERE bl.lead_score >= ? AND bl.qualification_status NOT IN ('closed_won', 'closed_lost')
            ORDER BY bl.lead_score DESC, bl.urgency_level DESC
            LIMIT ?
        """
        
        return self.db.execute_query(query, (min_score, limit))
    
    # Search and Analytics
    def search_posts_fts(self, query: str, limit: int = 50) -> List[Dict]:
        """Full-text search posts"""
        search_query = """
            SELECT 
                p.id, p.title, p.author, p.score, s.name as subreddit,
                snippet(reddit_posts_fts, 1, '<mark>', '</mark>', '...', 32) as snippet
            FROM reddit_posts_fts
            JOIN reddit_posts p ON reddit_posts_fts.rowid = p.id
            JOIN subreddits s ON p.subreddit_id = s.id
            WHERE reddit_posts_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        return self.db.execute_query(search_query, (query, limit))
    
    def get_trending_categories(self, days: int = 7) -> List[Dict]:
        """Get trending business categories"""
        query = """
            SELECT 
                pa.category_predicted as category,
                COUNT(*) as mention_count,
                AVG(pa.score) as avg_score,
                COUNT(CASE WHEN p.created_utc >= datetime('now', '-1 day') THEN 1 END) as recent_mentions,
                MAX(p.score) as top_post_score
            FROM post_analysis pa
            JOIN reddit_posts p ON pa.post_id = p.id
            WHERE pa.analysis_type = 'category'
              AND p.created_utc >= datetime('now', ? || ' days')
              AND pa.category_predicted IS NOT NULL
            GROUP BY pa.category_predicted
            HAVING mention_count >= 3
            ORDER BY recent_mentions DESC, avg_score DESC
        """
        return self.db.execute_query(query, (f"-{days}",))
    
    # Maintenance Operations
    def cleanup_old_data(self, days_old: int = 90):
        """Archive or delete old data"""
        # Archive low-value posts
        archive_query = """
            INSERT INTO archived_content (content_type, original_id, reddit_id, content_data, archive_reason, original_created_at)
            SELECT 
                'post', p.id, p.reddit_id,
                json_object('title', p.title, 'author', p.author, 'score', p.score, 'subreddit_id', p.subreddit_id),
                'automated_cleanup',
                p.created_utc
            FROM reddit_posts p
            LEFT JOIN business_leads bl ON p.id = bl.post_id
            WHERE p.created_utc < datetime('now', ? || ' days')
              AND p.score <= 5 
              AND p.num_comments <= 2
              AND bl.id IS NULL  -- Don't archive posts with leads
              AND p.is_archived = 0
        """
        
        # Mark posts as archived
        mark_archived_query = """
            UPDATE reddit_posts 
            SET is_archived = 1, archived_at = datetime('now'), archive_reason = 'automated_cleanup'
            WHERE created_utc < datetime('now', ? || ' days')
              AND score <= 5 
              AND num_comments <= 2
              AND id NOT IN (SELECT post_id FROM business_leads WHERE post_id IS NOT NULL)
              AND is_archived = 0
        """
        
        with self.db.get_connection() as conn:
            conn.execute(archive_query, (f"-{days_old}",))
            conn.execute(mark_archived_query, (f"-{days_old}",))
            conn.commit()
    
    def optimize_database(self):
        """Optimize database performance"""
        with self.db.get_connection() as conn:
            conn.execute("ANALYZE")
            conn.execute("PRAGMA optimize")
            # Update FTS index
            conn.execute("INSERT INTO reddit_posts_fts(reddit_posts_fts) VALUES('optimize')")
            conn.commit()


# Usage Example
def main():
    """Example usage of the database system"""
    # Initialize database
    db_manager = DatabaseManager("test_reddit.db")
    reddit_data = RedditDataManager(db_manager)
    
    # Create a test account
    account = RedditAccount(
        username="test_user",
        account_type="business",
        is_primary=True
    )
    account_id = reddit_data.create_account(account)
    print(f"Created account with ID: {account_id}")
    
    # Create a test subreddit
    subreddit = Subreddit(
        name="entrepreneur",
        display_name="r/entrepreneur",
        title="Entrepreneur",
        subscribers=1000000,
        is_monitored=True
    )
    subreddit_id = reddit_data.create_subreddit(subreddit)
    print(f"Created subreddit with ID: {subreddit_id}")
    
    # Create a test post
    post = RedditPost(
        reddit_id="test123",
        subreddit_id=subreddit_id,
        title="Need help automating my business processes",
        selftext="I spend hours every day manually entering data...",
        author="business_owner",
        score=25,
        num_comments=5
    )
    post_id = reddit_data.create_post(post)
    print(f"Created post with ID: {post_id}")
    
    # Create analysis
    analysis = PostAnalysis(
        post_id=post_id,
        analysis_type="business_opportunity",
        score=0.85,
        confidence=0.92,
        business_score=0.88,
        lead_potential="high",
        keywords_matched='["manual data entry", "automate"]',
        sentiment_score=0.3,
        sentiment_label="problem_seeking"
    )
    analysis_id = reddit_data.create_analysis(analysis)
    print(f"Created analysis with ID: {analysis_id}")
    
    # Create business lead
    lead = BusinessLead(
        post_id=post_id,
        account_id=account_id,
        lead_title="Data Entry Automation Opportunity",
        business_problem="Manual data entry consuming hours daily",
        potential_solution="Custom automation software or RPA implementation",
        industry_category="General Business",
        urgency_level=4,
        lead_score=0.85,
        reddit_author="business_owner"
    )
    lead_id = reddit_data.create_lead(lead)
    print(f"Created lead with ID: {lead_id}")
    
    # Query high-quality leads
    leads = reddit_data.get_high_quality_leads(min_score=0.7)
    print(f"Found {len(leads)} high-quality leads")
    
    # Cleanup and optimize
    reddit_data.cleanup_old_data(days_old=90)
    reddit_data.optimize_database()
    print("Database maintenance completed")


if __name__ == "__main__":
    main()