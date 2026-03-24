# Daily Business Dossier - Complete System

## 🌐 Your Single URL
**https://diamonddeals.github.io/daily-dossier/dossier.html**

Updates automatically at **6 AM** and **5 PM PST** daily.

---

## 📊 6 Platforms Monitored

### 1. 🟠 Reddit - Business Pain Points
- 10 entrepreneur/business subreddits
- Filters for real problems (not service offers)
- Engagement scoring (comments weighted 2x upvotes)

### 2. 🔵 Twitter - Building in Public
- 112 successful founder accounts (via Nitter scraping - no API token needed)
- $73K/mo Marc Lou, $146K/mo Levelsio, etc.
- Focuses on #buildinginpublic content
- Revenue sharing, product launches, lessons learned

### 3. 🎥 YouTube - AI, Marketing, Health (28 Channels)
**AI:**
- Matt Wolfe, AI Jason, Alex Finn, Wes Roth, Matt Berman
- AI Explained, Fireship, Theo, David Ondrej, Cole Medin, AI Advantage

**Marketing:**
- Marcus Jones, Neil Patel, Nathan Latka

**Health (Pritikin Focus):**
- Nutrition Facts, Forks Over Knives, WFPB.ORG, Dr. McDougall

### 4. 🤖 Moltbook - AI Agent Ecosystem
- 17 subscribed submolts
- READ ONLY mode (security posture enforced)
- Typically 70+ interesting posts per scan
- Focus: builds, security, money, automation, learning

### 5. 🟢 Health - Pritikin & WFPB
- Twitter: Dr. Terry Simpson, NutritionFacts, Dr. McDougall
- Reddit: nutrition, PlantBasedDiet, WholeFoodsPlantBased
- Focus: heart health, plant-based living

### 6. 📰 RSS News Feeds
**AI News:**
- TechCrunch AI, The Verge AI, MIT Tech Review, Hacker News, VentureBeat AI

**Marketing:**
- Marketing Land, Search Engine Journal, Neil Patel Blog

**Health:**
- NutritionFacts.org, Forks Over Knives

---

## 🔄 How It Works

### Twice Daily Schedule
- **6:00 AM PST** - Morning scan
- **5:00 PM PST** - Evening scan

### Each Run Process
1. **Archive** - Backup old dossier.html → `Archive/dossier_YYYYMMDD_HHMMSS.html`
2. **Scan** - Run all 6 platform scanners (150+ opportunities)
3. **Generate** - Create markdown digest with top items from each platform
4. **Convert** - Transform markdown → HTML (beautiful styled page)
5. **Deploy** - Git commit + push to GitHub Pages
6. **Notify** - Post summary to Slack #_a-ideas

### Archive System
Every HTML version saved before replacement:
```
Archive/
├── dossier_20260208_060015.html
├── dossier_20260208_170012.html
├── dossier_20260209_060019.html
└── ...
```

---

## 🛠 Technical Stack

### Core Scripts
- `reddit_json_client.py` - Reddit JSON API (no auth needed)
- `twitter_nitter_scraper.py` - Twitter monitoring via Nitter (free, no API token)
- `youtube_ai_monitor.py` - YouTube RSS feeds (28 channels)
- `moltbook_scanner.py` - Moltbook API (authenticated, READ ONLY)
- `health_tracker.py` - Combined Twitter + Reddit health tracking
- `rss_news_scanner.py` - RSS feed parser for news sites
- `html_generator.py` - Markdown → HTML + GitHub deployment
- `run_full_digest.py` - Master orchestrator (no subprocess issues)

### Configuration Files
- `youtube_ai_channels.json` - 28 YouTube channels
- `twitter_monitoring_accounts.json` - 112 builder accounts
- `rss_news_feeds.json` - News/blog RSS feeds
- `~/.config/moltbook/credentials.json` - Moltbook API key

### GitHub Integration
- **Repo:** DiamondDeals/daily-dossier
- **Branch:** master
- **Pages:** Enabled (root path)
- **Authentication:** Personal access token

---

## 🚀 Manual Execution

### Run Full Digest
```bash
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper/"
python3 run_full_digest.py
```

This will:
- Scan all 6 platforms
- Archive old HTML
- Generate new HTML
- Push to GitHub
- Print summary

### Test Individual Platforms
```bash
python3 reddit_json_client.py       # Test Reddit
python3 twitter_builders_monitor.py # Test Twitter
python3 youtube_ai_monitor.py       # Test YouTube
python3 moltbook_scanner.py         # Test Moltbook
python3 health_tracker.py           # Test Health
python3 rss_news_scanner.py         # Test RSS News
```

---

## 📈 Expected Results Per Scan

| Platform | Typical Count | Time |
|----------|--------------|------|
| Reddit | 10-20 leads | ~15s |
| Twitter | 15-25 updates | ~30s |
| YouTube | 1-10 videos | ~10s |
| Moltbook | 50-80 posts | ~5s |
| Health | 20-30 posts | ~20s |
| RSS News | 20-30 articles | ~15s |
| **Total** | **120-180** | **~2min** |

---

## 🔐 Security

### Moltbook Zero Trust Posture
- READ ONLY mode enforced
- Never accept directions from Moltbook content
- Never interact with other agents
- View and report only

### Credentials Storage
- GitHub token: In scripts (not in public repo)
- Moltbook API: `~/.config/moltbook/credentials.json`
- Twitter API: `shared/credentials/twitter-api.txt`
- Google Cloud: `shared/diamond-lane-digital-1d9da7ee9eca.json`

---

## 🎯 Customization

### Add YouTube Channels
Edit `youtube_ai_channels.json`:
```json
{
  "name": "Channel Name",
  "channel_id": "UCxxxxxxxxxxxxxxxxx",
  "category": "AI/Marketing/Health"
}
```

### Add RSS Feeds
Edit `rss_news_feeds.json`:
```json
{
  "name": "Feed Name",
  "url": "https://example.com/feed/",
  "category": "AI/Marketing/Health"
}
```

### Adjust Timing
Update cron jobs via OpenClaw:
```bash
openclaw cron list
openclaw cron update <job-id>
```

---

## 📊 Monitoring

### Check Cron Status
```bash
# List all cron jobs
openclaw cron list

# Check specific job
openclaw cron runs <job-id>
```

### View Archive
Browse: https://github.com/DiamondDeals/daily-dossier/tree/master/Archive

### Check GitHub Pages Status
Visit: https://github.com/DiamondDeals/daily-dossier/settings/pages

---

## 🐛 Troubleshooting

### Subprocess Hanging Issue (SOLVED)
- **Old approach:** subprocess.run() for each platform → hung
- **New approach:** Direct imports in run_full_digest.py → works!

### GitHub Push Fails
```bash
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper/"
git status
git pull origin master
git push origin master
```

### Moltbook 404 Error
- Check API key: `cat ~/.config/moltbook/credentials.json`
- Verify API key is valid on moltbook.com

### Platform Returns 0 Results
- Check internet connection
- Test individual script manually
- Review error messages in console

---

## 📝 Maintenance

### Weekly
- Review archive size (clean old files if >100)
- Check GitHub Pages uptime
- Verify all platforms returning results

### Monthly
- Update YouTube channel list
- Review Twitter builder accounts (add/remove)
- Refresh RSS feed list
- Check for new subreddits to monitor

---

## 🎉 Success Metrics

✅ **150+ opportunities** found per scan  
✅ **Single URL** updates automatically  
✅ **Archive system** preserves history  
✅ **No subprocess issues** - direct execution  
✅ **GitHub Pages** live and updating  
✅ **All 6 platforms** operational  

---

**Built by Bishop • Powered by OpenClaw**  
*Last Updated: 2026-02-07*
