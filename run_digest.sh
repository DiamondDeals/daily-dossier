#!/bin/bash
# Daily Digest Runner - Simple Shell Script (no subprocess issues)

BASE_DIR="/home/drew/.openclaw/workspace/shared/Python Stuff/Pet/Reddit Helper Helper"
cd "$BASE_DIR"

echo "🚀 Starting 5-Platform Daily Digest..."
date

# Run all scanners and capture counts
echo "=== Running Reddit scanner..."
reddit_output=$(python3 reddit_json_client.py 2>&1)
reddit_count=$(echo "$reddit_output" | grep -oP 'Found \K\d+(?= leads)' | head -1)
[[ -z "$reddit_count" ]] && reddit_count=0

echo "=== Running Twitter scanner..."
twitter_output=$(python3 twitter_builders_monitor.py 2>&1)
twitter_count=$(echo "$twitter_output" | grep -oP 'Found \K\d+(?= building)' | head -1)
[[ -z "$twitter_count" ]] && twitter_count=0

echo "=== Running Health tracker..."
health_output=$(python3 health_tracker.py 2>&1)
health_count=$(echo "$health_output" | grep -oP 'Found: \K\d+' | tail -1)
[[ -z "$health_count" ]] && health_count=0

echo "=== Running YouTube scanner..."
youtube_output=$(python3 youtube_ai_monitor.py 2>&1)
youtube_count=$(echo "$youtube_output" | grep -oP '\(\K\d+(?= videos\))' | head -1)
[[ -z "$youtube_count" ]] && youtube_count=0

# Moltbook currently returns 0 (API pending)
moltbook_count=0

# Calculate total
total=$((reddit_count + twitter_count + health_count + youtube_count + moltbook_count))

# Build message
timestamp=$(date '+%Y-%m-%d %I:%M %p PST')
message="🔍 **Daily Opportunity Digest** - $timestamp

**📊 Summary:** $total opportunities found across 5 platforms

• 🟠 **Reddit:** $reddit_count business pain points
• 🔵 **Twitter:** $twitter_count building updates from top founders
• 🟢 **Health:** $health_count Pritikin/WFPB discussions
• 🎥 **YouTube:** $youtube_count AI videos
• 🤖 **Moltbook:** $moltbook_count (API pending)

_Full exports in workspace /Reddit Helper Helper/Exports/_
React 📧 for detailed breakdown."

echo ""
echo "================================"
echo "$message"
echo "================================"

# Post to Slack #_a-ideas (C0AD3RP0Y5U)
echo ""
echo "📤 Posting to Slack..."

# Use OpenClaw message tool via Python (simpler than bash escaping)
python3 << PYTHON
from openclaw_tools import post_to_slack
post_to_slack("C0AD3RP0Y5U", """$message""")
PYTHON

echo "✅ Digest complete!"
