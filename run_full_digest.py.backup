#!/usr/bin/env python3
"""
Full Digest Runner - All 6 Platforms
No subprocess issues - direct imports and execution
"""

import sys
import os
import shutil
import subprocess
from datetime import datetime

# Import all scanners
from reddit_json_client import RedditJSONClient
from twitter_builders_monitor import TwitterBuildersMonitor
from youtube_ai_monitor import YouTubeAIMonitor
from health_tracker import HealthTracker
from moltbook_scanner import MoltbookScanner
from rss_news_scanner import RSSNewsScanner
from html_generator import DigestHTMLGenerator

def run_full_digest():
    """Run all platforms and generate complete digest"""
    print("=" * 80)
    print("🚀 RUNNING FULL 6-PLATFORM DIGEST")
    print("=" * 80)
    print()
    
    results = {}
    
    # 1. Reddit
    print("🟠 REDDIT - Business Pain Points")
    try:
        reddit = RedditJSONClient()
        reddit_posts = reddit.scan_subreddits()
        results['reddit'] = {'count': len(reddit_posts), 'posts': reddit_posts}
        print(f"✅ Found {len(reddit_posts)} Reddit leads\n")
    except Exception as e:
        print(f"❌ Reddit failed: {e}\n")
        results['reddit'] = {'count': 0, 'posts': []}
    
    # 2. Twitter
    print("🔵 TWITTER - Building in Public")
    try:
        twitter = TwitterBuildersMonitor()
        twitter_updates = twitter.scan_builders()
        results['twitter'] = {'count': len(twitter_updates), 'posts': twitter_updates}
        print(f"✅ Found {len(twitter_updates)} Twitter updates\n")
    except Exception as e:
        print(f"❌ Twitter failed: {e}\n")
        results['twitter'] = {'count': 0, 'posts': []}
    
    # 3. YouTube
    print("🎥 YOUTUBE - AI Videos")
    try:
        youtube = YouTubeAIMonitor()
        youtube_videos = youtube.scan_all_channels()
        # Flatten dict to list
        all_videos = []
        for channel_videos in youtube_videos.values():
            all_videos.extend(channel_videos)
        results['youtube'] = {'count': len(all_videos), 'videos': all_videos}
        print(f"✅ Found {len(all_videos)} YouTube videos\n")
    except Exception as e:
        print(f"❌ YouTube failed: {e}\n")
        results['youtube'] = {'count': 0, 'videos': []}
    
    # 4. Moltbook
    print("🤖 MOLTBOOK - AI Agent Ecosystem")
    try:
        moltbook = MoltbookScanner()
        moltbook_posts = moltbook.scan_feed(limit=100)
        results['moltbook'] = {'count': len(moltbook_posts), 'posts': moltbook_posts}
        print(f"✅ Found {len(moltbook_posts)} Moltbook posts\n")
    except Exception as e:
        print(f"❌ Moltbook failed: {e}\n")
        results['moltbook'] = {'count': 0, 'posts': []}
    
    # 5. Health
    print("🟢 HEALTH - Pritikin & WFPB")
    try:
        health = HealthTracker()
        health_posts = health.scan_all()
        results['health'] = {'count': len(health_posts), 'posts': health_posts}
        print(f"✅ Found {len(health_posts)} Health posts\n")
    except Exception as e:
        print(f"❌ Health failed: {e}\n")
        results['health'] = {'count': 0, 'posts': []}
    
    # 6. RSS News
    print("📰 RSS NEWS - AI, Marketing, Health News")
    try:
        rss = RSSNewsScanner()
        rss_articles = rss.scan_all_feeds(hours_back=24)
        # Flatten
        all_articles = []
        for articles in rss_articles.values():
            all_articles.extend(articles)
        results['rss'] = {'count': len(all_articles), 'articles': all_articles}
        print(f"✅ Found {len(all_articles)} RSS articles\n")
    except Exception as e:
        print(f"❌ RSS News failed: {e}\n")
        results['rss'] = {'count': 0, 'articles': []}
    
    # Calculate total
    total = sum(r['count'] for r in results.values())
    
    print("=" * 80)
    print(f"📊 TOTAL: {total} opportunities found across 6 platforms")
    print("=" * 80)
    print()
    
    # Generate combined markdown
    markdown = generate_combined_markdown(results)
    
    # Save markdown
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_file = f"Exports/full_digest_{timestamp}.md"
    os.makedirs("Exports", exist_ok=True)
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✅ Saved markdown to: {md_file}\n")
    
    # Generate HTML
    print("🌐 Generating HTML...")
    html_gen = DigestHTMLGenerator()
    
    # Archive old version
    html_gen.archive_current_html()
    
    # Convert to HTML
    html = html_gen.markdown_to_html(markdown, "Daily Business Dossier")
    html_gen.save_html(html)
    
    # Deploy to GitHub
    print("\n📤 Deploying to GitHub Pages...")
    url = html_gen.deploy_to_github()
    
    if url:
        print(f"\n✅ COMPLETE! View at: {url}")
    
    return results

def generate_combined_markdown(results):
    """Generate combined markdown digest"""
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p PST")
    total = sum(r['count'] for r in results.values())
    
    md = f"""# 📊 Daily Business Dossier
## {timestamp}

**Total Opportunities: {total}**

---

## 📊 Platform Summary

| Platform | Count | Status |
|----------|-------|--------|
| 🟠 Reddit | {results['reddit']['count']} | {'✅' if results['reddit']['count'] > 0 else '⚠️'} |
| 🔵 Twitter | {results['twitter']['count']} | {'✅' if results['twitter']['count'] > 0 else '⚠️'} |
| 🎥 YouTube | {results['youtube']['count']} | {'✅' if results['youtube']['count'] > 0 else '⚠️'} |
| 🤖 Moltbook | {results['moltbook']['count']} | {'✅' if results['moltbook']['count'] > 0 else '⚠️'} |
| 🟢 Health | {results['health']['count']} | {'✅' if results['health']['count'] > 0 else '⚠️'} |
| 📰 RSS News | {results['rss']['count']} | {'✅' if results['rss']['count'] > 0 else '⚠️'} |

---

## 🟠 Reddit Business Leads

"""
    
    # Add top 10 from each platform
    if results['reddit']['count'] > 0:
        for i, post in enumerate(results['reddit']['posts'][:10], 1):
            md += f"\n**{i}. {post.get('title', 'Untitled')}**\n"
            md += f"- r/{post.get('subreddit', 'unknown')} • u/{post.get('author', 'unknown')}\n"
            md += f"- Score: {post.get('score', 0)} (↑{post.get('ups', 0)} • 💬{post.get('num_comments', 0)})\n"
            md += f"- {post.get('url', '')}\n"
    else:
        md += "\n_No Reddit leads found_\n"
    
    md += "\n---\n\n## 🔵 Twitter Building Updates\n"
    
    if results['twitter']['count'] > 0:
        for i, tweet in enumerate(results['twitter']['posts'][:10], 1):
            md += f"\n**{i}. @{tweet.get('username', 'unknown')}**\n"
            md += f"- {tweet.get('text', '')[:200]}...\n"
            md += f"- ❤️{tweet.get('likes', 0)} 🔁{tweet.get('retweets', 0)} 💬{tweet.get('replies', 0)}\n"
            md += f"- {tweet.get('url', '')}\n"
    else:
        md += "\n_No Twitter updates found_\n"
    
    md += "\n---\n\n## 🎥 YouTube AI Videos\n"
    
    if results['youtube']['count'] > 0:
        for i, video in enumerate(results['youtube']['videos'][:10], 1):
            md += f"\n**{i}. {video.get('title', 'Untitled')}**\n"
            md += f"- Channel: {video.get('channel_name', 'unknown')}\n"
            md += f"- {video.get('url', '')}\n"
    else:
        md += "\n_No YouTube videos found_\n"
    
    md += "\n---\n\n## 🤖 Moltbook Agent Builds\n"
    
    if results['moltbook']['count'] > 0:
        for i, post in enumerate(results['moltbook']['posts'][:10], 1):
            md += f"\n**{i}. {post.get('title', 'Untitled')}**\n"
            md += f"- @{post.get('author', 'unknown')} • Score: {post.get('score', 0)}\n"
            md += f"- {post.get('url', '')}\n"
    else:
        md += "\n_No Moltbook posts found_\n"
    
    md += "\n---\n\n## 🟢 Health & Wellness\n"
    
    if results['health']['count'] > 0:
        for i, post in enumerate(results['health']['posts'][:10], 1):
            md += f"\n**{i}. {post.get('title', 'Untitled')}**\n"
            md += f"- Source: {post.get('source', 'unknown')}\n"
            md += f"- {post.get('url', '')}\n"
    else:
        md += "\n_No health posts found_\n"
    
    md += "\n---\n\n## 📰 RSS News Feed\n"
    
    if results['rss']['count'] > 0:
        for i, article in enumerate(results['rss']['articles'][:15], 1):
            md += f"\n**{i}. {article.get('title', 'Untitled')}**\n"
            md += f"- {article.get('source', 'unknown')} • {article.get('category', '')}\n"
            md += f"- {article.get('url', '')}\n"
    else:
        md += "\n_No RSS articles found_\n"
    
    md += f"\n---\n\n_Generated by Bishop • Last updated: {timestamp}_\n"
    
    return md

if __name__ == "__main__":
    run_full_digest()

    # Create Daily folder structure
    print("\n📁 Creating Daily folder structure...")
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%I%p').lstrip('0')  # "6AM" or "5PM"
    daily_folder = f'Daily/{date_str}-{time_str}'
    
    os.makedirs(daily_folder, exist_ok=True)
    
    # Copy complete database files to Daily folder
    if os.path.exists(f'Database/all_items_{date_str}.html'):
        shutil.copy(f'Database/all_items_{date_str}.html', f'{daily_folder}/all_items.html')
        print(f"✅ Copied complete database: {daily_folder}/all_items.html")
    
    if os.path.exists(f'Database/complete_{date_str}.json'):
        shutil.copy(f'Database/complete_{date_str}.json', f'{daily_folder}/complete.json')
        print(f"✅ Copied raw data: {daily_folder}/complete.json")
    
    # Copy the digest
    if os.path.exists('dossier.html'):
        shutil.copy('dossier.html', f'{daily_folder}/digest.html')
        print(f"✅ Copied highlights: {daily_folder}/digest.html")
    
    # Add footer links to main dossier
    print("\n🔗 Adding footer links...")
    subprocess.run(['python3', 'add_footer_links.py'], check=True)
    
    print(f"\n✅ Daily folder complete: {daily_folder}/")

# After generating digest, create database with summaries
print("\n📊 Creating database with summaries...")
date_str = datetime.now().strftime('%Y-%m-%d_%H%M')
subprocess.run(['python3', 'complete_with_titles.py'], timeout=180)
print(f"✅ Database created: Database/complete_with_titles.html")
