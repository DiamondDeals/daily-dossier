# Reddit Subreddit Description Scraper v2.0

A modern, GUI-based tool for scraping Reddit subreddit descriptions with intelligent NSFW classification. Built with CustomTkinter for a professional, dark-themed interface.

## Features

### Core Functionality
- **Modern GUI**: CustomTkinter-based interface with dark theme
- **Dual Scraping Methods**: HTML scraping (primary) and Reddit API (fallback)
- **NSFW Classification**: Intelligent content classification based on description analysis
- **Real-time Progress Tracking**: Live progress bars, counters, and status updates
- **Pause/Resume Capability**: Full state persistence for interrupted sessions
- **Auto-save**: Configurable auto-save intervals to prevent data loss

### User Interface
- **Progress Dashboard**: Real-time statistics and progress visualization
- **Recent Results Table**: Last 20 processed items with status and classification
- **Activity Log**: Timestamped activity tracking with auto-scroll
- **Settings Panel**: Comprehensive configuration options
- **Export Functionality**: CSV export with full metadata

### Advanced Features
- **Threading**: Non-blocking GUI with background processing
- **Rate Limiting**: Configurable delays to respect server limits
- **Error Handling**: Robust retry logic with graceful error recovery
- **Memory Management**: Efficient handling of large datasets
- **Resume Capability**: Continue from where you left off after interruptions

## Quick Start

### Method 1: Using the Launcher (Recommended)
```bash
python launch_scraper.py
```
The launcher will automatically:
- Check Python version compatibility
- Install missing dependencies
- Create required directories
- Launch the main application

### Method 2: Direct Launch
```bash
python reddit_scraper_gui.py
```

### Requirements
- Python 3.7 or higher
- Dependencies (auto-installed by launcher):
  - customtkinter>=5.2.0
  - requests>=2.31.0
  - beautifulsoup4>=4.12.0
  - lxml>=4.9.0

## Usage Guide

### 1. File Selection
- Click **Browse** to select your input CSV file
- Default: `Subreddits/Reddit SubReddits - ALL SUBREDDITS.csv`
- CSV format: `Subreddit,Link` (with headers)

### 2. Starting the Scraper
- Click **Start Scraping** to begin processing
- The app will automatically resume from previous sessions if interrupted
- Monitor progress via the real-time dashboard

### 3. Controls
- **Pause/Resume**: Pause processing without losing progress
- **Stop**: Stop processing and save current progress
- **Settings**: Configure rate limiting, timeouts, and other options
- **Export Results**: Save current results to CSV file

### 4. Monitoring Progress
- **Overall Progress**: Visual progress bar and completion percentage
- **Classification Results**: Real-time NSFW/Safe/Error counts
- **Status Information**: Current item, processing rate, and ETA
- **Recent Results**: Last 20 processed items with details
- **Activity Log**: Detailed timestamped processing log

## Configuration Options

Access via the **Settings** button:

### Rate Limiting
- **Rate Limit**: Seconds between requests (default: 2.0)
- **Request Timeout**: HTTP request timeout (default: 10)
- **Max Retries**: Maximum retry attempts (default: 3)

### Auto-Save
- **Auto-save Interval**: Save progress every N items (default: 50)
- **Output Directory**: Where to save results (default: "Exports")

### Scraping Method
- **Use Reddit API**: Toggle between HTML scraping and API (default: HTML)
- **Batch Size**: Processing batch size (default: 100)

## Output Files

### Main Output
- Location: `Exports/subreddit_descriptions_YYYYMMDD_HHMMSS.csv`
- Columns:
  - `Subreddit`: Subreddit name
  - `Link`: Full Reddit URL
  - `Description`: Extracted description text
  - `NSFW_Flag`: YES/NO classification
  - `NSFW_Reason`: Reasoning for NSFW classification
  - `Confidence_Score`: Classification confidence (0-10)
  - `Processing_Time`: Time taken to process this item

### Progress Files
- `scraper_progress.json`: Session state for resume capability
- `scraper_config.json`: User configuration settings

## NSFW Classification Algorithm

The scraper uses a sophisticated multi-factor analysis:

### Classification Factors
1. **Explicit Content Markers** (Confidence: 9)
   - Terms: "adult content", "nsfw", "18+", "explicit", etc.

2. **Sexual Terminology** (Confidence: 7)
   - Terms: "erotic", "fetish", "sexual", "porn", etc.

3. **Community Indicators** (Confidence: 6)
   - Terms: "gonewild", "hookup", "verification required", etc.

4. **Body-Related Terms** (Confidence: 4)
   - Terms: "body", "curves", "attractive", "sexy", etc.

5. **Age Restrictions** (Confidence: 8)
   - Explicit age verification requirements

### Decision Logic
- NSFW threshold: Confidence >= 6
- Multiple indicators boost confidence
- Context-aware analysis prevents false positives

## Performance Optimization

### Recommended Settings
- **Rate Limit**: 2-3 seconds for stable performance
- **Auto-save Interval**: 50-100 items to balance performance and safety
- **Batch Size**: 100 items for optimal memory usage

### Large Dataset Handling
- The app efficiently handles datasets of 50,000+ subreddits
- Progress is automatically saved every N items
- Memory usage is optimized with rotating result buffers
- Resume capability prevents data loss on interruptions

## Troubleshooting

### Common Issues
1. **"No description found"**: Normal for subreddits without descriptions
2. **Timeout errors**: Increase timeout in settings or check internet connection
3. **Rate limiting**: Increase rate limit delay if getting blocked
4. **Memory issues**: Reduce batch size or restart application

### Error Recovery
- The app automatically retries failed requests
- Progress is saved regularly to prevent data loss
- Resume functionality handles interruptions gracefully
- Detailed error logging helps identify issues

## File Structure

```
Reddit Helper Helper/
├── reddit_scraper_gui.py          # Main application
├── launch_scraper.py              # Setup and launcher script
├── scraper_config.json            # Configuration settings
├── scraper_progress.json          # Session progress (auto-created)
├── Exports/                       # Output files
├── Archive/                       # Old scraper versions
└── Subreddits/                    # Input CSV files
```

## Technical Architecture

### Threading Model
- Main GUI thread for user interface
- Background worker thread for scraping
- Queue-based communication between threads
- Non-blocking UI with real-time updates

### Data Flow
1. Load CSV input file
2. Initialize scraping session with configuration
3. Process subreddits in background thread
4. Extract descriptions via HTML parsing
5. Apply NSFW classification algorithm
6. Update GUI with real-time progress
7. Save results with auto-save intervals
8. Export final results to CSV

### Error Handling
- Graceful handling of network timeouts
- Retry logic for failed requests
- Progress preservation on failures
- Detailed error logging and user feedback

## Development Notes

Built following Drew's preferences:
- CustomTkinter for modern dark theme
- Professional UI with comprehensive functionality
- Robust error handling and progress tracking
- Export-first design with full metadata
- No placeholder code - fully functional implementation

This scraper represents a significant upgrade from the previous Selenium-based version, offering better performance, reliability, and user experience while maintaining all the advanced features required for professional subreddit analysis.