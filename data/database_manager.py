"""
Database Manager for PersonalizedReddit
Handles SQLite database operations, schema management, and data persistence
"""

import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from contextlib import contextmanager
import logging

from utils.logging_config import get_logger, log_performance

class DatabaseManager:
    """
    Comprehensive database manager for PersonalizedReddit application
    Handles all SQLite operations with connection pooling and transaction management
    """
    
    def __init__(self, db_path: str = "data/personalized_reddit.db"):
        self.db_path = Path(db_path)
        self.logger = get_logger(__name__)
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Connection pool for thread safety
        self._local = threading.local()
        self._lock = threading.Lock()
        
        # Schema version management
        self.current_schema_version = 1
        
        # Initialize database
        self.initialize_database()
        
        self.logger.info(f"Database manager initialized with database: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            
            # Enable foreign keys and set pragmas
            cursor = self._local.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = 10000")
            cursor.execute("PRAGMA temp_store = MEMORY")
            cursor.close()
        
        return self._local.connection
    
    @contextmanager
    def get_cursor(self, commit: bool = True):
        """Context manager for database operations"""
        connection = self._get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    
    def initialize_database(self):
        """Initialize database with comprehensive schema"""
        try:
            # For reliability, use the built-in comprehensive schema instead of file parsing
            self._create_comprehensive_schema()
            self.logger.info("Database schema initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise
    
    def _create_basic_schema(self):
        """Create basic schema if schema file is not available"""
        basic_schema = """
        CREATE TABLE IF NOT EXISTS reddit_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            access_token TEXT,
            refresh_token TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reddit_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            selftext TEXT,
            author TEXT,
            subreddit TEXT,
            score INTEGER DEFAULT 0,
            num_comments INTEGER DEFAULT 0,
            created_utc TIMESTAMP,
            retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS post_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            business_score REAL DEFAULT 0.0,
            sentiment_score REAL DEFAULT 0.0,
            keywords_matched TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES reddit_posts(id)
        );
        
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with self.get_cursor() as cursor:
            cursor.executescript(basic_schema)
        
        self.logger.info("Basic database schema created")
    
    def _create_comprehensive_schema(self):
        """Create comprehensive schema for PersonalizedReddit"""
        
        # Core tables creation SQL
        schema_statements = [
            # Reddit accounts table
            """
            CREATE TABLE IF NOT EXISTS reddit_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                account_type TEXT DEFAULT 'personal',
                is_active BOOLEAN DEFAULT 1,
                is_primary BOOLEAN DEFAULT 0,
                rate_limit_remaining INTEGER DEFAULT 60,
                rate_limit_reset TIMESTAMP,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # User preferences table
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT,
                preference_type TEXT DEFAULT 'string',
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE,
                UNIQUE(account_id, preference_key)
            )
            """,
            
            # App settings table
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type TEXT DEFAULT 'string',
                description TEXT,
                is_system BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Subreddits table
            """
            CREATE TABLE IF NOT EXISTS subreddits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT,
                title TEXT,
                description TEXT,
                public_description TEXT,
                subscribers INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                category TEXT,
                is_nsfw BOOLEAN DEFAULT 0,
                is_quarantined BOOLEAN DEFAULT 0,
                subreddit_type TEXT DEFAULT 'public',
                created_utc TIMESTAMP,
                url TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                is_monitored BOOLEAN DEFAULT 1,
                last_scraped TIMESTAMP,
                scrape_frequency_hours INTEGER DEFAULT 24,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Reddit posts table
            """
            CREATE TABLE IF NOT EXISTS reddit_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reddit_id TEXT UNIQUE NOT NULL,
                subreddit_id INTEGER,
                account_id INTEGER,
                title TEXT NOT NULL,
                selftext TEXT,
                selftext_html TEXT,
                url TEXT,
                permalink TEXT,
                author TEXT,
                author_flair_text TEXT,
                domain TEXT,
                score INTEGER DEFAULT 0,
                upvote_ratio REAL DEFAULT 0.0,
                num_comments INTEGER DEFAULT 0,
                gilded INTEGER DEFAULT 0,
                awards_count INTEGER DEFAULT 0,
                distinguished TEXT,
                stickied BOOLEAN DEFAULT 0,
                over_18 BOOLEAN DEFAULT 0,
                spoiler BOOLEAN DEFAULT 0,
                locked BOOLEAN DEFAULT 0,
                archived BOOLEAN DEFAULT 0,
                removed BOOLEAN DEFAULT 0,
                deleted BOOLEAN DEFAULT 0,
                post_hint TEXT,
                thumbnail TEXT,
                preview_data TEXT,
                media_data TEXT,
                link_flair_text TEXT,
                created_utc TIMESTAMP NOT NULL,
                edited_utc TIMESTAMP,
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_processed BOOLEAN DEFAULT 0,
                processing_status TEXT DEFAULT 'pending',
                FOREIGN KEY (subreddit_id) REFERENCES subreddits(id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
            )
            """,
            
            # Reddit comments table
            """
            CREATE TABLE IF NOT EXISTS reddit_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reddit_id TEXT UNIQUE NOT NULL,
                post_id INTEGER NOT NULL,
                parent_comment_id INTEGER,
                author TEXT,
                body TEXT,
                body_html TEXT,
                score INTEGER DEFAULT 0,
                ups INTEGER DEFAULT 0,
                downs INTEGER DEFAULT 0,
                gilded INTEGER DEFAULT 0,
                awards_count INTEGER DEFAULT 0,
                distinguished TEXT,
                stickied BOOLEAN DEFAULT 0,
                depth INTEGER DEFAULT 0,
                comment_order INTEGER DEFAULT 0,
                is_submitter BOOLEAN DEFAULT 0,
                controversiality INTEGER DEFAULT 0,
                created_utc TIMESTAMP NOT NULL,
                edited_utc TIMESTAMP,
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES reddit_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_comment_id) REFERENCES reddit_comments(id) ON DELETE CASCADE
            )
            """,
            
            # Post analysis table
            """
            CREATE TABLE IF NOT EXISTS post_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_version TEXT DEFAULT '1.0',
                score REAL DEFAULT 0.0,
                confidence REAL DEFAULT 0.0,
                result_data TEXT,
                keywords_matched TEXT,
                sentiment_score REAL DEFAULT 0.0,
                sentiment_label TEXT,
                business_score REAL DEFAULT 0.0,
                lead_potential TEXT DEFAULT 'low',
                category_predicted TEXT,
                category_confidence REAL DEFAULT 0.0,
                processing_time_ms INTEGER,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES reddit_posts(id) ON DELETE CASCADE
            )
            """,
            
            # Business leads table
            """
            CREATE TABLE IF NOT EXISTS business_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                account_id INTEGER,
                lead_title TEXT NOT NULL,
                lead_description TEXT,
                business_problem TEXT,
                potential_solution TEXT,
                industry_category TEXT,
                company_size_estimate TEXT,
                urgency_level INTEGER DEFAULT 1,
                budget_estimate TEXT,
                contact_method TEXT,
                contact_info TEXT,
                reddit_author TEXT,
                author_history_summary TEXT,
                lead_score REAL DEFAULT 0.0,
                qualification_status TEXT DEFAULT 'unqualified',
                follow_up_date DATE,
                notes TEXT,
                tags TEXT,
                estimated_value DECIMAL(10,2),
                probability_percent INTEGER DEFAULT 0,
                source_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES reddit_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
            )
            """,
            
            # User interactions table
            """
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                content_id INTEGER NOT NULL,
                interaction_type TEXT NOT NULL,
                interaction_data TEXT,
                duration_seconds INTEGER DEFAULT 0,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
            )
            """,
            
            # Export history table
            """
            CREATE TABLE IF NOT EXISTS export_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                export_type TEXT NOT NULL,
                export_format TEXT NOT NULL,
                file_name TEXT,
                file_path TEXT,
                file_size_bytes INTEGER,
                record_count INTEGER,
                date_range_start DATE,
                date_range_end DATE,
                filters_applied TEXT,
                export_parameters TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
            )
            """,
            
            # User sessions table
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                account_id INTEGER,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                device_type TEXT,
                pages_visited INTEGER DEFAULT 0,
                actions_performed INTEGER DEFAULT 0,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                session_data TEXT,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
            )
            """,
            
            # AI recommendations table
            """
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                recommendation_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_item_type TEXT,
                target_item_id TEXT,
                recommendation_data TEXT,
                confidence_score REAL DEFAULT 0.0,
                priority_score REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending',
                expires_at TIMESTAMP,
                user_feedback TEXT,
                feedback_score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
            )
            """,
            
            # Keyword sets table
            """
            CREATE TABLE IF NOT EXISTS keyword_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                keywords TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                is_active BOOLEAN DEFAULT 1,
                case_sensitive BOOLEAN DEFAULT 0,
                match_type TEXT DEFAULT 'partial',
                created_by INTEGER,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES reddit_accounts(id) ON DELETE SET NULL
            )
            """
        ]
        
        # Create indexes
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_reddit_accounts_username ON reddit_accounts(username)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_accounts_active ON reddit_accounts(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_subreddits_name ON subreddits(name)",
            "CREATE INDEX IF NOT EXISTS idx_subreddits_monitored ON subreddits(is_monitored)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_posts_reddit_id ON reddit_posts(reddit_id)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_posts_subreddit ON reddit_posts(subreddit_id)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_posts_created_utc ON reddit_posts(created_utc)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_posts_score ON reddit_posts(score)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_posts_author ON reddit_posts(author)",
            "CREATE INDEX IF NOT EXISTS idx_reddit_posts_processed ON reddit_posts(is_processed)",
            "CREATE INDEX IF NOT EXISTS idx_post_analysis_post_id ON post_analysis(post_id)",
            "CREATE INDEX IF NOT EXISTS idx_post_analysis_type ON post_analysis(analysis_type)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_post_id ON business_leads(post_id)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_score ON business_leads(lead_score)",
            "CREATE INDEX IF NOT EXISTS idx_user_interactions_account ON user_interactions(account_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_interactions_content ON user_interactions(content_type, content_id)"
        ]
        
        # Execute all statements
        with self.get_cursor() as cursor:
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            
            # Create tables
            for statement in schema_statements:
                try:
                    cursor.execute(statement.strip())
                except sqlite3.Error as e:
                    if "already exists" not in str(e).lower():
                        self.logger.warning(f"Table creation failed: {e}")
            
            # Create indexes
            for statement in index_statements:
                try:
                    cursor.execute(statement.strip())
                except sqlite3.Error as e:
                    if "already exists" not in str(e).lower():
                        self.logger.warning(f"Index creation failed: {e}")
            
            # Insert default settings
            self._insert_default_settings(cursor)
        
        self.logger.info("Comprehensive database schema created")
    
    def _insert_default_settings(self, cursor):
        """Insert default application settings"""
        default_settings = [
            ('app_version', '1.0.0', 'string', 'Current application version', 1),
            ('max_posts_per_subreddit', '100', 'integer', 'Maximum posts to fetch per subreddit per scrape', 0),
            ('scrape_interval_hours', '6', 'integer', 'Default hours between subreddit scrapes', 0),
            ('ai_processing_enabled', 'true', 'boolean', 'Enable AI analysis of posts', 0),
            ('export_directory', './Exports', 'string', 'Default directory for exports', 0),
            ('cache_max_size_mb', '500', 'integer', 'Maximum cache size in megabytes', 0),
            ('session_timeout_hours', '24', 'integer', 'User session timeout in hours', 0),
            ('performance_monitoring', 'true', 'boolean', 'Enable performance metrics collection', 1),
            ('auto_cleanup_days', '90', 'integer', 'Days after which to archive old data', 0),
            ('reddit_api_user_agent', 'PersonalizedReddit/1.0', 'string', 'User agent for Reddit API requests', 1)
        ]
        
        for setting_key, setting_value, setting_type, description, is_system in default_settings:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO app_settings 
                    (setting_key, setting_value, setting_type, description, is_system)
                    VALUES (?, ?, ?, ?, ?)
                """, (setting_key, setting_value, setting_type, description, is_system))
            except sqlite3.Error as e:
                self.logger.warning(f"Failed to insert setting {setting_key}: {e}")
    
    # Reddit Accounts Management
    @log_performance
    def save_reddit_account(self, username: str, access_token: str = None, 
                           refresh_token: str = None, is_primary: bool = False) -> int:
        """Save Reddit account credentials"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO reddit_accounts 
                (username, access_token, refresh_token, is_primary, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (username, access_token, refresh_token, is_primary))
            
            account_id = cursor.lastrowid
            self.logger.info(f"Saved Reddit account: {username}")
            return account_id
    
    def get_reddit_account(self, username: str) -> Optional[Dict]:
        """Get Reddit account by username"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM reddit_accounts WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_active_reddit_accounts(self) -> List[Dict]:
        """Get all active Reddit accounts"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM reddit_accounts WHERE is_active = 1
                ORDER BY is_primary DESC, created_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Subreddit Management
    def save_subreddit(self, subreddit_data: Dict) -> int:
        """Save subreddit data"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO subreddits 
                (name, display_name, title, description, subscribers, active_users,
                 category, is_nsfw, subreddit_type, created_utc, url, is_monitored)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                subreddit_data.get('name'),
                subreddit_data.get('display_name'),
                subreddit_data.get('title'),
                subreddit_data.get('description'),
                subreddit_data.get('subscribers', 0),
                subreddit_data.get('active_users', 0),
                subreddit_data.get('category'),
                subreddit_data.get('is_nsfw', False),
                subreddit_data.get('subreddit_type', 'public'),
                subreddit_data.get('created_utc'),
                subreddit_data.get('url'),
                subreddit_data.get('is_monitored', True)
            ))
            
            subreddit_id = cursor.lastrowid
            self.logger.debug(f"Saved subreddit: {subreddit_data.get('name')}")
            return subreddit_id
    
    def get_subreddit_by_name(self, name: str) -> Optional[Dict]:
        """Get subreddit by name"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM subreddits WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_or_create_subreddit(self, name: str, display_name: str = None) -> int:
        """Get existing subreddit ID or create new one"""
        subreddit = self.get_subreddit_by_name(name)
        if subreddit:
            return subreddit['id']
        
        subreddit_data = {
            'name': name,
            'display_name': display_name or name,
            'is_monitored': True
        }
        return self.save_subreddit(subreddit_data)
    
    # Posts Management
    @log_performance
    def save_reddit_post(self, post_data: Dict) -> int:
        """Save Reddit post data"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO reddit_posts 
                (reddit_id, subreddit_id, account_id, title, selftext, author, score, num_comments, 
                 created_utc, url, permalink, upvote_ratio, over_18, stickied, locked, 
                 archived, spoiler, retrieved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                post_data.get('reddit_id'),
                post_data.get('subreddit_id'),
                post_data.get('account_id'),
                post_data.get('title'),
                post_data.get('text') or post_data.get('selftext'),
                post_data.get('author'),
                post_data.get('score', 0),
                post_data.get('num_comments', 0),
                post_data.get('created_utc'),
                post_data.get('url'),
                post_data.get('permalink'),
                post_data.get('upvote_ratio', 0.0),
                post_data.get('over_18', False),
                post_data.get('stickied', False),
                post_data.get('locked', False),
                post_data.get('archived', False),
                post_data.get('spoiler', False)
            ))
            
            post_id = cursor.lastrowid
            self.logger.debug(f"Saved post: {post_data.get('reddit_id')}")
            return post_id
    
    def get_reddit_post(self, reddit_id: str) -> Optional[Dict]:
        """Get Reddit post by reddit_id"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM reddit_posts WHERE reddit_id = ?
            """, (reddit_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_posts_by_subreddit(self, subreddit: str, limit: int = 100) -> List[Dict]:
        """Get posts from a specific subreddit"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT rp.*, s.name as subreddit_name 
                FROM reddit_posts rp
                JOIN subreddits s ON rp.subreddit_id = s.id
                WHERE s.name = ? 
                ORDER BY rp.created_utc DESC 
                LIMIT ?
            """, (subreddit, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_posts(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get recent posts within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM reddit_posts 
                WHERE retrieved_at > ? 
                ORDER BY created_utc DESC 
                LIMIT ?
            """, (cutoff_time, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Post Analysis Management
    @log_performance
    def save_post_analysis(self, post_id: int, analysis_data: Dict) -> int:
        """Save post analysis results"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO post_analysis 
                (post_id, analysis_type, score, confidence, result_data, 
                 sentiment_score, business_score, keywords_matched, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                post_id,
                analysis_data.get('analysis_type', 'general'),
                analysis_data.get('score', 0.0),
                analysis_data.get('confidence', 0.0),
                json.dumps(analysis_data.get('result_data', {})),
                analysis_data.get('sentiment_score', 0.0),
                analysis_data.get('business_score', 0.0),
                json.dumps(analysis_data.get('keywords_matched', []))
            ))
            
            analysis_id = cursor.lastrowid
            self.logger.debug(f"Saved analysis for post_id: {post_id}")
            return analysis_id
    
    def get_post_analysis(self, post_id: int) -> List[Dict]:
        """Get all analysis for a post"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM post_analysis WHERE post_id = ?
                ORDER BY created_at DESC
            """, (post_id,))
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON fields
                if data.get('result_data'):
                    try:
                        data['result_data'] = json.loads(data['result_data'])
                    except:
                        data['result_data'] = {}
                
                if data.get('keywords_matched'):
                    try:
                        data['keywords_matched'] = json.loads(data['keywords_matched'])
                    except:
                        data['keywords_matched'] = []
                
                results.append(data)
            
            return results
    
    # Business Leads Management
    def save_business_lead(self, lead_data: Dict) -> int:
        """Save business lead data"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO business_leads 
                (post_id, lead_title, lead_description, business_problem, 
                 industry_category, urgency_level, lead_score, qualification_status,
                 reddit_author, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                lead_data.get('post_id'),
                lead_data.get('lead_title'),
                lead_data.get('lead_description'),
                lead_data.get('business_problem'),
                lead_data.get('industry_category'),
                lead_data.get('urgency_level', 1),
                lead_data.get('lead_score', 0.0),
                lead_data.get('qualification_status', 'unqualified'),
                lead_data.get('reddit_author'),
                lead_data.get('notes')
            ))
            
            lead_id = cursor.lastrowid
            self.logger.info(f"Saved business lead: {lead_data.get('lead_title')}")
            return lead_id
    
    def get_business_leads(self, status: str = None, min_score: float = None) -> List[Dict]:
        """Get business leads with optional filtering"""
        query = "SELECT * FROM business_leads WHERE 1=1"
        params = []
        
        if status:
            query += " AND qualification_status = ?"
            params.append(status)
        
        if min_score:
            query += " AND lead_score >= ?"
            params.append(min_score)
        
        query += " ORDER BY lead_score DESC, created_at DESC"
        
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_leads_with_posts(self, limit: int = 50) -> List[Dict]:
        """Get business leads with their associated post data"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT bl.*, rp.title as post_title, rp.author as post_author,
                       rp.subreddit, rp.created_utc as post_created_utc
                FROM business_leads bl
                JOIN reddit_posts rp ON bl.post_id = rp.id
                ORDER BY bl.lead_score DESC, bl.created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # User Interactions and Analytics
    def record_user_interaction(self, account_id: int, content_type: str, 
                              content_id: int, interaction_type: str, 
                              duration: int = None) -> int:
        """Record user interaction for analytics"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_interactions 
                (account_id, content_type, content_id, interaction_type, 
                 duration_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (account_id, content_type, content_id, interaction_type, duration))
            
            return cursor.lastrowid
    
    def get_user_analytics(self, account_id: int, days: int = 30) -> Dict:
        """Get user analytics summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_cursor(commit=False) as cursor:
            # Get interaction counts
            cursor.execute("""
                SELECT interaction_type, COUNT(*) as count
                FROM user_interactions 
                WHERE account_id = ? AND created_at > ?
                GROUP BY interaction_type
            """, (account_id, cutoff_date))
            
            interactions = {row['interaction_type']: row['count'] for row in cursor.fetchall()}
            
            # Get total time spent
            cursor.execute("""
                SELECT SUM(duration_seconds) as total_seconds
                FROM user_interactions 
                WHERE account_id = ? AND created_at > ? AND duration_seconds IS NOT NULL
            """, (account_id, cutoff_date))
            
            total_time = cursor.fetchone()['total_seconds'] or 0
            
            return {
                'interactions': interactions,
                'total_time_seconds': total_time,
                'period_days': days,
                'generated_at': datetime.now().isoformat()
            }
    
    # Application Settings
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT setting_value, setting_type FROM app_settings WHERE setting_key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if not row:
                return default
            
            value = row['setting_value']
            setting_type = row['setting_type'] if 'setting_type' in row.keys() else 'string'
            
            # Convert value based on type
            if setting_type == 'boolean':
                return value.lower() == 'true'
            elif setting_type == 'integer':
                return int(value)
            elif setting_type == 'json':
                return json.loads(value)
            else:
                return value
    
    def set_setting(self, key: str, value: Any, setting_type: str = None) -> None:
        """Set application setting"""
        # Auto-detect type if not specified
        if setting_type is None:
            if isinstance(value, bool):
                setting_type = 'boolean'
                value = str(value).lower()
            elif isinstance(value, int):
                setting_type = 'integer'
                value = str(value)
            elif isinstance(value, (dict, list)):
                setting_type = 'json'
                value = json.dumps(value)
            else:
                setting_type = 'string'
                value = str(value)
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO app_settings 
                (setting_key, setting_value, setting_type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, setting_type))
    
    # Search and Query Methods
    def search_posts(self, query: str, subreddit: str = None, limit: int = 50) -> List[Dict]:
        """Search posts by text content"""
        base_query = """
            SELECT * FROM reddit_posts 
            WHERE (title LIKE ? OR selftext LIKE ?)
        """
        params = [f'%{query}%', f'%{query}%']
        
        if subreddit:
            base_query += " AND subreddit = ?"
            params.append(subreddit)
        
        base_query += " ORDER BY score DESC, created_utc DESC LIMIT ?"
        params.append(limit)
        
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(base_query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_subreddits(self, limit: int = 20) -> List[Dict]:
        """Get top subreddits by post count"""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT subreddit, COUNT(*) as post_count, 
                       AVG(score) as avg_score,
                       MAX(created_utc) as latest_post
                FROM reddit_posts 
                GROUP BY subreddit 
                ORDER BY post_count DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Database Maintenance
    def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """Clean up old data beyond specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleanup_stats = {}
        
        with self.get_cursor() as cursor:
            # Clean old interactions
            cursor.execute("""
                DELETE FROM user_interactions WHERE created_at < ?
            """, (cutoff_date,))
            cleanup_stats['interactions_deleted'] = cursor.rowcount
            
            # Clean old analysis
            cursor.execute("""
                DELETE FROM post_analysis WHERE created_at < ?
            """, (cutoff_date,))
            cleanup_stats['analysis_deleted'] = cursor.rowcount
            
            # Clean old posts (but keep posts with leads)
            cursor.execute("""
                DELETE FROM reddit_posts 
                WHERE retrieved_at < ? 
                AND id NOT IN (SELECT DISTINCT post_id FROM business_leads)
            """, (cutoff_date,))
            cleanup_stats['posts_deleted'] = cursor.rowcount
        
        self.logger.info(f"Database cleanup completed: {cleanup_stats}")
        return cleanup_stats
    
    def vacuum_database(self):
        """Vacuum database to reclaim space"""
        with self.get_cursor() as cursor:
            cursor.execute("VACUUM")
        self.logger.info("Database vacuumed successfully")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        tables = [
            'reddit_accounts', 'reddit_posts', 'post_analysis',
            'business_leads', 'user_interactions', 'app_settings'
        ]
        
        with self.get_cursor(commit=False) as cursor:
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[f'{table}_count'] = cursor.fetchone()['count']
                except sqlite3.Error:
                    stats[f'{table}_count'] = 0
            
            # Get database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size_bytes'] = cursor.fetchone()['size']
        
        return stats
    
    def close(self):
        """Close database connections"""
        try:
            if hasattr(self._local, 'connection') and self._local.connection:
                self._local.connection.close()
                self._local.connection = None
            
            self.logger.info("Database connections closed")
            
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Test the database manager
    db = DatabaseManager("test_db.sqlite")
    
    print("=== Database Manager Test ===")
    print(f"Database stats: {db.get_database_stats()}")
    
    # Test saving and retrieving data
    account_id = db.save_reddit_account("test_user", "token123", "refresh456")
    print(f"Saved account ID: {account_id}")
    
    account = db.get_reddit_account("test_user")
    print(f"Retrieved account: {account}")
    
    db.close()