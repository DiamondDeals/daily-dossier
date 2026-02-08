# PersonalizedReddit Database Performance & Maintenance Guide

## Overview
This guide provides comprehensive strategies for maintaining optimal performance, data integrity, and efficient operation of the PersonalizedReddit SQLite database.

## Performance Optimization Strategies

### 1. Index Management

#### Critical Indexes Already Implemented
- **reddit_posts**: Composite index on (subreddit_id, created_utc, score) for efficient filtering and sorting
- **post_analysis**: Indexes on post_id, analysis_type, and score for fast AI result lookups
- **business_leads**: Indexes on lead_score, status, and follow_up dates for CRM functionality
- **user_interactions**: Indexes on account_id, content type/id, and timestamps for analytics

#### Index Monitoring Queries
```sql
-- Check index usage (requires SQLITE_ENABLE_STAT4)
SELECT name, tbl, sql FROM sqlite_master WHERE type = 'index';

-- Analyze index effectiveness
ANALYZE;
SELECT * FROM sqlite_stat1 WHERE tbl = 'reddit_posts';
```

### 2. Query Optimization

#### Best Practices
- **Use covering indexes** where possible to avoid table lookups
- **Limit result sets** early with WHERE clauses before JOINs
- **Use EXISTS instead of IN** for subqueries when checking existence
- **Avoid SELECT \*** - specify only needed columns
- **Use prepared statements** to enable query plan caching

#### Problem Query Patterns to Avoid
```sql
-- BAD: No index on created_utc filtering
SELECT * FROM reddit_posts WHERE title LIKE '%keyword%' ORDER BY created_utc;

-- GOOD: Use FTS and limit results
SELECT p.id, p.title, p.score FROM reddit_posts_fts 
JOIN reddit_posts p ON reddit_posts_fts.rowid = p.id
WHERE reddit_posts_fts MATCH 'keyword' 
ORDER BY rank LIMIT 50;
```

### 3. Database Configuration

#### Optimal SQLite PRAGMA Settings
```sql
-- Enable Write-Ahead Logging for better concurrency
PRAGMA journal_mode = WAL;

-- Optimize for mixed read/write workload
PRAGMA synchronous = NORMAL;

-- Increase cache size (adjust based on available RAM)
PRAGMA cache_size = 10000;  -- ~40MB cache

-- Store temporary tables in memory
PRAGMA temp_store = MEMORY;

-- Enable query planner optimizations
PRAGMA optimize;
```

#### Connection Pool Settings
- **Maximum connections**: 5-10 for typical workload
- **Connection timeout**: 30 seconds
- **Busy timeout**: 10 seconds for write operations

### 4. Full-Text Search Optimization

#### FTS5 Configuration
```sql
-- Rebuild FTS index for optimal performance
INSERT INTO reddit_posts_fts(reddit_posts_fts) VALUES('rebuild');

-- Optimize FTS index
INSERT INTO reddit_posts_fts(reddit_posts_fts) VALUES('optimize');
```

#### Search Performance Tips
- **Use content filters** to limit FTS scope
- **Implement result caching** for common searches
- **Pre-filter by date ranges** before FTS queries

## Data Archival and Cleanup

### 1. Automated Cleanup Schedule

#### Daily Cleanup (Low Impact)
```sql
-- Clean expired cache entries
DELETE FROM cache_management WHERE expires_at < datetime('now');

-- Clean old sessions (older than 7 days)
DELETE FROM user_sessions 
WHERE end_time < datetime('now', '-7 days') OR 
      (is_active = 0 AND start_time < datetime('now', '-7 days'));

-- Clean processed realtime events
DELETE FROM realtime_events 
WHERE is_processed = 1 AND created_at < datetime('now', '-1 day');
```

#### Weekly Cleanup (Medium Impact)
```sql
-- Archive old performance metrics (keep 30 days)
DELETE FROM performance_metrics 
WHERE timestamp < datetime('now', '-30 days');

-- Clean old notifications (keep 14 days)
DELETE FROM notifications 
WHERE created_at < datetime('now', '-14 days') AND is_read = 1;

-- Update engagement pattern summaries
-- (Run aggregation queries to update engagement_patterns table)
```

#### Monthly Cleanup (High Impact)
```sql
-- Archive low-value posts (score < 5, no comments, older than 90 days)
INSERT INTO archived_content (content_type, original_id, reddit_id, content_data, archive_reason, original_created_at)
SELECT 
    'post', p.id, p.reddit_id,
    json_object('title', p.title, 'author', p.author, 'score', p.score, 'subreddit_id', p.subreddit_id),
    'low_engagement_auto',
    p.created_utc
FROM reddit_posts p
LEFT JOIN business_leads bl ON p.id = bl.post_id
WHERE p.created_utc < datetime('now', '-90 days')
  AND p.score <= 5 
  AND p.num_comments = 0
  AND bl.id IS NULL  -- Don't archive posts with leads
  AND p.is_archived = 0;

-- Mark posts as archived
UPDATE reddit_posts SET is_archived = 1, archived_at = datetime('now') 
WHERE id IN (SELECT original_id FROM archived_content WHERE content_type = 'post' AND archived_at > datetime('now', '-1 hour'));
```

### 2. Storage Management

#### Database Size Monitoring
```sql
-- Get table sizes
SELECT 
    name,
    (SELECT COUNT(*) FROM sqlite_master WHERE name = main.name) as record_count,
    pgsize as page_size
FROM pragma_table_info('sqlite_master') main;

-- Check database file size
PRAGMA page_count;
PRAGMA page_size;
-- Total size = page_count * page_size
```

#### Space Reclamation
```sql
-- Analyze tables for optimization
ANALYZE;

-- Rebuild database to reclaim space (run during maintenance window)
VACUUM;

-- Incremental vacuum (less disruptive)
PRAGMA incremental_vacuum(1000);
```

## Data Integrity and Backup

### 1. Integrity Checks

#### Daily Integrity Verification
```sql
-- Quick integrity check
PRAGMA quick_check;

-- Full integrity check (run weekly)
PRAGMA integrity_check;

-- Check foreign key constraints
PRAGMA foreign_key_check;
```

#### Custom Data Validation
```sql
-- Check for orphaned records
SELECT 'Orphaned post_analysis' as issue, COUNT(*) as count
FROM post_analysis pa 
LEFT JOIN reddit_posts p ON pa.post_id = p.id 
WHERE p.id IS NULL
UNION ALL
SELECT 'Orphaned business_leads', COUNT(*)
FROM business_leads bl 
LEFT JOIN reddit_posts p ON bl.post_id = p.id 
WHERE p.id IS NULL
UNION ALL
SELECT 'Posts without subreddit', COUNT(*)
FROM reddit_posts p 
LEFT JOIN subreddits s ON p.subreddit_id = s.id 
WHERE s.id IS NULL;
```

### 2. Backup Strategy

#### Backup Schedule
- **Hourly**: WAL checkpoint and copy
- **Daily**: Full database backup with compression
- **Weekly**: Backup to remote location
- **Monthly**: Full backup with data validation

#### Backup Implementation
```sql
-- Force WAL checkpoint before backup
PRAGMA wal_checkpoint(FULL);

-- Create backup (use .backup command or file copy)
-- .backup main backup_filename.db
```

#### Recovery Testing
- **Monthly**: Restore backup to test environment
- **Verify data integrity** after restore
- **Test critical application functions** against restored database

## Monitoring and Alerting

### 1. Performance Metrics to Track

#### Database Performance
- **Query execution time** (track slow queries > 1 second)
- **Database file size** growth rate
- **Cache hit ratio** and memory usage
- **Index usage** statistics
- **Lock wait times** and deadlocks

#### Application Metrics
- **Reddit API rate limit** consumption
- **AI processing queue** length and processing times
- **Export job** success rates and duration
- **User session** counts and duration

### 2. Alert Thresholds

#### Critical Alerts
- Database file size > 5GB (consider archival)
- Query execution time > 10 seconds
- Cache hit ratio < 85%
- Failed integrity checks
- Export jobs failing > 10%

#### Warning Alerts
- Database growth > 100MB/day
- Long-running transactions > 5 minutes
- Reddit API rate limit < 10 remaining
- AI processing queue > 1000 items

### 3. Monitoring Queries

#### Performance Dashboard Query
```sql
SELECT 
    'Posts processed today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM reddit_posts 
WHERE created_at >= date('now')
UNION ALL
SELECT 
    'Average post analysis time',
    AVG(processing_time_ms),
    'milliseconds'
FROM post_analysis 
WHERE created_at >= datetime('now', '-1 hour')
UNION ALL
SELECT 
    'Active user sessions',
    COUNT(*),
    'count'
FROM user_sessions 
WHERE is_active = 1;
```

## Troubleshooting Common Issues

### 1. Performance Problems

#### Slow Queries
```sql
-- Enable query logging
PRAGMA query_only = OFF;

-- Check for missing indexes
EXPLAIN QUERY PLAN SELECT ...;

-- Look for table scans in query plan
```

#### Database Locking
```sql
-- Check for long-running transactions
SELECT * FROM pragma_database_list;

-- Force WAL checkpoint if readers are blocked
PRAGMA wal_checkpoint(RESTART);
```

### 2. Data Issues

#### Duplicate Detection
```sql
-- Find duplicate posts
SELECT reddit_id, COUNT(*) 
FROM reddit_posts 
GROUP BY reddit_id 
HAVING COUNT(*) > 1;

-- Find inconsistent analysis scores
SELECT post_id, analysis_type, COUNT(*), GROUP_CONCAT(score)
FROM post_analysis 
GROUP BY post_id, analysis_type 
HAVING COUNT(*) > 1;
```

#### Data Consistency
```sql
-- Verify lead scores match analysis scores
SELECT bl.id, bl.lead_score, pa.score
FROM business_leads bl
JOIN post_analysis pa ON bl.post_id = pa.post_id 
WHERE pa.analysis_type = 'lead_score' 
  AND abs(bl.lead_score - pa.score) > 0.1;
```

## Deployment and Migration

### 1. Database Updates

#### Safe Migration Process
1. **Create backup** before any schema changes
2. **Test migration** on copy of production data
3. **Use transactions** for atomic updates
4. **Verify data integrity** after migration
5. **Update application** to use new schema

#### Migration Rollback Plan
```sql
-- Always include rollback script in migrations
BEGIN TRANSACTION;
-- Migration changes here
-- Test critical queries
-- ROLLBACK if issues found
COMMIT;
```

### 2. Version Management

#### Schema Version Tracking
```sql
-- Check current schema version
SELECT version, applied_at FROM schema_migrations ORDER BY applied_at DESC LIMIT 1;

-- List all applied migrations
SELECT version, description, applied_at FROM schema_migrations ORDER BY version;
```

This maintenance guide ensures the PersonalizedReddit database remains performant, reliable, and scalable as the application grows.