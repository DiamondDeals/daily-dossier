#!/usr/bin/env python3
"""
5-Platform Daily Digest Runner
Reddit + Twitter + Moltbook + Health + YouTube
"""

import subprocess
import sys
from datetime import datetime

def run_platform(name, script):
    """Run a platform scanner and return results"""
    print(f"\n{'='*80}")
    print(f"🔍 Scanning {name}...")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            ["python3", script],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"✅ {name} completed")
            return result.stdout
        else:
            print(f"❌ {name} failed: {result.stderr}")
            return f"ERROR in {name}: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ {name} timed out")
        return f"TIMEOUT in {name}"
    except Exception as e:
        print(f"❌ {name} error: {str(e)}")
        return f"ERROR in {name}: {str(e)}"

def main():
    print(f"🚀 Starting 5-Platform Daily Digest")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PST')}")
    
    platforms = [
        ("Reddit", "reddit_json_client.py"),
        ("Twitter", "twitter_builders_monitor.py"),
        ("Moltbook", "moltbook_scanner.py"),
        ("Health", "health_tracker.py"),
        ("YouTube", "youtube_ai_monitor.py")
    ]
    
    results = {}
    for name, script in platforms:
        results[name] = run_platform(name, script)
    
    # TODO: Combine results and post to Slack
    print(f"\n{'='*80}")
    print(f"✅ All platforms scanned!")
    print(f"{'='*80}")
    
    # Show summary
    for name in results:
        if "ERROR" in results[name] or "TIMEOUT" in results[name]:
            print(f"❌ {name}: Failed")
        else:
            print(f"✅ {name}: Success")

if __name__ == "__main__":
    main()
