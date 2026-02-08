# Reddit Helper Helper - RSS Edition

## ✅ FULLY FUNCTIONAL - NO AUTHENTICATION NEEDED

A Reddit business lead detector that uses RSS feeds instead of PRAW authentication.

---

## 🚀 Quick Start

```bash
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper/"
python3 main_rss_search.py
```

**Results appear in:** `Exports/` folder (CSV, JSON, Markdown)

---

## 📊 What It Does

1. **Loads 95,957 subreddits** from database
2. **Scores each subreddit** by business potential (0-100)
3. **Selects top subreddits** for automation opportunities
4. **Searches via RSS** (no authentication needed)
5. **Detects business leads** using 80 keyword matches
6. **Exports results** to multiple formats

---

## 🏆 Best Subreddits for Leads

**Perfect Score (100):**
- r/Entrepreneur
- r/SaaS  
- r/smallbusiness
- r/startups

**High Value (90):**
- r/AgencyAutomation ⭐ (direct automation needs)
- r/AiForSmallBusiness
- r/BootstrappedSaaS
- r/productivity
- r/freelance

**Found:** 3,561 business-relevant subreddits total

---

## 📁 Files

**Core Scripts:**
- `main_rss_search.py` - Complete workflow (run this)
- `reddit_rss_client.py` - RSS feed fetcher
- `subreddit_scorer.py` - Subreddit ranker
- `business_lead_detector.py` - Lead detector

**Documentation:**
- `QUICKSTART.md` - Simple start guide
- `IMPLEMENTATION.md` - Technical details
- `REBUILD_COMPLETE.md` - Project summary

**Data:**
- `keywords.json` - 80 business keywords
- `csvtojson/subreddits.csv` - 95,957 subreddit database

---

## ✅ Verification Test

```bash
python3 reddit_rss_client.py      # Test RSS fetching
python3 subreddit_scorer.py       # See top subreddits  
python3 business_lead_detector.py # Test lead detection
python3 main_rss_search.py        # Full workflow
```

---

## 📊 Performance

- **Subreddit scoring:** 2 seconds (95k subreddits)
- **RSS fetch:** 2-3 seconds per subreddit
- **15 subreddit search:** 60-90 seconds
- **Export:** <1 second

---

## 🎯 Sample Output

```
🏆 TOP BUSINESS LEADS

1. [5 matches] Automation expert available for new builds
   📍 r/AgencyAutomation
   🔑 Keywords: manual process, workflow, integration, automate, automation
   
2. [4 matches] Spending 40+ hours a week vetting creators...
   📍 r/AgencyAutomation
   🔑 Keywords: bottleneck, there has to be a better way, mass, automate
```

---

## 🔧 Customization

**Change search settings in `main_rss_search.py`:**

```python
# Number of subreddits
top_subreddits = scorer.get_top_subreddits(n=20, min_score=70)

# Minimum keyword matches  
min_score=3

# Posts per subreddit
limit_per_sub=50
```

**Add keywords in `keywords.json`:**

```json
[
  "manual data entry",
  "YOUR KEYWORD HERE",
  ...
]
```

---

## 💡 Tips

1. **Target high-value subreddits first** (r/Entrepreneur, r/AgencyAutomation)
2. **Adjust min_score** based on quality vs quantity needs
3. **Search daily** for top 5 subreddits
4. **Customize keywords** for your specific business
5. **Check Exports folder** for results

---

## ⚡ Why RSS > PRAW

- ✅ No authentication required
- ✅ No API keys needed  
- ✅ Never breaks due to auth issues
- ✅ Simple and reliable
- ✅ Works immediately

---

## 📚 Read More

- **QUICKSTART.md** - Get started in 30 seconds
- **IMPLEMENTATION.md** - How it works + top 30 subreddits
- **REBUILD_COMPLETE.md** - Full project summary

---

**Built:** February 7, 2026  
**Status:** Production ready ✅  
**Authentication:** None required  
**Database:** 95,957 subreddits loaded
