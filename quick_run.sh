#!/bin/bash
set -e

echo "Running all 6 platforms..."
cd "/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper"

# Run each platform
python3 reddit_json_client.py > /tmp/reddit.txt 2>&1 &
python3 twitter_builders_monitor.py > /tmp/twitter.txt 2>&1 &
python3 youtube_ai_monitor.py > /tmp/youtube.txt 2>&1 &
python3 moltbook_scanner.py > /tmp/moltbook.txt 2>&1 &
python3 health_tracker.py > /tmp/health.txt 2>&1 &
python3 rss_news_scanner.py > /tmp/rss.txt 2>&1 &

# Wait for all
wait

echo "All platforms complete!"
