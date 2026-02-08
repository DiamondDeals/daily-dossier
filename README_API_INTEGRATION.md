# Reddit API Integration - Complete Guide

This comprehensive Reddit API integration provides OAuth2 authentication, multi-account management, rate limiting, content fetching, and business logic for lead detection.

## Features

### Core Functionality
- **OAuth2 Authentication**: Secure Reddit API authentication with token management
- **Multi-Account Support**: Manage multiple Reddit accounts with automatic load balancing
- **Advanced Rate Limiting**: Token bucket algorithm with exponential backoff
- **Business Lead Detection**: AI-powered analysis of posts for automation opportunities
- **Async Support**: High-performance async client for concurrent operations
- **Production-Ready**: Comprehensive error handling, logging, and monitoring

### Business Logic Engine
- **Keyword Matching**: Configurable business problem detection
- **Scoring System**: Intelligent post scoring based on multiple factors
- **Urgency Analysis**: Automatic urgency level detection (high/medium/low)
- **Value Assessment**: Potential business value estimation
- **Scale Detection**: Identification of large-scale automation opportunities

## Quick Start

### 1. Setup Reddit Application

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "web app" for OAuth2 or "script" for username/password
4. Set redirect URI to `http://localhost:8080/callback` for web apps
5. Note your `client_id` and `client_secret`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=YourApp/1.0.0 by YourUsername
```

### 4. Authenticate Users

```python
from auth.reddit_auth import RedditAuthenticator

# Web OAuth flow (recommended)
authenticator = RedditAuthenticator()
token = authenticator.authenticate_web_flow()
print(f"Authenticated: {token.username}")
```

### 5. Basic Usage

```python
from reddit_api_client import RedditAPIClient, SearchQuery

# Initialize client
client = RedditAPIClient()

# Authenticate (uses stored tokens)
client.authenticate_user("your_username", use_web_flow=False)

# Search for business opportunities
query = SearchQuery(
    query="manual data entry automation",
    subreddits=["entrepreneur", "smallbusiness"],
    limit=50,
    min_score=5
)

posts = client.search_posts(query)

# Analyze results
for post in posts:
    if post.business_score > 3.0:
        print(f"High-value opportunity: {post.title}")
        print(f"Score: {post.business_score}")
        print(f"Indicators: {', '.join(post.problem_indicators)}")
```

## API Reference

### RedditAPIClient

Main synchronous client for Reddit API operations.

```python
from reddit_api_client import RedditAPIClient, SearchQuery

client = RedditAPIClient(config=None)
```

#### Methods

**authenticate_user(username, use_web_flow=True)**
- Authenticate a Reddit user account
- Returns: `bool` - Success status

**search_posts(query, progress_callback=None)**
- Search for posts with business analysis
- Parameters:
  - `query`: SearchQuery object
  - `progress_callback`: Optional progress function
- Returns: `List[PostData]` - Analyzed posts

**get_post_comments(post_id, max_depth=3)**
- Get comments for a specific post
- Returns: `List[CommentData]` - Comment data

**export_results(posts, filename, format="csv")**
- Export search results to file
- Formats: "csv", "json", "markdown"
- Returns: `Path` - Export file path

### AsyncRedditAPIClient

High-performance async client for concurrent operations.

```python
from async_reddit_client import AsyncRedditAPIClient

async with AsyncRedditAPIClient() as client:
    # Async operations here
    pass
```

#### Methods

**search_posts_concurrent(queries, progress_callback=None)**
- Search multiple queries concurrently
- Returns: `Dict[str, List[PostData]]` - Results by query

**stream_search_results(query)**
- Stream search results in real-time
- Returns: `AsyncIterator[PostData]` - Post stream

**get_performance_stats()**
- Get performance statistics
- Returns: `Dict[str, Any]` - Performance metrics

### SearchQuery

Configuration for Reddit searches.

```python
from reddit_api_client import SearchQuery

query = SearchQuery(
    query="automation workflow",
    subreddits=["entrepreneur", "smallbusiness"],
    sort="top",  # relevance, hot, top, new, comments
    time_filter="month",  # all, year, month, week, day, hour
    limit=100,
    include_nsfw=False,
    min_score=5,
    max_age_days=30
)
```

### PostData

Reddit post data with business analysis.

```python
# Access post data
print(f"Title: {post.title}")
print(f"Score: {post.score}")
print(f"Comments: {post.num_comments}")

# Business analysis fields
print(f"Business Score: {post.business_score}")
print(f"Urgency: {post.urgency_level}")  # high, medium, low
print(f"Value: {post.potential_value}")  # high, medium, low, unknown
print(f"Problems: {', '.join(post.problem_indicators)}")
```

## Advanced Usage

### Multi-Account Management

```python
from reddit_api_client import RedditAPIClient

client = RedditAPIClient()

# Add multiple accounts
usernames = ["account1", "account2", "account3"]
for username in usernames:
    client.authenticate_user(username, use_web_flow=False)

# Client automatically load-balances requests across accounts
posts = client.search_posts(query)
```

### Async Concurrent Processing

```python
import asyncio
from async_reddit_client import AsyncRedditAPIClient, SearchQuery

async def concurrent_search():
    async with AsyncRedditAPIClient() as client:
        # Add accounts
        await client.authenticate_user("account1")
        await client.authenticate_user("account2")
        
        # Multiple queries
        queries = [
            SearchQuery(query="automation", subreddits=["tech"]),
            SearchQuery(query="workflow", subreddits=["business"]),
            SearchQuery(query="manual process", subreddits=["productivity"])
        ]
        
        # Concurrent execution
        results = await client.search_posts_concurrent(queries)
        
        for query_name, posts in results.items():
            print(f"{query_name}: {len(posts)} posts")

asyncio.run(concurrent_search())
```

### Real-Time Monitoring

```python
async def monitor_opportunities():
    async with AsyncRedditAPIClient() as client:
        await client.authenticate_user("monitor_account")
        
        query = SearchQuery(
            query="automation OR manual OR workflow",
            subreddits=["entrepreneur", "smallbusiness"],
            sort="new",
            limit=100
        )
        
        async for post in client.stream_search_results(query):
            if post.business_score > 3.0:
                print(f"🔥 Opportunity: {post.title}")
                print(f"Score: {post.business_score}")
                # Send notification, save to database, etc.
```

### Custom Business Logic

```python
from reddit_api_client import BusinessLogicEngine
import json

# Create custom keywords
custom_keywords = [
    "manual data entry",
    "repetitive task",
    "time-consuming process",
    "automation needed",
    "workflow bottleneck"
]

# Save to file
with open("custom_keywords.json", "w") as f:
    json.dump(custom_keywords, f)

# Use custom engine
engine = BusinessLogicEngine("custom_keywords.json")
analyzed_post = engine.analyze_post(post)
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```env
# Required
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=YourApp/1.0.0 by YourUsername

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
BURST_LIMIT=10

# Performance
MAX_CONCURRENT_REQUESTS=3
THREAD_POOL_SIZE=5
```

### Configuration File

Alternative to environment variables (`config/reddit_settings.ini`):

```ini
[reddit_credentials]
user_agent = YourApp/1.0.0 by YourUsername
redirect_uri = http://localhost:8080/callback

[api_limits]
requests_per_minute = 60
burst_limit = 10

[app_settings]
max_concurrent_requests = 3
thread_pool_size = 5
```

## Authentication

### OAuth2 Web Flow (Recommended)

```python
from auth.reddit_auth import RedditAuthenticator

auth = RedditAuthenticator()

# Start web authentication
token = auth.authenticate_web_flow(
    scopes=["read", "identity", "history"],
    auto_open_browser=True,
    timeout=300
)

print(f"Authenticated: {token.username}")
```

### Script App (Username/Password)

```python
# Less secure - only use for personal scripts
token = auth.authenticate_password_flow("username", "password")
```

### Token Management

```python
# List stored tokens
users = auth.list_stored_users()

# Load existing token
token = auth.load_token("username")

# Validate token
is_valid = auth.validate_token(token)

# Refresh expired token
if token.is_expired() and token.refresh_token:
    new_token = auth.refresh_token(token)

# Delete token
auth.delete_token("username")
```

## Business Logic

### Scoring Algorithm

Posts are scored based on:

1. **Keyword Matches** (weight: 1.0)
   - Direct keyword appearances in title/text
   - Multiple keyword bonus (weight: 1.5)

2. **Urgency Indicators** (weight: 2.0)
   - "urgent", "asap", "crisis" → High urgency
   - "soon", "deadline" → Medium urgency

3. **Scale Indicators** (weight: 1.8)
   - "hundreds", "thousands", "bulk", "mass"

4. **Manual Process Indicators** (weight: 2.2)
   - "manual", "by hand", "repetitive", "tedious"

5. **Automation Requests** (weight: 2.5)
   - Direct mentions of automation needs

6. **Engagement Factor** (weight: 0.8)
   - Based on upvotes and comments

### Customizing Business Logic

```python
from reddit_api_client import BusinessLogicEngine

# Custom scoring weights
engine = BusinessLogicEngine()
engine.weights = {
    'keyword_match': 1.5,
    'urgency_indicators': 3.0,
    'automation_request': 4.0,
    # ... other weights
}

# Custom urgency patterns
engine.urgency_patterns['high'].append(r'\bemergency\b')
engine.urgency_patterns['medium'].append(r'\bpriority\b')
```

## Rate Limiting

### Synchronous Rate Limiter

```python
from reddit_api_client import RateLimiter

limiter = RateLimiter(config)

# Check if request can be made
can_request, wait_time = limiter.can_make_request()

if can_request:
    # Make API request
    limiter.record_request()
else:
    # Wait or handle rate limit
    time.sleep(wait_time)
```

### Async Rate Limiter

```python
from async_reddit_client import AsyncRateLimiter

limiter = AsyncRateLimiter(config)

# Acquire token for request
await limiter.acquire()

# Make API request
# limiter automatically handles backoff
```

## Export Formats

### CSV Export

```python
# Basic CSV export
csv_file = client.export_results(posts, "results", "csv")

# CSV includes:
# - id, title, text, author, subreddit
# - score, num_comments, created_utc
# - business_score, urgency_level, potential_value
# - problem_indicators, automation_keywords
```

### JSON Export

```python
# JSON export with full data
json_file = client.export_results(posts, "results", "json")

# Includes all PostData fields as JSON objects
```

### Markdown Export

```python
# Human-readable markdown report
md_file = client.export_results(posts, "results", "markdown")

# Formatted report with:
# - Post summaries
# - Business analysis
# - Links and metadata
```

## Testing

### Run Tests

```bash
# Run all tests
python -m pytest test_reddit_api.py -v

# Run specific test class
python -m pytest test_reddit_api.py::TestBusinessLogicEngine -v

# Run with coverage
python -m pytest test_reddit_api.py --cov=reddit_api_client --cov-report=html
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Full workflow testing
- **Performance Tests**: Load and speed testing
- **Async Tests**: Asynchronous functionality testing

## Examples

### Run Example Suite

```bash
python example_usage.py
```

Available examples:
1. **Authentication** - OAuth2 and token management
2. **Basic Search** - Simple business opportunity search
3. **Async Concurrent Search** - High-performance concurrent searches
4. **Real-time Monitoring** - Live monitoring of new opportunities
5. **Multi-Account Management** - Load balancing across accounts
6. **Advanced Business Analysis** - Comprehensive opportunity analysis

### Example Output

```
=== Basic Search Example ===
Searching for: 'manual data entry automation'
In subreddits: entrepreneur, smallbusiness, productivity, excel
Progress: 4/4 subreddits searched

Found 45 posts

1. Business Score: 8.75
   Title: Urgent: Need automation for our manual data entry process
   Subreddit: r/entrepreneur
   Score: 67 | Comments: 23
   Urgency: high | Value: high
   Problem Indicators: manual data entry, automation, repetitive task
   URL: https://reddit.com/r/entrepreneur/comments/xyz/urgent_need...

Results exported to:
  CSV: ./Exports/business_leads_20250814_143022.csv
  JSON: ./Exports/business_leads_20250814_143022.json
  Markdown: ./Exports/business_leads_20250814_143022.md
```

## Performance Optimization

### Async Benefits

- **Concurrent Requests**: Process multiple queries simultaneously
- **I/O Efficiency**: Non-blocking API calls
- **Resource Utilization**: Better CPU and memory usage
- **Scalability**: Handle higher request volumes

### Multi-Account Benefits

- **Rate Limit Distribution**: Spread requests across accounts
- **Higher Throughput**: Increase effective rate limits
- **Redundancy**: Fallback if one account is limited
- **Load Balancing**: Automatic account selection

### Caching

```python
# Built-in caching for repeated requests
client.post_cache  # 5-minute TTL cache
client.subreddit_cache  # LRU cache for subreddit metadata

# Cache statistics
stats = client.get_account_stats()
print(f"Cache hits: {stats['cache_stats']['post_cache_size']}")
```

## Monitoring and Logging

### Statistics Tracking

```python
# Get comprehensive statistics
stats = client.get_account_stats()

print(f"API Requests: {stats['api_stats']['requests_made']}")
print(f"Posts Analyzed: {stats['api_stats']['posts_analyzed']}")
print(f"Business Leads: {stats['api_stats']['business_leads_found']}")
print(f"Error Rate: {stats['api_stats']['errors']}")
```

### Logging Configuration

```python
import logging
import structlog

# Setup structured logging
logging.basicConfig(level=logging.INFO)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

# Client automatically logs:
# - Authentication events
# - Rate limiting
# - API errors
# - Performance metrics
```

## Error Handling

### Common Errors

```python
try:
    posts = client.search_posts(query)
except ValueError as e:
    # Configuration or authentication error
    print(f"Setup error: {e}")
except prawcore.exceptions.TooManyRequests as e:
    # Rate limited
    print(f"Rate limited: {e}")
except prawcore.exceptions.Forbidden as e:
    # Insufficient permissions
    print(f"Permission error: {e}")
except Exception as e:
    # General error
    print(f"Unexpected error: {e}")
```

### Automatic Recovery

- **Rate Limit Recovery**: Automatic backoff and retry
- **Token Refresh**: Automatic OAuth token refresh
- **Account Switching**: Fallback to other accounts
- **Connection Retry**: Automatic reconnection on network errors

## Security Considerations

### Credential Protection

- Store sensitive credentials in environment variables
- Never commit `.env` files to version control
- Use OAuth2 instead of username/password when possible
- Regularly rotate API credentials

### Token Security

- Tokens are encrypted in database storage
- Automatic token expiration handling
- Secure OAuth2 state validation
- CSRF protection in authentication flow

### Network Security

- HTTPS-only API communications
- Request timeout configuration
- User-Agent identification
- Rate limiting compliance

## Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Check client_id and client_secret
   - Verify redirect_uri matches Reddit app settings
   - Ensure required scopes are granted

2. **Rate Limited**
   - Check rate limit configuration
   - Add more accounts for load balancing
   - Reduce request frequency

3. **No Results Found**
   - Verify subreddit names are correct
   - Check search query syntax
   - Adjust minimum score filters

4. **Import Errors**
   - Install all required dependencies
   - Check Python version compatibility (3.8+)
   - Verify file paths are correct

### Debug Mode

```python
# Enable debug logging
import os
os.environ['DEBUG'] = 'true'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Reload configuration
from config.reddit_config import reload_config
config = reload_config()
```

### Support

For issues and questions:
1. Check the example usage scripts
2. Review configuration files
3. Enable debug logging
4. Check Reddit API status
5. Verify network connectivity

## License and Compliance

- Comply with Reddit API Terms of Service
- Respect rate limits and usage guidelines
- Attribution required for commercial use
- No warranty provided - use at your own risk

## Contributing

To contribute improvements:
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

---

*This integration was built for the PersonalizedReddit application to identify business automation opportunities on Reddit.*