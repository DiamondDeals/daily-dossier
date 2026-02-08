-- =============================================================================
-- PersonalizedReddit Database Schema
-- SQLite Implementation for Reddit Content Analysis and AI Processing
-- =============================================================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;

-- =============================================================================
-- USER MANAGEMENT TABLES
-- =============================================================================

-- Main user accounts table for Reddit authentication
CREATE TABLE reddit_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    account_type TEXT DEFAULT 'personal' CHECK (account_type IN ('personal', 'business')),
    is_active BOOLEAN DEFAULT 1,
    is_primary BOOLEAN DEFAULT 0,
    rate_limit_remaining INTEGER DEFAULT 60,
    rate_limit_reset TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences and settings
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT,
    preference_type TEXT DEFAULT 'string' CHECK (preference_type IN ('string', 'integer', 'boolean', 'json')),
    category TEXT DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE,
    UNIQUE(account_id, preference_key)
);

-- Application settings and configuration
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type TEXT DEFAULT 'string' CHECK (setting_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    is_system BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- REDDIT CONTENT STORAGE TABLES
-- =============================================================================

-- Subreddits tracking and metadata
CREATE TABLE subreddits (
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
    icon_img TEXT,
    banner_img TEXT,
    primary_color TEXT,
    key_color TEXT,
    lang TEXT DEFAULT 'en',
    whitelist_status TEXT,
    url TEXT,
    is_favorite BOOLEAN DEFAULT 0,
    is_monitored BOOLEAN DEFAULT 1,
    last_scraped TIMESTAMP,
    scrape_frequency_hours INTEGER DEFAULT 24,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reddit posts storage with comprehensive metadata
CREATE TABLE reddit_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reddit_id TEXT UNIQUE NOT NULL,
    subreddit_id INTEGER NOT NULL,
    account_id INTEGER,
    title TEXT NOT NULL,
    selftext TEXT,
    selftext_html TEXT,
    url TEXT,
    permalink TEXT,
    author TEXT,
    author_flair_text TEXT,
    author_flair_css_class TEXT,
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
    preview_data TEXT, -- JSON for preview images/videos
    media_data TEXT, -- JSON for media information
    link_flair_text TEXT,
    link_flair_css_class TEXT,
    created_utc TIMESTAMP NOT NULL,
    edited_utc TIMESTAMP,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT 0,
    processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    FOREIGN KEY (subreddit_id) REFERENCES subreddits(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- Reddit comments storage
CREATE TABLE reddit_comments (
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
);

-- =============================================================================
-- AI ANALYTICS AND PROCESSING TABLES
-- =============================================================================

-- AI analysis results for posts
CREATE TABLE post_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL CHECK (analysis_type IN ('keyword_match', 'sentiment', 'business_opportunity', 'lead_score', 'category')),
    analysis_version TEXT DEFAULT '1.0',
    score REAL DEFAULT 0.0,
    confidence REAL DEFAULT 0.0,
    result_data TEXT, -- JSON for detailed results
    keywords_matched TEXT, -- JSON array of matched keywords
    sentiment_score REAL DEFAULT 0.0,
    sentiment_label TEXT,
    business_score REAL DEFAULT 0.0,
    lead_potential TEXT DEFAULT 'low' CHECK (lead_potential IN ('low', 'medium', 'high', 'very_high')),
    category_predicted TEXT,
    category_confidence REAL DEFAULT 0.0,
    processing_time_ms INTEGER,
    model_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES reddit_posts(id) ON DELETE CASCADE
);

-- AI-generated summaries and insights
CREATE TABLE content_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL CHECK (content_type IN ('post', 'comment', 'thread')),
    content_id INTEGER NOT NULL,
    summary_type TEXT NOT NULL CHECK (summary_type IN ('brief', 'detailed', 'business_insight', 'key_points')),
    summary_text TEXT NOT NULL,
    key_points TEXT, -- JSON array
    entities_extracted TEXT, -- JSON for named entities
    topics TEXT, -- JSON array of topics
    action_items TEXT, -- JSON array of potential actions
    urgency_score REAL DEFAULT 0.0,
    relevance_score REAL DEFAULT 0.0,
    word_count INTEGER,
    reading_time_seconds INTEGER,
    language_detected TEXT DEFAULT 'en',
    model_used TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI recommendations and suggestions
CREATE TABLE ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN ('subreddit', 'post', 'keyword', 'schedule', 'opportunity')),
    title TEXT NOT NULL,
    description TEXT,
    target_item_type TEXT, -- 'post', 'subreddit', 'keyword'
    target_item_id TEXT,
    recommendation_data TEXT, -- JSON with detailed recommendation
    confidence_score REAL DEFAULT 0.0,
    priority_score REAL DEFAULT 0.0,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'viewed', 'accepted', 'dismissed', 'acted_upon')),
    expires_at TIMESTAMP,
    user_feedback TEXT,
    feedback_score INTEGER DEFAULT 0 CHECK (feedback_score BETWEEN -2 AND 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
);

-- =============================================================================
-- USER ACTIVITY AND ENGAGEMENT TRACKING
-- =============================================================================

-- User interactions with posts
CREATE TABLE user_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('post', 'comment', 'subreddit')),
    content_id INTEGER NOT NULL,
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('view', 'click', 'save', 'export', 'share', 'upvote', 'downvote', 'comment', 'bookmark')),
    interaction_data TEXT, -- JSON for additional context
    duration_seconds INTEGER DEFAULT 0,
    session_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
);

-- User saved/bookmarked content
CREATE TABLE saved_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('post', 'comment', 'subreddit', 'thread')),
    content_id INTEGER NOT NULL,
    collection_name TEXT DEFAULT 'default',
    notes TEXT,
    tags TEXT, -- JSON array
    priority INTEGER DEFAULT 0 CHECK (priority BETWEEN 0 AND 5),
    reminder_date TIMESTAMP,
    is_archived BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE,
    UNIQUE(account_id, content_type, content_id, collection_name)
);

-- User engagement patterns and analytics
CREATE TABLE engagement_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    date_period TEXT NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    posts_viewed INTEGER DEFAULT 0,
    posts_saved INTEGER DEFAULT 0,
    posts_exported INTEGER DEFAULT 0,
    comments_read INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    subreddits_visited INTEGER DEFAULT 0,
    searches_performed INTEGER DEFAULT 0,
    ai_recommendations_viewed INTEGER DEFAULT 0,
    ai_recommendations_accepted INTEGER DEFAULT 0,
    top_subreddits TEXT, -- JSON array
    top_keywords TEXT, -- JSON array
    peak_activity_hour INTEGER,
    average_session_duration INTEGER,
    bounce_rate REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE,
    UNIQUE(account_id, date_period, period_start)
);

-- =============================================================================
-- LEAD MANAGEMENT AND EXPORT TRACKING
-- =============================================================================

-- Business leads identified from Reddit posts
CREATE TABLE business_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    account_id INTEGER,
    lead_title TEXT NOT NULL,
    lead_description TEXT,
    business_problem TEXT,
    potential_solution TEXT,
    industry_category TEXT,
    company_size_estimate TEXT,
    urgency_level INTEGER DEFAULT 1 CHECK (urgency_level BETWEEN 1 AND 5),
    budget_estimate TEXT,
    contact_method TEXT,
    contact_info TEXT,
    reddit_author TEXT,
    author_history_summary TEXT,
    lead_score REAL DEFAULT 0.0,
    qualification_status TEXT DEFAULT 'unqualified' CHECK (qualification_status IN ('unqualified', 'qualified', 'contacted', 'in_progress', 'closed_won', 'closed_lost')),
    follow_up_date DATE,
    notes TEXT,
    tags TEXT, -- JSON array
    estimated_value DECIMAL(10,2),
    probability_percent INTEGER DEFAULT 0 CHECK (probability_percent BETWEEN 0 AND 100),
    source_data TEXT, -- JSON with original post data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES reddit_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- Export history and tracking
CREATE TABLE export_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    export_type TEXT NOT NULL CHECK (export_type IN ('posts', 'leads', 'analytics', 'subreddits', 'full_report')),
    export_format TEXT NOT NULL CHECK (export_format IN ('csv', 'json', 'xlsx', 'pdf', 'markdown')),
    file_name TEXT,
    file_path TEXT,
    file_size_bytes INTEGER,
    record_count INTEGER,
    date_range_start DATE,
    date_range_end DATE,
    filters_applied TEXT, -- JSON
    export_parameters TEXT, -- JSON
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- =============================================================================
-- APPLICATION STATE AND SESSION MANAGEMENT
-- =============================================================================

-- User sessions tracking
CREATE TABLE user_sessions (
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
    session_data TEXT, -- JSON for additional session info
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- Application cache management
CREATE TABLE cache_management (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    cache_type TEXT NOT NULL CHECK (cache_type IN ('reddit_api', 'post_content', 'user_data', 'ai_results', 'subreddit_info')),
    data_size_bytes INTEGER,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    is_compressed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance monitoring and metrics
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL CHECK (metric_type IN ('api_response_time', 'db_query_time', 'ai_processing_time', 'export_time', 'scrape_time')),
    metric_name TEXT NOT NULL,
    value_numeric REAL,
    value_text TEXT,
    unit TEXT,
    category TEXT,
    tags TEXT, -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    account_id INTEGER,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- =============================================================================
-- KEYWORD AND SEARCH CONFIGURATION
-- =============================================================================

-- Keyword sets for business opportunity detection
CREATE TABLE keyword_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    category TEXT,
    keywords TEXT NOT NULL, -- JSON array of keywords
    weight REAL DEFAULT 1.0,
    is_active BOOLEAN DEFAULT 1,
    case_sensitive BOOLEAN DEFAULT 0,
    match_type TEXT DEFAULT 'partial' CHECK (match_type IN ('exact', 'partial', 'regex')),
    created_by INTEGER,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- Search queries and results tracking
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    query_text TEXT NOT NULL,
    search_type TEXT DEFAULT 'content' CHECK (search_type IN ('content', 'subreddit', 'user', 'keyword')),
    filters_applied TEXT, -- JSON
    results_count INTEGER DEFAULT 0,
    search_duration_ms INTEGER,
    result_quality_score REAL DEFAULT 0.0,
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================================================

-- Reddit accounts indexes
CREATE INDEX idx_reddit_accounts_username ON reddit_accounts(username);
CREATE INDEX idx_reddit_accounts_active ON reddit_accounts(is_active);
CREATE INDEX idx_reddit_accounts_primary ON reddit_accounts(is_primary);

-- User preferences indexes
CREATE INDEX idx_user_preferences_account_key ON user_preferences(account_id, preference_key);
CREATE INDEX idx_user_preferences_category ON user_preferences(category);

-- Subreddits indexes
CREATE INDEX idx_subreddits_name ON subreddits(name);
CREATE INDEX idx_subreddits_monitored ON subreddits(is_monitored);
CREATE INDEX idx_subreddits_last_scraped ON subreddits(last_scraped);
CREATE INDEX idx_subreddits_subscribers ON subreddits(subscribers);

-- Reddit posts indexes
CREATE INDEX idx_reddit_posts_reddit_id ON reddit_posts(reddit_id);
CREATE INDEX idx_reddit_posts_subreddit ON reddit_posts(subreddit_id);
CREATE INDEX idx_reddit_posts_created_utc ON reddit_posts(created_utc);
CREATE INDEX idx_reddit_posts_score ON reddit_posts(score);
CREATE INDEX idx_reddit_posts_author ON reddit_posts(author);
CREATE INDEX idx_reddit_posts_processed ON reddit_posts(is_processed);
CREATE INDEX idx_reddit_posts_status ON reddit_posts(processing_status);
CREATE INDEX idx_reddit_posts_composite ON reddit_posts(subreddit_id, created_utc, score);

-- Comments indexes
CREATE INDEX idx_reddit_comments_post_id ON reddit_comments(post_id);
CREATE INDEX idx_reddit_comments_parent_id ON reddit_comments(parent_comment_id);
CREATE INDEX idx_reddit_comments_created_utc ON reddit_comments(created_utc);
CREATE INDEX idx_reddit_comments_score ON reddit_comments(score);

-- Post analysis indexes
CREATE INDEX idx_post_analysis_post_id ON post_analysis(post_id);
CREATE INDEX idx_post_analysis_type ON post_analysis(analysis_type);
CREATE INDEX idx_post_analysis_score ON post_analysis(score);
CREATE INDEX idx_post_analysis_lead_potential ON post_analysis(lead_potential);

-- Content summaries indexes
CREATE INDEX idx_content_summaries_content ON content_summaries(content_type, content_id);
CREATE INDEX idx_content_summaries_type ON content_summaries(summary_type);
CREATE INDEX idx_content_summaries_created ON content_summaries(created_at);

-- AI recommendations indexes
CREATE INDEX idx_ai_recommendations_account ON ai_recommendations(account_id);
CREATE INDEX idx_ai_recommendations_type ON ai_recommendations(recommendation_type);
CREATE INDEX idx_ai_recommendations_status ON ai_recommendations(status);
CREATE INDEX idx_ai_recommendations_priority ON ai_recommendations(priority_score);
CREATE INDEX idx_ai_recommendations_expires ON ai_recommendations(expires_at);

-- User interactions indexes
CREATE INDEX idx_user_interactions_account ON user_interactions(account_id);
CREATE INDEX idx_user_interactions_content ON user_interactions(content_type, content_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_user_interactions_created ON user_interactions(created_at);
CREATE INDEX idx_user_interactions_session ON user_interactions(session_id);

-- Business leads indexes
CREATE INDEX idx_business_leads_post_id ON business_leads(post_id);
CREATE INDEX idx_business_leads_account ON business_leads(account_id);
CREATE INDEX idx_business_leads_score ON business_leads(lead_score);
CREATE INDEX idx_business_leads_status ON business_leads(qualification_status);
CREATE INDEX idx_business_leads_urgency ON business_leads(urgency_level);
CREATE INDEX idx_business_leads_follow_up ON business_leads(follow_up_date);

-- Export history indexes
CREATE INDEX idx_export_history_account ON export_history(account_id);
CREATE INDEX idx_export_history_type ON export_history(export_type);
CREATE INDEX idx_export_history_created ON export_history(created_at);

-- Sessions indexes
CREATE INDEX idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX idx_user_sessions_account ON user_sessions(account_id);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);
CREATE INDEX idx_user_sessions_start_time ON user_sessions(start_time);

-- Performance metrics indexes
CREATE INDEX idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp);

-- =============================================================================
-- TRIGGERS FOR AUTOMATED MAINTENANCE
-- =============================================================================

-- Update timestamps automatically
CREATE TRIGGER update_reddit_accounts_timestamp 
    AFTER UPDATE ON reddit_accounts
    FOR EACH ROW
    BEGIN
        UPDATE reddit_accounts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_user_preferences_timestamp 
    AFTER UPDATE ON user_preferences
    FOR EACH ROW
    BEGIN
        UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_app_settings_timestamp 
    AFTER UPDATE ON app_settings
    FOR EACH ROW
    BEGIN
        UPDATE app_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_subreddits_timestamp 
    AFTER UPDATE ON subreddits
    FOR EACH ROW
    BEGIN
        UPDATE subreddits SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_reddit_posts_timestamp 
    AFTER UPDATE ON reddit_posts
    FOR EACH ROW
    BEGIN
        UPDATE reddit_posts SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_business_leads_timestamp 
    AFTER UPDATE ON business_leads
    FOR EACH ROW
    BEGIN
        UPDATE business_leads SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Maintain engagement patterns when interactions are added
CREATE TRIGGER update_engagement_patterns_on_interaction
    AFTER INSERT ON user_interactions
    FOR EACH ROW
    BEGIN
        INSERT OR REPLACE INTO engagement_patterns 
        (account_id, date_period, period_start, period_end, posts_viewed, time_spent_seconds, created_at)
        VALUES (
            NEW.account_id,
            'daily',
            date(NEW.created_at),
            date(NEW.created_at),
            CASE WHEN NEW.interaction_type = 'view' THEN 1 ELSE 0 END,
            COALESCE(NEW.duration_seconds, 0),
            CURRENT_TIMESTAMP
        );
    END;

-- Clean up expired cache entries
CREATE TRIGGER cleanup_expired_cache
    AFTER INSERT ON cache_management
    FOR EACH ROW
    WHEN NEW.expires_at IS NOT NULL
    BEGIN
        DELETE FROM cache_management WHERE expires_at < CURRENT_TIMESTAMP;
    END;

-- =============================================================================
-- INITIAL DATA POPULATION
-- =============================================================================

-- Insert default application settings
INSERT OR IGNORE INTO app_settings (setting_key, setting_value, setting_type, description, is_system) VALUES
('app_version', '1.0.0', 'string', 'Current application version', 1),
('max_posts_per_subreddit', '100', 'integer', 'Maximum posts to fetch per subreddit per scrape', 0),
('scrape_interval_hours', '6', 'integer', 'Default hours between subreddit scrapes', 0),
('ai_processing_enabled', 'true', 'boolean', 'Enable AI analysis of posts', 0),
('export_directory', './exports', 'string', 'Default directory for exports', 0),
('cache_max_size_mb', '500', 'integer', 'Maximum cache size in megabytes', 0),
('session_timeout_hours', '24', 'integer', 'User session timeout in hours', 0),
('performance_monitoring', 'true', 'boolean', 'Enable performance metrics collection', 1),
('auto_cleanup_days', '90', 'integer', 'Days after which to archive old data', 0),
('reddit_api_user_agent', 'PersonalizedReddit/1.0', 'string', 'User agent for Reddit API requests', 1);

-- Insert default keyword sets for business opportunity detection
INSERT OR IGNORE INTO keyword_sets (name, description, category, keywords, weight, is_active) VALUES
('Manual Processes', 'Keywords indicating manual, time-consuming work', 'automation', 
'["manual data entry", "copy and paste", "manual process", "doing by hand", "typing everything", "manual work", "tedious task", "repetitive work"]', 
1.5, 1),

('Time Issues', 'Keywords indicating time-related business problems', 'efficiency', 
'["takes hours to", "eating up my time", "time consuming", "waste of time", "too slow", "taking forever", "hours every day", "all day long"]', 
1.3, 1),

('Workflow Problems', 'Keywords indicating workflow and scaling issues', 'workflow', 
'["bottleneck", "cant scale", "workflow issue", "process problem", "inefficient", "broken process", "workflow nightmare"]', 
1.4, 1),

('Data Management', 'Keywords indicating data and file management issues', 'data', 
'["file management nightmare", "duplicate entries", "data mess", "cant find files", "disorganized", "spreadsheet hell", "version control"]', 
1.2, 1),

('Integration Needs', 'Keywords indicating system integration problems', 'integration', 
'["systems dont talk", "manual sync", "integration problem", "cant connect", "different platforms", "switching between", "compatibility issue"]', 
1.6, 1),

('Business Operations', 'Keywords indicating core business operation challenges', 'operations', 
'["inventory tracking", "customer follow-up", "order processing", "invoice management", "lead tracking", "project management", "scheduling nightmare"]', 
1.4, 1),

('Help Requests', 'Keywords indicating someone is asking for help or solutions', 'intent', 
'["need help", "looking for solution", "how do I", "struggling with", "need advice", "recommendations", "better way", "suggestions"]', 
1.1, 1);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View for posts with their analysis scores
CREATE VIEW post_analysis_summary AS
SELECT 
    p.id,
    p.reddit_id,
    p.title,
    p.author,
    p.score as reddit_score,
    p.num_comments,
    p.created_utc,
    s.name as subreddit_name,
    COALESCE(AVG(pa.score), 0) as avg_analysis_score,
    COALESCE(MAX(CASE WHEN pa.analysis_type = 'lead_score' THEN pa.score END), 0) as lead_score,
    COALESCE(MAX(CASE WHEN pa.analysis_type = 'sentiment' THEN pa.sentiment_score END), 0) as sentiment_score,
    COALESCE(MAX(CASE WHEN pa.analysis_type = 'business_opportunity' THEN pa.lead_potential END), 'low') as lead_potential,
    COUNT(pa.id) as analysis_count
FROM reddit_posts p
LEFT JOIN subreddits s ON p.subreddit_id = s.id
LEFT JOIN post_analysis pa ON p.id = pa.post_id
GROUP BY p.id, p.reddit_id, p.title, p.author, p.score, p.num_comments, p.created_utc, s.name;

-- View for business leads with post context
CREATE VIEW business_leads_with_context AS
SELECT 
    bl.*,
    p.title as post_title,
    p.author as post_author,
    p.score as post_score,
    p.num_comments,
    s.name as subreddit_name,
    pa.score as analysis_score
FROM business_leads bl
JOIN reddit_posts p ON bl.post_id = p.id
JOIN subreddits s ON p.subreddit_id = s.id
LEFT JOIN post_analysis pa ON p.id = pa.post_id AND pa.analysis_type = 'lead_score';

-- View for user engagement summary
CREATE VIEW user_engagement_summary AS
SELECT 
    ra.username,
    COUNT(DISTINCT ui.id) as total_interactions,
    COUNT(DISTINCT CASE WHEN ui.interaction_type = 'view' THEN ui.id END) as posts_viewed,
    COUNT(DISTINCT CASE WHEN ui.interaction_type = 'save' THEN ui.id END) as posts_saved,
    COUNT(DISTINCT CASE WHEN ui.interaction_type = 'export' THEN ui.id END) as exports_made,
    AVG(ui.duration_seconds) as avg_interaction_duration,
    COUNT(DISTINCT sc.id) as saved_items,
    COUNT(DISTINCT bl.id) as leads_created,
    MAX(ui.created_at) as last_activity
FROM reddit_accounts ra
LEFT JOIN user_interactions ui ON ra.id = ui.account_id
LEFT JOIN saved_content sc ON ra.id = sc.account_id
LEFT JOIN business_leads bl ON ra.id = bl.account_id
GROUP BY ra.id, ra.username;

-- View for subreddit performance metrics
CREATE VIEW subreddit_performance AS
SELECT 
    s.name,
    s.subscribers,
    s.is_monitored,
    s.last_scraped,
    COUNT(DISTINCT p.id) as total_posts,
    COUNT(DISTINCT CASE WHEN p.created_utc >= datetime('now', '-7 days') THEN p.id END) as posts_last_week,
    AVG(p.score) as avg_post_score,
    AVG(p.num_comments) as avg_comments,
    COUNT(DISTINCT bl.id) as leads_generated,
    MAX(pa.score) as best_lead_score,
    COUNT(DISTINCT pa.id) as analyzed_posts
FROM subreddits s
LEFT JOIN reddit_posts p ON s.id = p.subreddit_id
LEFT JOIN business_leads bl ON p.id = bl.post_id
LEFT JOIN post_analysis pa ON p.id = pa.post_id AND pa.analysis_type = 'lead_score'
GROUP BY s.id, s.name, s.subscribers, s.is_monitored, s.last_scraped;