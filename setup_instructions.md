# PersonalizedReddit Setup Instructions

## Overview
PersonalizedReddit is a comprehensive AI-powered Reddit analysis tool that identifies business automation opportunities and generates personalized newsletters. It features a modern CustomTkinter GUI with three main views: Home (Newsletter), Live (Enhanced Reddit), and Discover (AI Recommendations).

## Features Tested & Working
✅ **Database Management**: SQLite with comprehensive schema  
✅ **AI Services**: Sentiment analysis, business opportunity detection, summarization  
✅ **Export System**: CSV, JSON, Markdown, Excel, PDF export functionality  
✅ **GUI Components**: CustomTkinter interface with navigation and dialogs  
✅ **Reddit Integration**: PRAW-based API client (configuration required)  
✅ **Newsletter Service**: AI-powered daily digest generation  
✅ **Configuration Management**: Flexible settings and preferences  

## Installation

### 1. Prerequisites
- Python 3.11 or later
- Windows 10/11 (tested environment)

### 2. Install Dependencies
```bash
# Install production requirements
pip install -r requirements_production.txt

# Or install manually:
pip install customtkinter praw pandas numpy requests beautifulsoup4
pip install transformers torch sentence-transformers scikit-learn nltk
pip install structlog cachetools openpyxl reportlab markdown backoff
```

### 3. Configuration

#### Reddit API Setup (Optional but Recommended)
1. Create Reddit app at https://www.reddit.com/prefs/apps
2. Edit `config/reddit_settings.ini`:
```ini
[reddit_api]
client_id = your_client_id_here
client_secret = your_client_secret_here
user_agent = PersonalizedReddit/1.0
username = your_reddit_username
password = your_reddit_password
```

#### Business Keywords (Optional)
- Edit `keywords.json` to customize business opportunity detection
- Current format supports both list and categorized dict formats

## Running the Application

### Main Application
```bash
python main.py
```

### Test Individual Components
```bash
# Test AI services (offline mode)
python test_ai_simple.py

# Test export functionality
python test_export.py

# Test GUI components
python test_gui_simple.py

# Run comprehensive tests
python test_integration_final.py
```

## Application Structure

### Main Views
- **Home**: Newsletter overview with AI digest and opportunity cards
- **Live**: Enhanced Reddit browsing with real-time analysis
- **Discover**: AI-powered subreddit recommendations

### Core Services
- **AI Service**: Business opportunity detection, sentiment analysis
- **Export Service**: Multi-format data export (CSV, JSON, Markdown, PDF)
- **Newsletter Service**: Daily digest generation
- **Reddit API Service**: Enhanced Reddit data fetching
- **Database Manager**: SQLite operations with comprehensive schema

### Key Features
- Dark theme UI with professional design
- Real-time AI analysis of Reddit posts
- Business lead scoring and categorization
- Comprehensive export functionality
- User preference management
- Caching and performance optimization

## Data Storage

### Database Schema
- Reddit accounts and authentication
- Subreddit monitoring and profiles
- Post analysis and business leads
- User interactions and preferences
- Export history and analytics

### Export Formats
- **CSV**: Spreadsheet-compatible business data
- **JSON**: Structured data for API integration
- **Markdown**: Human-readable reports
- **Excel**: Advanced spreadsheet format
- **PDF**: Professional presentation format

## Troubleshooting

### Common Issues
1. **AI Models Not Loading**: Use offline mode with `skip_model_loading: True`
2. **Reddit API Errors**: Verify credentials in `config/reddit_settings.ini`
3. **GUI Issues**: Ensure CustomTkinter is properly installed
4. **Export Failures**: Check write permissions in `Exports/` directory

### Performance Tips
- Enable AI model caching for faster analysis
- Use background threading for heavy operations
- Configure appropriate scraping intervals
- Monitor database size and clean up old data

## Development

### Testing
The application includes comprehensive tests covering:
- Database operations and schema validation
- AI service functionality with fallback modes
- Export system with multiple formats
- GUI component integration
- Service integration and error handling

### Code Quality
- Structured logging with performance monitoring
- Error handling with graceful degradation
- Modular architecture with clear separation
- Comprehensive documentation and type hints

## Production Deployment

### Recommended Configuration
- Set up proper Reddit API credentials
- Configure AI model caching
- Enable performance monitoring
- Set up automated data cleanup
- Configure export directory permissions

### Security Considerations
- Store API credentials securely
- Validate all user inputs
- Implement rate limiting
- Monitor database access
- Regular security updates

## Support

For issues or questions:
1. Check logs in the application debug console
2. Run individual component tests
3. Verify configuration files
4. Review export history for data validation

The application is designed to work with graceful degradation - if Reddit API is not configured, it will use mock data. If AI models fail to load, it falls back to keyword-based analysis.