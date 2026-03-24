# 🚀 Quick Start: Create Bishop's Reddit Account

**Time Required:** 10 minutes  
**Goal:** Get Bishop's Reddit credentials for the daily digest

---

## Step 1: Create Gmail Account (2 minutes)

1. Go to https://accounts.google.com/signup
2. Fill in:
   - **First name:** Bishop
   - **Last name:** OpenClaw (or AI, or whatever)
   - **Username:** Try these in order:
     - `bishop.openclaw@gmail.com`
     - `bishopopenclawai@gmail.com`
     - `bishopai.digest@gmail.com`
   - **Password:** Generate strong password (save it!)
3. **Recovery email:** Add your personal email (drewlovesai@gmail.com)
4. **Skip** phone number if possible
5. Complete setup

**Save these credentials:**
```
Gmail: bishop.openclaw@gmail.com (or whatever you got)
Password: [your password]
```

---

## Step 2: Create Reddit Account (3 minutes)

1. Go to https://www.reddit.com/register
2. Fill in:
   - **Email:** Use the Gmail you just created
   - **Username:** Try these:
     - `bishop_ai`
     - `bishop_openclaw`
     - `bishopdaily`
     - `businessintel_bot`
3. **Password:** Can use same as Gmail or generate new
4. Click "Sign Up"
5. **Verify email:** Check the Gmail inbox and click verification link
6. Skip the "what are you interested in" tour (or quickly click through)

**Save these credentials:**
```
Reddit Username: bishop_ai (or whatever you got)
Reddit Password: [your password]
```

---

## Step 3: Create Reddit API Application (5 minutes)

1. **Log into Reddit** as Bishop (the account you just created)
2. Go to: https://www.reddit.com/prefs/apps
3. Scroll to bottom, click **"Create App"** or **"Create Another App"**
4. Fill in the form:

```
┌─────────────────────────────────────────────┐
│ Name:                                       │
│ Bishop Daily Digest                        │
│                                             │
│ App type:                                   │
│ ● script    ○ web app    ○ installed app   │  ← Select "script"
│                                             │
│ Description:                                │
│ Automated business intelligence digest     │
│                                             │
│ About URL:                                  │
│ [leave blank]                               │
│                                             │
│ Redirect URI:                               │
│ http://localhost:8080                       │
│                                             │
└─────────────────────────────────────────────┘
```

5. Click **"Create app"**

6. **Find your credentials** on the next page:

```
Bishop Daily Digest
personal use script         ← This is your CLIENT_ID
[random string]

secret: xxxxxxxxxxxxxx      ← This is your CLIENT_SECRET
         [show]
```

**Save these credentials:**
```
Client ID: [the string under "personal use script"]
Client Secret: [the string after "secret:"]
```

---

## Step 4: Configure .env File

Now create the configuration file:

```bash
cd "/home/drew/.openclaw/workspace/shared/Reddit Helper Helper"
nano .env
```

Copy and paste this template, **replacing the placeholder values**:

```env
# Reddit API Credentials
REDDIT_CLIENT_ID=paste_your_client_id_here
REDDIT_CLIENT_SECRET=paste_your_client_secret_here
REDDIT_USERNAME=bishop_ai
REDDIT_PASSWORD=paste_your_reddit_password_here
REDDIT_USER_AGENT=BishopDigestBot/1.0 by bishop_ai

# Rate Limiting (defaults are fine)
MAX_REQUESTS_PER_MINUTE=60
```

**Save and exit:**
- Press `Ctrl + O` (WriteOut)
- Press `Enter` (confirm filename)
- Press `Ctrl + X` (exit)

**Secure the file:**
```bash
chmod 600 .env
```

---

## Step 5: Test It!

```bash
cd "/home/drew/.openclaw/workspace/shared/Reddit Helper Helper"

# Test authentication
python3 -c "
from daily_business_digest import DailyDigestBot
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
bot = DailyDigestBot(Path.cwd())
result = bot.authenticate(
    os.getenv('REDDIT_CLIENT_ID'),
    os.getenv('REDDIT_CLIENT_SECRET'),
    os.getenv('REDDIT_USER_AGENT'),
    os.getenv('REDDIT_USERNAME'),
    os.getenv('REDDIT_PASSWORD')
)
if result:
    print('✅ SUCCESS! Bishop is authenticated with Reddit.')
else:
    print('❌ Authentication failed. Check credentials.')
"
```

If you see **"✅ SUCCESS!"**, you're done! 🎉

If you see an error:
- Double-check credentials in `.env`
- Make sure Reddit app type is "script"
- Verify email was confirmed on Reddit account

---

## Step 6: Run Test Digest

```bash
python3 daily_business_digest.py
```

This will:
- Scan all configured subreddits (~5-10 minutes)
- Find and score opportunities
- Generate `digest_YYYYMMDD.txt`
- Show progress in terminal

**Check the output:**
```bash
cat digest_$(date +%Y%m%d).txt | head -100
```

If you see a formatted digest with categories and opportunities, **it's working!** 🚀

---

## Step 7: Tell Bishop You're Ready

Come back to Slack and tell me:

**"@Bishop I've set up the Reddit account. Credentials are in .env. Test run worked. Let's go live!"**

I'll then:
1. Set up the cron job for 5 AM PT daily
2. Verify everything is working
3. Deliver your first digest tomorrow morning

---

## 🎯 Quick Reference Card

Save these for later:

```
BISHOP'S REDDIT CREDENTIALS
═══════════════════════════════════════════

Gmail:
  Email: _______________________________
  Password: ____________________________

Reddit Account:
  Username: _______________________________
  Password: _______________________________

Reddit API:
  Client ID: ______________________________
  Client Secret: __________________________
  
File Location:
  /home/drew/.openclaw/workspace/shared/Reddit Helper Helper/.env

Test Command:
  cd "shared/Reddit Helper Helper" && python3 daily_business_digest.py
```

---

## 🆘 Troubleshooting

### "Username already taken"
Try variations: `bishop_ai2`, `bishop_daily`, `businessintel_ai`, etc.

### "Email already in use"
Use a variation of the Gmail: `bishopai2@gmail.com`, etc.

### "Invalid credentials" error
1. Check .env file has no extra spaces
2. Verify you're using CLIENT_ID not the app name
3. Make sure app type is "script" not "web app"

### "praw not installed"
```bash
pip install praw python-dotenv
```

### Still stuck?
Paste the exact error message in Slack and I'll help debug.

---

## ✅ Done!

Once this is complete, you'll have:
- ✅ Gmail account for Bishop
- ✅ Reddit account for Bishop
- ✅ Reddit API credentials
- ✅ .env file configured
- ✅ Test run successful

**Next:** Daily automated digests at 5 AM PT starting tomorrow!

**Time investment:** 10 minutes  
**Value generated:** Hundreds of qualified leads/month

**Let's go get rich.** 💰

— Bishop 🧠
