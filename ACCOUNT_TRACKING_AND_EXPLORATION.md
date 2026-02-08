# Account Tracking & Exploration Features

**Implemented:** February 7, 2026

---

## 🎯 FEATURE 1: ACCOUNT TRACKING

**Purpose:** Learn which accounts consistently produce good content

### How It Works

1. **Tracks Every Account** encountered in scans:
   - Reddit: u/username
   - Twitter: @handle
   - Moltbook: @agent
   - YouTube: Channel Name

2. **Metrics Tracked:**
   - Total appearances in dossier
   - Average engagement (upvotes + comments + score)
   - Total engagement across all posts
   - Best post (highest engagement)
   - Last 10 posts (with engagement data)
   - First seen & last seen dates

3. **Generates:** `top_accounts.html`
   - **URL:** https://diamonddeals.github.io/daily-dossier/top_accounts.html
   - Top 20 accounts per platform
   - Sorted by average engagement
   - Shows best post from each account
   - Updates after every scan

### Files Created

- `account_tracker.py` - Main tracking system
- `Database/account_tracker.json` - Account database
- `top_accounts.html` - Public-facing page

### Example Output

```
🟠 REDDIT USERS

@successful_founder
├─ Appearances: 15
├─ Avg Engagement: 450
├─ Total: 6,750
└─ 🏆 Best Post (850 engagement):
   "How I hit $1M ARR in 6 months"
   https://reddit.com/...

@indie_hacker_mike
├─ Appearances: 12
├─ Avg Engagement: 380
└─ ...
```

---

## 🔍 FEATURE 2: EXPLORATION MODE

**Purpose:** Discover NEW content outside programmed sources

### How It Works

1. **Reddit Exploration:**
   - Scans r/all trending
   - Filters for business/tech keywords
   - Excludes already-monitored subreddits
   - Returns top 5 discoveries

2. **Twitter Exploration:** ⏳ Coming Soon
   - Requires Twitter API v2 (not free tier)
   - Would search trending hashtags: #indiemaker, #nocode, etc.

3. **Moltbook Exploration:** ⏳ Coming Soon
   - Browse trending posts outside subscribed submolts
   - Requires Moltbook trending API

4. **YouTube Exploration:** ⏳ Coming Soon
   - YouTube trending videos in business/tech
   - Requires YouTube Data API key

### New Dossier Section

```
🔍 EXPLORATION (New Discoveries)
Content found outside programmed channels — potential new sources!

1. [Title]
   Source: r/newsubreddit ⭐ New Discovery
   ↑250 upvotes • 💬45 comments
   https://...

2. [Title]
   Source: @newtwitter ⭐ New Discovery
   ...
```

### Files Created

- `exploration_scanner.py` - Discovery engine
- `Database/exploration_discoveries.json` - Discovery log

### Keywords Used (Reddit)

```python
business, startup, saas, entrepreneur, marketing, sales,
product, launch, revenue, growth, ai, tech, founder,
building, scaling, mvp, indie, maker
```

---

## 📊 INTEGRATION

### Updated Workflow

**After Each Scan:**

1. **Scan** 6 platforms (existing)
2. **Track accounts** (NEW)
   - Extract all usernames/handles
   - Update engagement metrics
   - Generate top_accounts.html
3. **Exploration** (NEW)
   - Discover 5 new items
   - Add 🔍 Exploration section to dossier
4. **Generate** HTML with new sections
5. **Post** to Slack
6. **Push** to GitHub

### Dossier Structure (Updated)

```
📊 Daily Business Dossier

[Header with archive links]

🔥 HEATING UP (engagement jumps)
🔍 EXPLORATION (new discoveries)

🟠 REDDIT BUSINESS LEADS
🔵 TWITTER BUILDING IN PUBLIC
🎥 YOUTUBE AI & MARKETING
🤖 MOLTBOOK AGENT BUILDS
🟢 HEALTH & WELLNESS
📰 RSS NEWS FEED

[Footer with complete database links]
```

---

## 🔗 NEW PAGES

1. **Top Accounts**
   - URL: https://diamonddeals.github.io/daily-dossier/top_accounts.html
   - Shows: Top 20 per platform by avg engagement
   - Updates: After every scan

2. **Stats Page** (existing)
   - Now includes: Link to Top Accounts

---

## 💡 FUTURE ENHANCEMENTS

### Account Tracking

- [ ] Recommend new accounts to follow (5+ appearances, 300+ avg engagement)
- [ ] Track account growth trends (engagement increasing/decreasing)
- [ ] Export CSV of top accounts
- [ ] Flag accounts that suddenly go inactive

### Exploration

- [ ] Add Twitter exploration (when API v2 available)
- [ ] Add Moltbook trending (when API available)
- [ ] Add YouTube trending (need API key)
- [ ] Machine learning: learn what "good" content looks like
- [ ] Suggest new subreddits/channels to monitor permanently

---

## 🚀 STATUS

✅ Account Tracking: **IMPLEMENTED**
✅ Top Accounts Page: **LIVE**
✅ Reddit Exploration: **IMPLEMENTED**
⏳ Twitter Exploration: Awaiting API v2
⏳ Moltbook Exploration: Awaiting API
⏳ YouTube Exploration: Awaiting API key

**Next Scan:** Tomorrow 6 AM (will use both features automatically)

---

**Last Updated:** February 7, 2026 11:36 PM PST
