# Fix Failing Scanners - Claude Code Task

## Problem
Multiple scanners are returning 0 results:
- 🔵 Twitter | 0 | ⚠️
- 🎥 YouTube | 0 | ⚠️
- 🤖 Moltbook | 0 | ⚠️
- 🟢 Health | 0 | ⚠️

## Your Task
Debug and fix each failing scanner so it returns results.

---

## Scanners to Fix

### 1. Twitter (`twitter_builders_monitor.py`)
**Expected:** Top 15 tweets from 112 builders  
**Getting:** 0 results

**Common Issues:**
- Nitter instance down/blocked
- Changed HTML structure (scraper broken)
- Rate limit exceeded
- Account list empty or invalid

**How to Fix:**
1. Run manually: `python3 twitter_builders_monitor.py`
2. Check error output
3. If Nitter instance down: Try different instance or use Twitter API
4. If scraping broken: Update selectors for current HTML structure
5. If rate limited: Add delays between requests
6. Test: Should output 15 tweets with scores

---

### 2. YouTube (`youtube_ai_monitor.py`)
**Expected:** Recent videos from 18 channels  
**Getting:** 0 results

**Common Issues:**
- API key missing/invalid
- API quota exceeded
- Channel list empty
- Wrong API endpoint

**How to Fix:**
1. Run manually: `python3 youtube_ai_monitor.py`
2. Check for API key errors
3. Check quota: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
4. Verify channel IDs are correct
5. Check `hours_back` parameter (should be 48)
6. Test: Should output videos with channel names

**API Key Location:** Look for `API_KEY` or similar in the file

---

### 3. Moltbook (`moltbook_scanner.py`)
**Expected:** Top 10 posts from AI agent feed  
**Getting:** 0 results

**Common Issues:**
- Auth token expired/invalid
- API endpoint changed
- Feed empty (unlikely)
- Wrong feed parameter

**How to Fix:**
1. Run manually: `python3 moltbook_scanner.py`
2. Check for auth errors (401, 403)
3. Verify token is still valid: https://moltbook.com (check account settings)
4. Check API endpoint is correct: `https://moltbook.com/api/`
5. Check feed limit parameter (should be 100)
6. Test: Should output 10 posts with scores

**Auth Token Location:** Look for `token` or `auth` or `bearer` in the file

---

### 4. Health (`health_tracker.py`)
**Expected:** Top 10 posts from health subreddits  
**Getting:** 0 results

**Common Issues:**
- Subreddit list empty
- Reddit API changed
- Filter too strict (no posts match)
- Wrong API endpoint

**How to Fix:**
1. Run manually: `python3 health_tracker.py`
2. Check error output
3. Verify subreddits: r/loseit, r/WholeFoodsPlantBased, r/PlantBasedDiet
4. Check filters aren't excluding all posts
5. Verify using Reddit JSON API: `https://www.reddit.com/r/loseit/.json`
6. Test: Should output 10 health posts

---

## Debugging Steps for Each Scanner

### Step 1: Run Manually
```bash
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper/"
python3 twitter_builders_monitor.py
```

**Look for:**
- Error messages
- API errors (401, 403, 429, 500)
- Empty responses
- Timeout errors

### Step 2: Check Network Connectivity
```bash
# Test APIs are reachable
curl -I https://nitter.net
curl -I https://www.googleapis.com/youtube/v3/
curl -I https://moltbook.com/api/
curl -I https://www.reddit.com/r/loseit/.json
```

### Step 3: Check Authentication
- YouTube: Verify API key is valid
- Moltbook: Verify token hasn't expired
- Reddit/Twitter: No auth needed, but check for rate limits

### Step 4: Test API Responses
```bash
# Test Reddit directly
curl "https://www.reddit.com/r/loseit/.json" | jq '.data.children | length'

# Test YouTube (replace YOUR_KEY)
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&key=YOUR_KEY"

# Test Moltbook (replace YOUR_TOKEN)
curl -H "Authorization: Bearer YOUR_TOKEN" "https://moltbook.com/api/feed"
```

### Step 5: Fix the Code
Based on errors found:
- Update API endpoints if changed
- Refresh tokens if expired
- Fix selectors if HTML structure changed
- Add error handling if missing
- Adjust filters if too strict

### Step 6: Test Again
```bash
python3 twitter_builders_monitor.py
python3 youtube_ai_monitor.py
python3 moltbook_scanner.py
python3 health_tracker.py
```

Each should output formatted text with results.

### Step 7: Run Full Workflow
```bash
python mydossier.py update
```

Should show counts > 0 for all platforms.

---

## Expected Output Format

**Twitter should output:**
```
📊 Score: 13278 (engagement: 13273 + bonus: 0)
💬 "Tweet text..."
🔗 https://twitter.com/...
```

**YouTube should output:**
```
**1. Video Title**
- Channel: Channel Name
- Published: 2h ago
- Link: https://youtube.com/...
```

**Moltbook should output:**
```
**1. Post Title**
- @agent_name • Score: 3578
- #hashtags
- ↑3547 • 💬12
- https://moltbook.com/post/...
```

**Health should output:**
```
📊 Post title...
- r/subreddit • #category
- ↑123 💬45
- https://reddit.com/...
```

---

## Common Quick Fixes

### If API Key/Token Expired
1. Get new key/token from service
2. Update in scanner file
3. Test immediately

### If API Endpoint Changed
1. Check service documentation
2. Update endpoint URL in code
3. Test with curl first

### If Scraping Broken (Twitter)
1. View page source: `curl https://nitter.net/username`
2. Find new selectors
3. Update BeautifulSoup/regex patterns

### If Rate Limited
1. Add delays: `time.sleep(1)` between requests
2. Reduce number of accounts/channels checked
3. Wait for limit to reset

---

## Verification Checklist

After fixing, verify:
- [ ] Twitter returns 10-15 tweets
- [ ] YouTube returns videos from multiple channels
- [ ] Moltbook returns 10 agent posts
- [ ] Health returns 10 health posts
- [ ] `python mydossier.py update` completes successfully
- [ ] Final `dossier.html` shows all platforms with content
- [ ] GitHub deployment succeeds
- [ ] Live page shows all platforms: https://DiamondDeals.github.io/daily-dossier/dossier.html

---

## Files to Check/Modify

**Scanner files:**
- `twitter_builders_monitor.py` (Twitter)
- `youtube_ai_monitor.py` (YouTube)
- `moltbook_scanner.py` (Moltbook)
- `health_tracker.py` (Health)

**Don't modify:**
- `run_full_digest.py` (main workflow - should be fine)
- `html_generator.py` (HTML generation - should be fine)
- Post-processing scripts (should be fine)

**Focus on:** Why scanners return 0 results instead of expected data.

---

## Priority Order

1. **YouTube** (easiest - probably just API key issue)
2. **Health** (second easiest - uses Reddit JSON like main scanner)
3. **Moltbook** (might be token expiration)
4. **Twitter** (hardest - might need scraper rewrite if Nitter changed)

Start with YouTube, then move down the list.

---

**Goal:** All 4 scanners returning results > 0

**Success Criteria:** 
```
🔵 Twitter   | 15 | ✅
🎥 YouTube   | 8  | ✅
🤖 Moltbook  | 10 | ✅
🟢 Health    | 10 | ✅
```
