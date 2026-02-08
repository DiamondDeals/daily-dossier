# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Reddit scraping and analysis tool called "Reddit Helper Helper" designed to find Reddit posts where people describe business problems that could be solved with automation or software solutions. The tool searches through Reddit using configurable keywords to identify potential leads for business opportunities.

## Project Structure

### Core Application Files
- **`reddithelper.py`** - Main application file containing the complete GUI and scraping logic
- **`reddit_test*.py`** - Various test versions and iterations of the application
- **`keywords.json`** - Configuration file containing search keywords for business problems
- **`subreddit_master.json`** - Master list of subreddits to search

### Supporting Directories
- **`Exports/`** - Contains CSV and Markdown export files from search results
- **`Images/`** - Screenshots and GUI mockups
- **`Subreddits/`** - Tools and data files for managing subreddit lists
- **`csvtojson/`** - Utility to convert CSV subreddit lists to JSON format

## Architecture and Key Components

### Main Application (`reddithelper.py`)
The application follows a GUI-based architecture using CustomTkinter:

1. **RedditHelperHelper Class**: Main application class containing all functionality
2. **Search Engine**: Dual-mode Reddit scraping (HTML scraping primary, API ready as fallback)
3. **Scoring System**: Intelligent post scoring based on keyword matches and engagement metrics
4. **Multi-View Display**: Table, List, and Card views for search results
5. **Export System**: CSV and Markdown export functionality
6. **Debug Console**: Real-time logging and debugging interface

### Key Patterns and Design Decisions

1. **Threading Architecture**: Search operations run in separate threads to prevent GUI freezing
2. **Dual Search Modes**: 
   - HTML scraping (primary) - More reliable, uses BeautifulSoup
   - Reddit API (fallback) - Ready to enable when needed
3. **Keyword-Based Detection**: Configurable business problem keywords for lead identification
4. **Memory Management**: Built-in cache clearing and result management
5. **Export-First Design**: Strong emphasis on data export capabilities (CSV/Markdown)

### Data Flow
1. Load keywords from `keywords.json`
2. Search Reddit using HTML scraping across predefined subreddits
3. Score posts based on keyword matches and engagement
4. Display results in multiple view formats
5. Enable export to CSV/Markdown for further analysis

## Common Development Commands

### Running the Application
```bash
# Run the main application
python reddithelper.py

# Run test versions
python reddit_test.py
python reddit_testv1.py
python reddit_testv2.py
```

### Data Management
```bash
# Convert CSV subreddit data to JSON
cd csvtojson
python csvtojson.py

# Generate subreddit lists
cd Subreddits
python getemall.py
```

### Dependencies
The application requires these key packages:
- `customtkinter>=5.2.0` - Modern GUI framework
- `requests>=2.31.0` - HTTP requests for web scraping
- `beautifulsoup4>=4.12.0` - HTML parsing
- `tkinter` - Standard GUI toolkit (built-in)

## Configuration Files

### keywords.json
Contains the search keywords used to identify business problems. Keywords focus on:
- Manual processes ("manual data entry", "copy and paste")  
- Time-consuming tasks ("takes hours to", "eating up my time")
- Workflow problems ("bottleneck", "can't scale")
- Data management issues ("file management nightmare", "duplicate entries")
- Integration needs ("systems don't talk", "manual sync")
- Business operations ("inventory tracking", "customer follow-up")

### Subreddit Configuration
- `subreddit_master.json` - Master list of subreddits for comprehensive searching
- Individual test files contain hardcoded subreddit lists for business-focused communities

## Development Notes

### GUI Framework Requirements
- **Must use CustomTkinter** - Project standardized on this modern tkinter wrapper
- Dark theme by default with toggle option
- Responsive design with scrollable interfaces
- Progress bars and real-time status updates required

### Search Strategy
The application focuses on business-oriented subreddits:
- Core business: entrepreneur, smallbusiness, freelance, productivity
- Industry-specific: realestate, insurance, healthcare, fitness
- Problem-focused: sysadmin, excel, automation, workflow

### Scoring Algorithm
Posts are scored based on:
- Keyword matches (primary factor)
- Engagement metrics (upvotes, comments)
- Problem indicators ("help", "need", "struggling")
- Multiple keyword matches receive bonus points

### Export Requirements
- CSV format for spreadsheet analysis
- Markdown format for documentation
- Timestamped filenames
- Comprehensive metadata inclusion

## Testing and Debugging

The application includes a built-in debug console accessible via the GUI that provides:
- Real-time search logging
- Connection testing tools
- Subreddit-specific test functions
- JSON vs HTML comparison tools
- Keyword verification utilities

Use the debug console when troubleshooting search issues or verifying connectivity to Reddit.