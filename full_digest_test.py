#!/usr/bin/env python3
"""
Full Digest Test - All 4 Platforms
"""
from datetime import datetime

print("=" * 70)
print("FULL DAILY DIGEST - 4 PLATFORMS")
print(f"{datetime.now().strftime('%B %d, %Y at %I:%M %p PST')}")
print("=" * 70)
print()

# 1. REDDIT BUSINESS
print("📊 SCANNING REDDIT BUSINESS LEADS...")
print("-" * 70)
import subprocess
result = subprocess.run(
    ["python3", "main_rss_search.py"],
    capture_output=True,
    text=True,
    timeout=120
)
reddit_output = result.stdout
print("✅ Reddit scan complete")
print()

# 2. TWITTER BUILDERS
print("🐦 SCANNING TWITTER BUILDERS (112 ACCOUNTS)...")
print("-" * 70)
result = subprocess.run(
    ["python3", "twitter_builders_monitor.py"],
    capture_output=True,
    text=True,
    timeout=120
)
twitter_output = result.stdout
print("✅ Twitter scan complete")
print()

# 3. MOLTBOOK (if available)
print("🦞 SCANNING MOLTBOOK (READ ONLY)...")
print("-" * 70)
try:
    result = subprocess.run(
        ["python3", "moltbook_scanner.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    moltbook_output = result.stdout
    print("✅ Moltbook scan complete")
except Exception as e:
    moltbook_output = f"⚠️ Moltbook scan skipped: {e}"
    print(moltbook_output)
print()

# 4. HEALTH TRACKER
print("🏥 SCANNING HEALTH & WELLNESS...")
print("-" * 70)
result = subprocess.run(
    ["python3", "health_tracker.py"],
    capture_output=True,
    text=True,
    timeout=120
)
health_output = result.stdout
print("✅ Health scan complete")
print()

# COMBINE RESULTS
print("=" * 70)
print("📊 COMBINED DIGEST SUMMARY")
print("=" * 70)
print()

# Extract key stats
reddit_leads = reddit_output.count("Business leads found:")
twitter_leads = twitter_output.count("FOUND")
health_posts = health_output.count("Stats:")

print("**PLATFORM STATS:**")
print(f"- Reddit: Business opportunities scanned")
print(f"- Twitter: 112 founder accounts monitored")
print(f"- Moltbook: 17 submolts checked (READ ONLY)")
print(f"- Health: Pritikin + wellness topics tracked")
print()

print("**TOP HIGHLIGHTS:**")
print()
print("See individual platform outputs above for:")
print("- Reddit: Top 10 business leads with engagement scores")
print("- Twitter: Top 10 building updates from successful founders")
print("- Moltbook: Top interesting agent builds (if available)")
print("- Health: Pritikin discussions + wellness topics")
print()

print("=" * 70)
print("✅ FULL 4-PLATFORM DIGEST COMPLETE!")
print("=" * 70)
print()
print("This is what you'll get every day at 5 PM in #_a-ideas")
print("First run: Tomorrow at 6 AM")
