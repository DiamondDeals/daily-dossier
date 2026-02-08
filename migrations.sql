-- =============================================================================
-- PersonalizedReddit Database Migration Scripts
-- SQLite Migration System for Database Updates and Maintenance
-- =============================================================================

-- =============================================================================
-- MIGRATION SYSTEM SETUP
-- =============================================================================

-- Migration tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rollback_script TEXT,
    checksum TEXT
);

-- Insert initial migration record
INSERT OR IGNORE INTO schema_migrations (version, description, checksum) 
VALUES ('001_initial_schema', 'Initial database schema creation', 'initial');

-- =============================================================================
-- MIGRATION 002: Enhanced Analytics
-- =============================================================================

-- Add enhanced analytics columns to posts
BEGIN TRANSACTION;

-- Check if migration already applied
INSERT OR IGNORE INTO schema_migrations (version, description) 
VALUES ('002_enhanced_analytics', 'Add enhanced analytics and performance tracking');

-- Add new columns if they don't exist
ALTER TABLE reddit_posts ADD COLUMN engagement_rate REAL DEFAULT 0.0;
ALTER TABLE reddit_posts ADD COLUMN velocity_score REAL DEFAULT 0.0;
ALTER TABLE reddit_posts ADD COLUMN trending_score REAL DEFAULT 0.0;

-- Add performance tracking for API calls
CREATE TABLE IF NOT EXISTS api_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    response_time_ms INTEGER,
    status_code INTEGER,
    payload_size_bytes INTEGER,
    error_message TEXT,
    account_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_api_performance_endpoint ON api_performance(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_performance_timestamp ON api_performance(timestamp);

-- Update rollback script
UPDATE schema_migrations 
SET rollback_script = '
    DROP TABLE IF EXISTS api_performance;
    -- Note: SQLite does not support DROP COLUMN, manual data migration required
'
WHERE version = '002_enhanced_analytics';

COMMIT;

-- =============================================================================
-- MIGRATION 003: Content Archival System
-- =============================================================================

BEGIN TRANSACTION;

INSERT OR IGNORE INTO schema_migrations (version, description) 
VALUES ('003_content_archival', 'Add content archival and cleanup system');

-- Add archival status to main tables
ALTER TABLE reddit_posts ADD COLUMN is_archived BOOLEAN DEFAULT 0;
ALTER TABLE reddit_posts ADD COLUMN archive_reason TEXT;
ALTER TABLE reddit_posts ADD COLUMN archived_at TIMESTAMP;

ALTER TABLE reddit_comments ADD COLUMN is_archived BOOLEAN DEFAULT 0;
ALTER TABLE reddit_comments ADD COLUMN archived_at TIMESTAMP;

-- Create archived content table for long-term storage
CREATE TABLE IF NOT EXISTS archived_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL CHECK (content_type IN ('post', 'comment')),
    original_id INTEGER NOT NULL,
    reddit_id TEXT NOT NULL,
    content_data TEXT NOT NULL, -- JSON of original record
    archive_reason TEXT,
    original_created_at TIMESTAMP,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    compressed_size INTEGER,
    retention_until DATE
);

CREATE INDEX IF NOT EXISTS idx_archived_content_type ON archived_content(content_type);
CREATE INDEX IF NOT EXISTS idx_archived_content_archived_at ON archived_content(archived_at);
CREATE INDEX IF NOT EXISTS idx_archived_content_retention ON archived_content(retention_until);

-- Create cleanup log table
CREATE TABLE IF NOT EXISTS cleanup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cleanup_type TEXT NOT NULL,
    records_affected INTEGER DEFAULT 0,
    data_freed_bytes INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed' CHECK (status IN ('running', 'completed', 'failed')),
    error_message TEXT,
    configuration TEXT -- JSON
);

UPDATE schema_migrations 
SET rollback_script = '
    DROP TABLE IF EXISTS archived_content;
    DROP TABLE IF EXISTS cleanup_log;
'
WHERE version = '003_content_archival';

COMMIT;

-- =============================================================================
-- MIGRATION 004: Advanced Search and Filtering
-- =============================================================================

BEGIN TRANSACTION;

INSERT OR IGNORE INTO schema_migrations (version, description) 
VALUES ('004_advanced_search', 'Add advanced search and filtering capabilities');

-- Full-text search setup for posts
DROP INDEX IF EXISTS idx_reddit_posts_fts;
CREATE VIRTUAL TABLE IF NOT EXISTS reddit_posts_fts USING fts5(
    reddit_id,
    title,
    selftext,
    author,
    content='reddit_posts',
    content_rowid='id'
);

-- Populate FTS table with existing data
INSERT OR IGNORE INTO reddit_posts_fts(reddit_id, title, selftext, author)
SELECT reddit_id, title, COALESCE(selftext, ''), COALESCE(author, '') FROM reddit_posts;

-- Create triggers to maintain FTS index
CREATE TRIGGER IF NOT EXISTS reddit_posts_fts_insert AFTER INSERT ON reddit_posts BEGIN
    INSERT INTO reddit_posts_fts(reddit_id, title, selftext, author)
    VALUES (NEW.reddit_id, NEW.title, COALESCE(NEW.selftext, ''), COALESCE(NEW.author, ''));
END;

CREATE TRIGGER IF NOT EXISTS reddit_posts_fts_delete AFTER DELETE ON reddit_posts BEGIN
    DELETE FROM reddit_posts_fts WHERE reddit_id = OLD.reddit_id;
END;

CREATE TRIGGER IF NOT EXISTS reddit_posts_fts_update AFTER UPDATE ON reddit_posts BEGIN
    DELETE FROM reddit_posts_fts WHERE reddit_id = OLD.reddit_id;
    INSERT INTO reddit_posts_fts(reddit_id, title, selftext, author)
    VALUES (NEW.reddit_id, NEW.title, COALESCE(NEW.selftext, ''), COALESCE(NEW.author, ''));
END;

-- Saved searches table
CREATE TABLE IF NOT EXISTS saved_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    search_parameters TEXT NOT NULL, -- JSON with search criteria
    alert_enabled BOOLEAN DEFAULT 0,
    alert_frequency TEXT DEFAULT 'daily' CHECK (alert_frequency IN ('realtime', 'hourly', 'daily', 'weekly')),
    last_run TIMESTAMP,
    results_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_saved_searches_account ON saved_searches(account_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_active ON saved_searches(is_active);

-- Search alerts table
CREATE TABLE IF NOT EXISTS search_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saved_search_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('new_results', 'threshold_met', 'trend_change')),
    trigger_condition TEXT NOT NULL, -- JSON
    notification_method TEXT DEFAULT 'app' CHECK (notification_method IN ('app', 'email', 'webhook')),
    is_active BOOLEAN DEFAULT 1,
    last_triggered TIMESTAMP,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (saved_search_id) REFERENCES saved_searches(id) ON DELETE CASCADE
);

UPDATE schema_migrations 
SET rollback_script = '
    DROP TRIGGER IF EXISTS reddit_posts_fts_insert;
    DROP TRIGGER IF EXISTS reddit_posts_fts_delete; 
    DROP TRIGGER IF EXISTS reddit_posts_fts_update;
    DROP TABLE IF EXISTS reddit_posts_fts;
    DROP TABLE IF EXISTS saved_searches;
    DROP TABLE IF EXISTS search_alerts;
'
WHERE version = '004_advanced_search';

COMMIT;

-- =============================================================================
-- MIGRATION 005: Real-time Notifications
-- =============================================================================

BEGIN TRANSACTION;

INSERT OR IGNORE INTO schema_migrations (version, description) 
VALUES ('005_realtime_notifications', 'Add real-time notifications and alerts system');

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('new_lead', 'high_score_post', 'search_alert', 'system', 'recommendation')),
    title TEXT NOT NULL,
    message TEXT,
    data TEXT, -- JSON with additional context
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    is_read BOOLEAN DEFAULT 0,
    is_actionable BOOLEAN DEFAULT 0,
    action_url TEXT,
    action_data TEXT, -- JSON
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_account ON notifications(account_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);

-- Notification preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    delivery_method TEXT DEFAULT 'app' CHECK (delivery_method IN ('app', 'email', 'push', 'webhook')),
    frequency TEXT DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'hourly', 'daily', 'weekly', 'never')),
    threshold_settings TEXT, -- JSON for specific thresholds
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE,
    UNIQUE(account_id, notification_type, delivery_method)
);

-- Real-time events table for WebSocket/SSE
CREATE TABLE IF NOT EXISTS realtime_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    account_id INTEGER,
    channel TEXT NOT NULL, -- user_123, global, etc.
    event_data TEXT NOT NULL, -- JSON
    is_processed BOOLEAN DEFAULT 0,
    expires_at TIMESTAMP DEFAULT (datetime('now', '+24 hours')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES reddit_accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_realtime_events_channel ON realtime_events(channel);
CREATE INDEX IF NOT EXISTS idx_realtime_events_processed ON realtime_events(is_processed);
CREATE INDEX IF NOT EXISTS idx_realtime_events_expires ON realtime_events(expires_at);

UPDATE schema_migrations 
SET rollback_script = '
    DROP TABLE IF EXISTS notifications;
    DROP TABLE IF EXISTS notification_preferences;
    DROP TABLE IF EXISTS realtime_events;
'
WHERE version = '005_realtime_notifications';

COMMIT;

-- =============================================================================
-- MAINTENANCE AND CLEANUP PROCEDURES
-- =============================================================================

-- Procedure to archive old posts (SQLite doesn't have stored procedures, but these are the queries)
/*
-- Archive posts older than 90 days with low engagement
INSERT INTO archived_content (content_type, original_id, reddit_id, content_data, archive_reason, original_created_at)
SELECT 
    'post',
    id,
    reddit_id,
    json_object(
        'title', title,
        'selftext', selftext,
        'author', author,
        'score', score,
        'num_comments', num_comments,
        'subreddit_id', subreddit_id,
        'created_utc', created_utc
    ),
    'automated_low_engagement',
    created_utc
FROM reddit_posts 
WHERE created_utc < datetime('now', '-90 days')
  AND score < 10 
  AND num_comments < 5
  AND is_archived = 0;

-- Mark posts as archived
UPDATE reddit_posts 
SET is_archived = 1, 
    archive_reason = 'automated_low_engagement',
    archived_at = CURRENT_TIMESTAMP
WHERE created_utc < datetime('now', '-90 days')
  AND score < 10 
  AND num_comments < 5
  AND is_archived = 0;
*/

-- =============================================================================
-- DATABASE OPTIMIZATION PROCEDURES
-- =============================================================================

-- Analyze tables for query optimization
-- Run periodically: ANALYZE;

-- Rebuild indexes for optimal performance
-- Run monthly:
/*
REINDEX idx_reddit_posts_created_utc;
REINDEX idx_reddit_posts_score;
REINDEX idx_reddit_posts_composite;
REINDEX idx_post_analysis_score;
REINDEX idx_business_leads_score;
*/

-- Vacuum to reclaim space after cleanup
-- Run weekly: VACUUM;

-- =============================================================================
-- ROLLBACK PROCEDURES
-- =============================================================================

-- Function to rollback a specific migration
/*
-- Example rollback for migration 003:
DELETE FROM schema_migrations WHERE version = '003_content_archival';
DROP TABLE IF EXISTS archived_content;
DROP TABLE IF EXISTS cleanup_log;
-- Note: Cannot remove added columns in SQLite without recreating table
*/

-- =============================================================================
-- DATA INTEGRITY CHECKS
-- =============================================================================

-- Check for orphaned records
/*
-- Posts without subreddits
SELECT COUNT(*) FROM reddit_posts p 
LEFT JOIN subreddits s ON p.subreddit_id = s.id 
WHERE s.id IS NULL;

-- Analysis without posts
SELECT COUNT(*) FROM post_analysis pa 
LEFT JOIN reddit_posts p ON pa.post_id = p.id 
WHERE p.id IS NULL;

-- Comments without posts
SELECT COUNT(*) FROM reddit_comments c 
LEFT JOIN reddit_posts p ON c.post_id = p.id 
WHERE p.id IS NULL;
*/