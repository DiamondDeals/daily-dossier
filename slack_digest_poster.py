#!/usr/bin/env python3
"""
Slack Digest Poster
Posts combined 5-platform digest to #_a-ideas
"""

import subprocess
import json
import sys
from datetime import datetime

# Slack channel
CHANNEL_ID = "C0AD3RP0Y5U"  # #_a-ideas

def run_scanner(script_name):
    """Run a scanner and capture output"""
    try:
        result = subprocess.run(
            ["python3", script_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        print(f"Error running {script_name}: {str(e)}")
        return None

def parse_reddit_count(output):
    """Extract Reddit lead count"""
    if not output:
        return 0
    lines = output.split('\n')
    for line in lines:
        if 'Found' in line and 'leads' in line:
            try:
                return int(line.split('Found')[1].split('leads')[0].strip())
            except:
                pass
    return 0

def parse_twitter_count(output):
    """Extract Twitter update count"""
    if not output:
        return 0
    lines = output.split('\n')
    for line in lines:
        if 'Found' in line and 'building updates' in line:
            try:
                return int(line.split('Found')[1].split('building')[0].strip())
            except:
                pass
    return 0

def parse_health_count(output):
    """Extract Health post count"""
    if not output:
        return 0
    lines = output.split('\n')
    for line in lines:
        if 'Stats:' in line:
            try:
                parts = line.split('Stats:')[1].strip()
                # Parse "2 Twitter + 24 Reddit"
                total = 0
                for part in parts.split('+'):
                    num = int(part.strip().split()[0])
                    total += num
                return total
            except:
                pass
    return 0

def parse_youtube_count(output):
    """Extract YouTube video count"""
    if not output:
        return 0
    lines = output.split('\n')
    for line in lines:
        if 'YouTube AI Digest' in line and 'videos' in line:
            try:
                return int(line.split('(')[1].split('videos')[0].strip())
            except:
                pass
    return 0

def main():
    print("🚀 Running 5-Platform Daily Digest...")
    
    # Run all scanners
    reddit_output = run_scanner("reddit_json_client.py")
    twitter_output = run_scanner("twitter_builders_monitor.py")
    health_output = run_scanner("health_tracker.py")
    youtube_output = run_scanner("youtube_ai_monitor.py")
    
    # Parse counts
    reddit_count = parse_reddit_count(reddit_output)
    twitter_count = parse_twitter_count(twitter_output)
    health_count = parse_health_count(health_output)
    youtube_count = parse_youtube_count(youtube_output)
    moltbook_count = 0  # API not working yet
    
    total = reddit_count + twitter_count + health_count + youtube_count + moltbook_count
    
    # Build digest message
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p PST")
    
    message = f"""🔍 **Daily Opportunity Digest** - {now}

**📊 Summary:** {total} opportunities found across 5 platforms

• 🟠 **Reddit:** {reddit_count} business pain points
• 🔵 **Twitter:** {twitter_count} building updates from top founders
• 🟢 **Health:** {health_count} Pritikin/WFPB discussions
• 🎥 **YouTube:** {youtube_count} AI videos
• 🤖 **Moltbook:** {moltbook_count} (API pending)

_Full exports saved to workspace. React with 📧 for detailed reports._
"""
    
    print(message)
    print("\n" + "="*80)
    print("📤 Posting to Slack #_a-ideas...")
    
    # Post to Slack via OpenClaw message tool
    # Using echo to stdin to avoid escaping issues
    slack_cmd = f'message send --channel={CHANNEL_ID} --message="{message}"'
    
    try:
        # Write message to temp file to avoid escaping issues
        with open('/tmp/digest_message.txt', 'w') as f:
            f.write(message)
        
        result = subprocess.run(
            ['bash', '-c', f'cat /tmp/digest_message.txt | xargs -0 -I {{}} openclaw message send --channel={CHANNEL_ID} --message="{{}}"'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Posted to Slack successfully!")
        else:
            print(f"⚠️ Slack post may have failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error posting to Slack: {str(e)}")
    
    return total

if __name__ == "__main__":
    total = main()
    sys.exit(0 if total > 0 else 1)
