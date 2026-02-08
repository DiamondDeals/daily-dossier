# Quick Start Guide - Reddit Helper Helper (RSS Edition)

## 🚀 Start Searching for Business Leads in 30 Seconds

### Step 1: Run the Main Script

```bash
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper/"
python3 main_rss_search.py
```

That's it! The script will:
1. Score 95,957 subreddits
2. Select the top 15 business-relevant ones
3. Search each subreddit for automation opportunities
4. Export results to `Exports/` folder

---

## 📊 What You'll Get

### Console Output
- Progress of subreddit scoring
- Real-time fetching status
- Top 15 business leads displayed
- Summary statistics

### Exported Files (in `Exports/` folder)
- `business_leads_TIMESTAMP.csv` - Spreadsheet format
- `business_leads_TIMESTAMP.json` - Structured data
- `business_leads_TIMESTAMP.md` - Human-readable report

---

## 🎯 Quick Tests

### Test 1: RSS Client (5 seconds)
```bash
python3 reddit_rss_client.py
```
Expected: Shows 5 posts from r/entrepreneur

### Test 2: Subreddit Scorer (2 seconds)
```bash
python3 subreddit_scorer.py
```
Expected: Shows top 30 subreddits with scores

### Test 3: Business Lead Detector (30 seconds)
```bash
python3 business_lead_detector.py
```
Expected: Finds leads in r/entrepreneur, exports to Exports/

### Test 4: Full Workflow (90 seconds)
```bash
python3 main_rss_search.py
```
Expected: Complete search across 15 subreddits

---

## 🔧 Customization

### Change Search Settings

Edit `main_rss_search.py`:

```python
# Line ~42: Number of subreddits to search
top_subreddits = scorer.get_top_subreddits(n=20, min_score=70)

# Line ~58: Minimum keyword matches
min_score=3  # Require 3+ matches instead of 2+

# Line ~60: Posts per subreddit
limit_per_sub=50  # Get 50 posts instead of 25
```

### Add More Keywords

Edit `keywords.json`:
```json
[
  "manual data entry",
  "YOUR NEW KEYWORD HERE",
  "another keyword",
  ...
]
```

### Search Specific Subreddits

Create a custom script:
```python
from business_lead_detector import BusinessLeadDetector

detector = BusinessLeadDetector()
results = detector.search_subreddits(
    subreddits=['entrepreneur', 'smallbusiness', 'saas'],
    min_score=2,
    limit_per_sub=50
)

detector.print_top_results(results)
detector.export_to_csv(results, 'Exports/my_search.csv')
```

---

## 🏆 Best Subreddits to Search

**Highest Signal:**
- r/Entrepreneur (100 score)
- r/AgencyAutomation (90 score) ⭐
- r/smallbusiness (100 score)
- r/SaaS (100 score)
- r/startups (100 score)

**Good Volume:**
- r/productivity (70 score)
- r/workflow (70 score)
- r/automation (70 score)
- r/freelance (90 score)
- r/digitalnomad (90 score)

---

## 📋 Sample Output

```
🏆 TOP 15 BUSINESS LEADS

1. [5 matches] Automation expert available for new builds
   📍 r/AgencyAutomation · u/example_user
   🔗 https://reddit.com/...
   🔑 Keywords: manual process, workflow, integration, automate, automation
   📝 I'm an automation developer specializing in n8n, AI integrations...

2. [4 matches] Spending 40+ hours a week vetting creators...
   📍 r/AgencyAutomation · u/another_user
   🔑 Keywords: bottleneck, there has to be a better way, mass, automate
   ...
```

---

## ❓ Troubleshooting

### "No module named 'requests'"
```bash
pip3 install requests
```

### "File not found: csvtojson/subreddits.csv"
Make sure you're in the correct directory:
```bash
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper/"
```

### RSS Rate Limiting / 429 Errors
The system already rate-limits to 2 seconds between requests. If you still get errors:
1. Increase rate limit in `reddit_rss_client.py` line 19: `rate_limit_seconds=5.0`
2. Reduce posts per subreddit: `limit_per_sub=10`

### No Leads Found
Try lowering the minimum score:
```python
min_score=1  # Accept posts with 1+ keyword match
```

---

## 🎯 Next Steps

1. **Review the results** in `Exports/` folder
2. **Adjust keywords** in `keywords.json` to match your business
3. **Target specific subreddits** based on your niche
4. **Schedule regular searches** with cron
5. **Reach out to leads** with helpful solutions

---

## 📚 Documentation

- **IMPLEMENTATION.md** - Technical details, how it works
- **QUICKSTART.md** - This file
- **keywords.json** - Business opportunity keywords
- **csvtojson/subreddits.csv** - 95,957 subreddit database

---

## ✅ Status Check

**System working?** Run this:
```bash
python3 reddit_rss_client.py
```

**Expected output:**
```
============================================================
TESTING REDDIT RSS CLIENT
============================================================

🔍 Testing with r/entrepreneur...

✅ Fetched 5 posts:

1. [Post title]
   Author: u/username
   ...

✅ RSS CLIENT WORKS!
```

---

**Built:** February 7, 2026  
**No authentication required** - Uses RSS feeds only  
**Ready to use** - No API keys, no credentials needed
