-- =============================================================================
-- PersonalizedReddit Sample Queries
-- Common Database Operations and Business Intelligence Queries
-- =============================================================================

-- =============================================================================
-- USER MANAGEMENT QUERIES
-- =============================================================================

-- Get active Reddit accounts with their settings
SELECT 
    ra.username,
    ra.account_type,
    ra.is_primary,
    ra.last_login,
    ra.rate_limit_remaining,
    COUNT(up.id) as preference_count
FROM reddit_accounts ra
LEFT JOIN user_preferences up ON ra.id = up.account_id
WHERE ra.is_active = 1
GROUP BY ra.id, ra.username, ra.account_type, ra.is_primary, ra.last_login, ra.rate_limit_remaining
ORDER BY ra.is_primary DESC, ra.last_login DESC;

-- Get user preferences for a specific account
SELECT 
    preference_key,
    preference_value,
    preference_type,
    category,
    updated_at
FROM user_preferences 
WHERE account_id = ? 
ORDER BY category, preference_key;

-- Update user preference
INSERT OR REPLACE INTO user_preferences (account_id, preference_key, preference_value, preference_type, category)
VALUES (?, 'theme', 'dark', 'string', 'ui');

-- =============================================================================
-- REDDIT CONTENT QUERIES
-- =============================================================================

-- Get recent posts from monitored subreddits with analysis scores
SELECT 
    p.id,
    p.title,
    p.author,
    p.score as reddit_score,
    p.num_comments,
    p.created_utc,
    s.name as subreddit,
    COALESCE(pa_lead.score, 0) as lead_score,
    COALESCE(pa_sent.sentiment_score, 0) as sentiment_score,
    COALESCE(pa_lead.lead_potential, 'low') as lead_potential
FROM reddit_posts p
JOIN subreddits s ON p.subreddit_id = s.id
LEFT JOIN post_analysis pa_lead ON p.id = pa_lead.post_id AND pa_lead.analysis_type = 'lead_score'
LEFT JOIN post_analysis pa_sent ON p.id = pa_sent.post_id AND pa_sent.analysis_type = 'sentiment'
WHERE s.is_monitored = 1 
  AND p.created_utc >= datetime('now', '-7 days')
  AND p.is_processed = 1
ORDER BY 
    CASE WHEN pa_lead.score IS NOT NULL THEN pa_lead.score ELSE 0 END DESC,
    p.score DESC
LIMIT 50;

-- Get top performing posts by subreddit
SELECT 
    s.name as subreddit,
    COUNT(p.id) as total_posts,
    AVG(p.score) as avg_score,
    AVG(p.num_comments) as avg_comments,
    MAX(p.score) as top_score,
    COUNT(CASE WHEN pa.lead_potential = 'high' THEN 1 END) as high_potential_leads,
    COUNT(CASE WHEN pa.lead_potential = 'very_high' THEN 1 END) as very_high_potential_leads
FROM subreddits s
JOIN reddit_posts p ON s.id = p.subreddit_id
LEFT JOIN post_analysis pa ON p.id = pa.post_id AND pa.analysis_type = 'business_opportunity'
WHERE p.created_utc >= datetime('now', '-30 days')
GROUP BY s.id, s.name
HAVING COUNT(p.id) >= 5
ORDER BY very_high_potential_leads DESC, high_potential_leads DESC, avg_score DESC;

-- Find posts matching specific business keywords
SELECT DISTINCT
    p.id,
    p.title,
    p.author,
    p.score,
    s.name as subreddit,
    pa.keywords_matched,
    pa.lead_potential,
    pa.score as analysis_score
FROM reddit_posts p
JOIN subreddits s ON p.subreddit_id = s.id
JOIN post_analysis pa ON p.id = pa.post_id
WHERE pa.analysis_type = 'keyword_match'
  AND json_extract(pa.keywords_matched, '$') LIKE '%manual process%'
  AND p.created_utc >= datetime('now', '-14 days')
ORDER BY pa.score DESC
LIMIT 25;

-- Get posts with their comments for thread analysis
SELECT 
    p.id as post_id,
    p.title,
    p.selftext,
    p.author as post_author,
    p.score as post_score,
    c.id as comment_id,
    c.body,
    c.author as comment_author,
    c.score as comment_score,
    c.depth
FROM reddit_posts p
LEFT JOIN reddit_comments c ON p.id = c.post_id
WHERE p.id = ?
ORDER BY c.depth, c.comment_order;

-- =============================================================================
-- AI ANALYSIS QUERIES
-- =============================================================================

-- Get comprehensive AI analysis for a post
SELECT 
    p.title,
    p.author,
    p.score,
    p.created_utc,
    pa.analysis_type,
    pa.score,
    pa.confidence,
    pa.sentiment_score,
    pa.sentiment_label,
    pa.lead_potential,
    pa.keywords_matched,
    pa.category_predicted
FROM reddit_posts p
JOIN post_analysis pa ON p.id = pa.post_id
WHERE p.id = ?
ORDER BY pa.analysis_type;

-- Find posts ready for AI processing
SELECT 
    p.id,
    p.reddit_id,
    p.title,
    p.created_utc,
    s.name as subreddit
FROM reddit_posts p
JOIN subreddits s ON p.subreddit_id = s.id
WHERE p.is_processed = 0 
  AND p.processing_status = 'pending'
  AND p.created_utc >= datetime('now', '-3 days')
ORDER BY p.created_utc DESC
LIMIT 100;

-- Get AI recommendations for a user
SELECT 
    r.recommendation_type,
    r.title,
    r.description,
    r.confidence_score,
    r.priority_score,
    r.status,
    r.created_at,
    r.expires_at
FROM ai_recommendations r
WHERE r.account_id = ?
  AND r.status IN ('pending', 'viewed')
  AND (r.expires_at IS NULL OR r.expires_at > datetime('now'))
ORDER BY r.priority_score DESC, r.created_at DESC;

-- Get content summaries for recent high-scoring posts
SELECT 
    p.title,
    p.score,
    s.name as subreddit,
    cs.summary_type,
    cs.summary_text,
    cs.key_points,
    cs.relevance_score
FROM reddit_posts p
JOIN subreddits s ON p.subreddit_id = s.id
JOIN content_summaries cs ON p.id = cs.content_id AND cs.content_type = 'post'
WHERE p.score >= 50
  AND p.created_utc >= datetime('now', '-7 days')
  AND cs.summary_type = 'business_insight'
ORDER BY cs.relevance_score DESC, p.score DESC;

-- =============================================================================
-- BUSINESS LEADS QUERIES
-- =============================================================================

-- Get high-quality business leads
SELECT 
    bl.lead_title,
    bl.business_problem,
    bl.industry_category,
    bl.urgency_level,
    bl.lead_score,
    bl.qualification_status,
    bl.follow_up_date,
    p.title as post_title,
    p.author,
    s.name as subreddit,
    p.created_utc as post_date
FROM business_leads bl
JOIN reddit_posts p ON bl.post_id = p.id
JOIN subreddits s ON p.subreddit_id = s.id
WHERE bl.lead_score >= 0.7
  AND bl.qualification_status IN ('unqualified', 'qualified')
ORDER BY bl.lead_score DESC, bl.urgency_level DESC;

-- Get leads that need follow-up
SELECT 
    bl.id,
    bl.lead_title,
    bl.qualification_status,
    bl.follow_up_date,
    bl.notes,
    p.author,
    s.name as subreddit
FROM business_leads bl
JOIN reddit_posts p ON bl.post_id = p.id
JOIN subreddits s ON p.subreddit_id = s.id
WHERE bl.follow_up_date <= date('now', '+3 days')
  AND bl.qualification_status NOT IN ('closed_won', 'closed_lost')
ORDER BY bl.follow_up_date ASC;

-- Lead conversion funnel analysis
SELECT 
    qualification_status,
    COUNT(*) as count,
    AVG(lead_score) as avg_score,
    SUM(CASE WHEN estimated_value IS NOT NULL THEN estimated_value ELSE 0 END) as total_estimated_value
FROM business_leads
WHERE created_at >= datetime('now', '-90 days')
GROUP BY qualification_status
ORDER BY 
    CASE qualification_status
        WHEN 'unqualified' THEN 1
        WHEN 'qualified' THEN 2 
        WHEN 'contacted' THEN 3
        WHEN 'in_progress' THEN 4
        WHEN 'closed_won' THEN 5
        WHEN 'closed_lost' THEN 6
    END;

-- =============================================================================
-- USER ACTIVITY AND ENGAGEMENT QUERIES
-- =============================================================================

-- Get user activity summary
SELECT 
    ui.account_id,
    ra.username,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT ui.content_id) as unique_content_interacted,
    COUNT(DISTINCT DATE(ui.created_at)) as active_days,
    AVG(ui.duration_seconds) as avg_interaction_duration,
    COUNT(CASE WHEN ui.interaction_type = 'save' THEN 1 END) as saves,
    COUNT(CASE WHEN ui.interaction_type = 'export' THEN 1 END) as exports
FROM user_interactions ui
JOIN reddit_accounts ra ON ui.account_id = ra.id
WHERE ui.created_at >= datetime('now', '-30 days')
GROUP BY ui.account_id, ra.username
ORDER BY total_interactions DESC;

-- Get saved content for a user
SELECT 
    sc.collection_name,
    sc.content_type,
    CASE sc.content_type
        WHEN 'post' THEN p.title
        WHEN 'subreddit' THEN s.name
    END as content_title,
    sc.notes,
    sc.tags,
    sc.priority,
    sc.created_at
FROM saved_content sc
LEFT JOIN reddit_posts p ON sc.content_type = 'post' AND sc.content_id = p.id
LEFT JOIN subreddits s ON sc.content_type = 'subreddit' AND sc.content_id = s.id
WHERE sc.account_id = ?
  AND sc.is_archived = 0
ORDER BY sc.priority DESC, sc.created_at DESC;

-- Daily engagement patterns
SELECT 
    DATE(ui.created_at) as activity_date,
    COUNT(DISTINCT ui.account_id) as active_users,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT ui.content_id) as unique_content,
    AVG(ui.duration_seconds) as avg_duration
FROM user_interactions ui
WHERE ui.created_at >= datetime('now', '-30 days')
GROUP BY DATE(ui.created_at)
ORDER BY activity_date DESC;

-- =============================================================================
-- EXPORT AND REPORTING QUERIES
-- =============================================================================

-- Generate lead export data
SELECT 
    bl.lead_title,
    bl.business_problem,
    bl.potential_solution,
    bl.industry_category,
    bl.urgency_level,
    bl.lead_score,
    bl.qualification_status,
    bl.estimated_value,
    bl.probability_percent,
    p.title as post_title,
    p.author as reddit_author,
    p.score as post_score,
    p.num_comments,
    s.name as subreddit,
    p.url as post_url,
    bl.created_at as lead_created,
    bl.follow_up_date
FROM business_leads bl
JOIN reddit_posts p ON bl.post_id = p.id
JOIN subreddits s ON p.subreddit_id = s.id
WHERE bl.created_at >= ?
  AND bl.created_at <= ?
ORDER BY bl.lead_score DESC;

-- Generate subreddit performance report
SELECT 
    s.name as subreddit,
    s.subscribers,
    COUNT(DISTINCT p.id) as posts_analyzed,
    AVG(p.score) as avg_post_score,
    COUNT(DISTINCT bl.id) as leads_generated,
    AVG(bl.lead_score) as avg_lead_score,
    COUNT(CASE WHEN bl.qualification_status = 'qualified' THEN 1 END) as qualified_leads,
    MAX(p.created_utc) as last_post_date,
    s.last_scraped
FROM subreddits s
LEFT JOIN reddit_posts p ON s.id = p.subreddit_id AND p.created_utc >= datetime('now', '-30 days')
LEFT JOIN business_leads bl ON p.id = bl.post_id
WHERE s.is_monitored = 1
GROUP BY s.id, s.name, s.subscribers, s.last_scraped
ORDER BY leads_generated DESC, avg_lead_score DESC;

-- Get export history
SELECT 
    eh.export_type,
    eh.export_format,
    eh.record_count,
    eh.file_size_bytes,
    eh.status,
    eh.created_at,
    eh.processing_time_ms,
    ra.username
FROM export_history eh
LEFT JOIN reddit_accounts ra ON eh.account_id = ra.id
WHERE eh.created_at >= datetime('now', '-90 days')
ORDER BY eh.created_at DESC;

-- =============================================================================
-- PERFORMANCE AND MONITORING QUERIES
-- =============================================================================

-- Database size and growth analysis
SELECT 
    'reddit_posts' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as latest_record,
    MIN(created_at) as earliest_record
FROM reddit_posts
UNION ALL
SELECT 
    'reddit_comments' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as latest_record,
    MIN(created_at) as earliest_record
FROM reddit_comments
UNION ALL
SELECT 
    'business_leads' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as latest_record,
    MIN(created_at) as earliest_record
FROM business_leads
UNION ALL
SELECT 
    'post_analysis' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as latest_record,
    MIN(created_at) as earliest_record
FROM post_analysis;

-- Performance metrics summary
SELECT 
    metric_type,
    metric_name,
    COUNT(*) as measurement_count,
    AVG(value_numeric) as avg_value,
    MIN(value_numeric) as min_value,
    MAX(value_numeric) as max_value,
    unit
FROM performance_metrics
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY metric_type, metric_name, unit
ORDER BY metric_type, avg_value DESC;

-- Cache efficiency
SELECT 
    cache_type,
    COUNT(*) as cache_entries,
    SUM(data_size_bytes) as total_size_bytes,
    AVG(access_count) as avg_access_count,
    COUNT(CASE WHEN expires_at < datetime('now') THEN 1 END) as expired_entries
FROM cache_management
GROUP BY cache_type
ORDER BY total_size_bytes DESC;

-- =============================================================================
-- SEARCH AND DISCOVERY QUERIES
-- =============================================================================

-- Full-text search across posts
SELECT 
    p.id,
    p.title,
    p.author,
    p.score,
    s.name as subreddit,
    snippet(reddit_posts_fts, 1, '<mark>', '</mark>', '...', 32) as title_snippet
FROM reddit_posts_fts
JOIN reddit_posts p ON reddit_posts_fts.rowid = p.id
JOIN subreddits s ON p.subreddit_id = s.id
WHERE reddit_posts_fts MATCH ?
ORDER BY rank
LIMIT 50;

-- Trending topics analysis
SELECT 
    pa.category_predicted as category,
    COUNT(*) as mention_count,
    AVG(pa.score) as avg_score,
    COUNT(CASE WHEN p.created_utc >= datetime('now', '-24 hours') THEN 1 END) as recent_mentions,
    MAX(p.score) as top_post_score
FROM post_analysis pa
JOIN reddit_posts p ON pa.post_id = p.id
WHERE pa.analysis_type = 'category'
  AND p.created_utc >= datetime('now', '-7 days')
  AND pa.category_predicted IS NOT NULL
GROUP BY pa.category_predicted
HAVING mention_count >= 3
ORDER BY recent_mentions DESC, avg_score DESC;

-- Similar posts recommendation
SELECT DISTINCT
    p2.id,
    p2.title,
    p2.author,
    p2.score,
    s.name as subreddit,
    COUNT(DISTINCT pa2.analysis_type) as matching_analyses
FROM reddit_posts p1
JOIN post_analysis pa1 ON p1.id = pa1.post_id
JOIN post_analysis pa2 ON pa1.analysis_type = pa2.analysis_type 
  AND abs(pa1.score - pa2.score) <= 0.2
JOIN reddit_posts p2 ON pa2.post_id = p2.id
JOIN subreddits s ON p2.subreddit_id = s.id
WHERE p1.id = ?
  AND p2.id != p1.id
  AND p2.created_utc >= datetime('now', '-30 days')
GROUP BY p2.id, p2.title, p2.author, p2.score, s.name
HAVING matching_analyses >= 2
ORDER BY matching_analyses DESC, p2.score DESC
LIMIT 10;