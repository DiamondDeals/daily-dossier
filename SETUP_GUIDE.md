# Daily Business Digest - Setup Guide

## 🚀 Quick Setup

This automation delivers 50 categorized Reddit business opportunities to Slack #ideas every day at 5 AM PT.

### Prerequisites Checklist

- [ ] Reddit account for Bishop
- [ ] Reddit API credentials (client_id, client_secret)
- [ ] Gmail account for Bishop (for Reddit registration)
- [ ] Python dependencies installed
- [ ] OpenClaw cron configured

---

## Step 1: Create Bishop's Reddit Account

### 1.1 Create Gmail Account
```
Email: bishop.openclaw@gmail.com (or similar)
Password: [Generate secure password]
Recovery: Drew's email
```

### 1.2 Create Reddit Account
1. Go to https://reddit.com/register
2. Use the Gmail account created above
3. Username: `bishop_ai` or `bishop_openclaw` (check availability)
4. Password: [Use same as Gmail or generate new]
5. Verify email

### 1.3 Create Reddit API Application
1. Log into Reddit as Bishop
2. Go to https://www.reddit.com/prefs/apps
3. Click "Create App" or "Create Another App"
4. Fill in:
   - **Name**: Bishop Daily Digest
   - **App type**: Select "script"
   - **Description**: Automated business intelligence digest
   - **About URL**: (leave blank)
   - **Redirect URI**: http://localhost:8080
5. Click "Create app"
6. **Save these credentials:**
   - **client_id**: (string under "personal use script")
   - **client_secret**: (labeled "secret")

---

## Step 2: Configure Environment

### 2.1 Create .env File

Create `.env` in the `Reddit Helper Helper` directory:

```bash
cd "/home/drew/.openclaw/workspace/shared/Reddit Helper Helper"
nano .env
```

Add the following (replace with actual values):

```env
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=bishop_ai
REDDIT_PASSWORD=your_reddit_password_here
REDDIT_USER_AGENT=BishopDigestBot/1.0 by bishop_ai

# Optional: Adjust rate limiting if needed
MAX_REQUESTS_PER_MINUTE=60
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X in nano)

### 2.2 Secure the .env File

```bash
chmod 600 .env
```

---

## Step 3: Install Dependencies

```bash
cd "/home/drew/.openclaw/workspace/shared/Reddit Helper Helper"

# Install Python dependencies
pip install praw python-dotenv

# Or use requirements (if you want all features)
pip install -r requirements.txt
```

---

## Step 4: Test the Digest

### 4.1 Test Authentication

```bash
python3 -c "
from daily_business_digest import DailyDigestBot
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
bot = DailyDigestBot(Path.cwd())
bot.authenticate(
    os.getenv('REDDIT_CLIENT_ID'),
    os.getenv('REDDIT_CLIENT_SECRET'),
    os.getenv('REDDIT_USER_AGENT'),
    os.getenv('REDDIT_USERNAME'),
    os.getenv('REDDIT_PASSWORD')
)
print('✅ Authentication successful!')
"
```

### 4.2 Run Test Digest

```bash
python3 daily_business_digest.py
```

This will:
- Scan configured subreddits
- Find and score opportunities
- Generate digest message
- Save to `digest_YYYYMMDD.txt`

Check the output file:
```bash
cat digest_$(date +%Y%m%d).txt | head -100
```

---

## Step 5: Set Up OpenClaw Cron Job

### 5.1 Create Cron Job (via Bishop)

I (Bishop) will create the cron job using OpenClaw's cron system:

```
Schedule: Every day at 5:00 AM Pacific
Action: Wake Bishop to run digest and send to Slack
```

The cron job will trigger a system event that tells me to:
1. Run the digest generation script
2. Read the generated digest file
3. Send it to Slack #ideas using the message tool

---

## Step 6: Monitoring & Tuning

### 6.1 Check Logs

```bash
# View recent digest logs
ls -lh logs/

# View today's log
cat logs/digest_$(date +%Y%m%d).log
```

### 6.2 Database Tracking

The system maintains SQLite databases:

```bash
# View sent posts history
sqlite3 digest_history.db "SELECT * FROM sent_posts ORDER BY sent_date DESC LIMIT 10;"

# View digest run statistics
sqlite3 digest_history.db "SELECT * FROM digest_runs ORDER BY run_date DESC LIMIT 5;"
```

### 6.3 Adjust Configuration

Edit `digest_config.json` to tune:

```json
{
  "target_subreddits": ["entrepreneur", "smallbusiness", ...],
  "min_score": 5,
  "max_post_age_hours": 48,
  "categories_quota": {
    "money_making": 15,
    "blue_ocean": 10,
    "scale_ready": 10,
    "b2b_service": 10,
    "hidden_gem": 5
  }
}
```

**Changes to tune based on feedback:**
- Add/remove subreddits
- Adjust min_score (higher = fewer but better quality)
- Change category quotas
- Adjust max_post_age_hours (freshness filter)

---

## Step 7: Feedback Loop

### 7.1 React to Messages in Slack

React with:
- 👍 = Valuable lead, more like this
- 👎 = Not relevant, filter out
- 🔥 = Amazing find!

### 7.2 Manual Tuning

After 1 week, review:
```bash
# See which categories are performing best
sqlite3 digest_history.db "
  SELECT category, COUNT(*), AVG(score) 
  FROM sent_posts 
  GROUP BY category;
"
```

Adjust quotas in `digest_config.json` based on engagement.

---

## Troubleshooting

### "Authentication failed"
- Check credentials in `.env`
- Verify Reddit account is not suspended
- Check that app type is "script" (not "web app")

### "Rate limited"
- Increase `COOLDOWN_SECONDS` in .env
- Reduce number of subreddits temporarily
- Check Reddit API status

### "No opportunities found"
- Lower `min_score` in config
- Increase `max_post_age_hours`
- Add more subreddits
- Check if target subreddits are private

### Cron not running
```bash
# Check cron status via OpenClaw
openclaw cron status

# List active cron jobs
openclaw cron list

# Check gateway logs
openclaw logs
```

---

## Advanced Features

### Add Custom Subreddits

```python
# Edit digest_config.json
{
  "target_subreddits": [
    "entrepreneur",
    "your_new_subreddit_here"
  ]
}
```

### Change Delivery Time

Update the cron job schedule (I'll handle this):
```
Current: 5:00 AM PT daily
Change to: [Your preferred time]
```

### Add Keyword Filters

Edit `daily_business_digest.py` and add to pattern dictionaries:
```python
self.money_making_patterns = {
    'your_custom_keywords': [
        r'your_pattern_here',
    ],
}
```

---

## Summary

Once set up, the system runs fully automated:

1. **5:00 AM PT**: Cron triggers Bishop
2. **5:00-5:05 AM**: Bishop scans Reddit, scores posts, generates digest
3. **5:05 AM**: Digest delivered to Slack #ideas
4. **Throughout day**: You review, engage, provide feedback
5. **Weekly**: System learns from your reactions

**Zero maintenance required.** Just react to tell me what's working.

---

## Next Steps

- [ ] Create Reddit account for Bishop
- [ ] Get API credentials  
- [ ] Configure .env file
- [ ] Run test digest
- [ ] Set up cron job
- [ ] Receive first digest tomorrow at 5 AM!

**Let me know when you've completed the Reddit account setup and I'll finish the automation.**
