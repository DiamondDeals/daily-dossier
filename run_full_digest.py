#!/usr/bin/env python3
"""
Full Digest Runner - FIXED VERSION
Runs scanners as subprocesses (not imports) to get properly formatted output
"""

import sys
import os
import shutil
import subprocess
from datetime import datetime
from track_duplicates import filter_markdown

def run_full_digest():
    """Run all platforms and generate complete digest"""
    print("=" * 80)
    print("🚀 RUNNING FULL 7-PLATFORM DIGEST")
    print("=" * 80)
    print()

    # Combined output markdown (no title/timestamp - already in header)
    combined_md = ""

    #  1. Reddit
    print("🟠 REDDIT - Business Pain Points")
    try:
        result = subprocess.run(['python3', 'reddit_json_client.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
        if result.returncode == 0:
            # Parse stdout
            lines = result.stdout.strip().split('\n')
            reddit_section = "\n## 🟠 Reddit Business Leads\n\n"
            for line in lines:
                if any(line.strip().startswith(f"{i}.") for i in range(1, 100)):
                    reddit_section += line + "\n"
                elif line.strip().startswith(('👤', '📍', '📊', '⏰', '🔗')):
                    reddit_section += line + "\n"
                elif line.strip() == "":
                    reddit_section += "\n"
            combined_md += reddit_section
            print(f"✅ Reddit complete\n")
        else:
            combined_md += "\n## 🟠 Reddit Business Leads\n\n_No Reddit leads found_\n\n"
            print(f"❌ Reddit failed\n")
    except Exception as e:
        print(f"❌ Reddit failed: {e}\n")
        combined_md += "\n## 🟠 Reddit Business Leads\n\n_No Reddit leads found_\n\n"

    # 2. Twitter
    print("🔵 TWITTER - Building in Public")
    try:
        result = subprocess.run(['python3', 'twitter_builders_monitor.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            twitter_section = "\n## 🔵 Twitter Building Updates\n\n"
            for line in lines:
                if line.strip().startswith(('**', '👤', '📊', '💬', '🔗', '-')):
                    twitter_section += line + "\n"
                elif line.strip() == "":
                    twitter_section += "\n"
            combined_md += twitter_section
            print(f"✅ Twitter complete\n")
        else:
            combined_md += "\n## 🔵 Twitter Building Updates\n\n_No Twitter updates found_\n\n"
            print(f"❌ Twitter failed\n")
    except Exception as e:
        print(f"❌ Twitter failed: {e}\n")
        combined_md += "\n## 🔵 Twitter Building Updates\n\n_No Twitter updates found_\n\n"

    # 3. YouTube
    print("🎥 YOUTUBE - AI Videos")
    try:
        result = subprocess.run(['python3', 'youtube_ai_monitor.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            youtube_section = "\n## 🎥 YouTube AI Videos\n\n"
            for line in lines:
                if line.strip().startswith(('**', 'Channel:', '🔗', '-', 'https://')):
                    youtube_section += line + "\n"
                elif line.strip() == "":
                    youtube_section += "\n"
            combined_md += youtube_section
            print(f"✅ YouTube complete\n")
        else:
            combined_md += "\n## 🎥 YouTube AI Videos\n\n_No YouTube videos found_\n\n"
            print(f"❌ YouTube failed\n")
    except Exception as e:
        print(f"❌ YouTube failed: {e}\n")
        combined_md += "\n## 🎥 YouTube AI Videos\n\n_No YouTube videos found_\n\n"

    # 4. Moltbook
    print("🤖 MOLTBOOK - AI Agent Ecosystem")
    try:
        result = subprocess.run(['python3', 'moltbook_scanner.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            moltbook_section = "\n## 🤖 Moltbook Agent Builds\n\n"
            for line in lines:
                if line.strip().startswith(('**', '@', '- @', 'Score:', '🔗', '-', 'https://moltbook')):
                    moltbook_section += line + "\n"
                elif line.strip() == "":
                    moltbook_section += "\n"
            combined_md += moltbook_section
            print(f"✅ Moltbook complete\n")
        else:
            combined_md += "\n## 🤖 Moltbook Agent Builds\n\n_No Moltbook posts found_\n\n"
            print(f"❌ Moltbook failed\n")
    except Exception as e:
        print(f"❌ Moltbook failed: {e}\n")
        combined_md += "\n## 🤖 Moltbook Agent Builds\n\n_No Moltbook posts found_\n\n"

    # 5. Health
    print("🟢 HEALTH - Pritikin & WFPB")
    try:
        result = subprocess.run(['python3', 'health_tracker.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            health_section = "\n## 🟢 Health & Wellness\n\n"
            for line in lines:
                if line.strip().startswith(('**', 'Source:', '🔗', '-', 'https://')):
                    health_section += line + "\n"
                elif line.strip() == "":
                    health_section += "\n"
            combined_md += health_section
            print(f"✅ Health complete\n")
        else:
            combined_md += "\n## 🟢 Health & Wellness\n\n_No health posts found_\n\n"
            print(f"❌ Health failed\n")
    except Exception as e:
        print(f"❌ Health failed: {e}\n")
        combined_md += "\n## 🟢 Health & Wellness\n\n_No health posts found_\n\n"

    # 6. RSS News
    print("📰 RSS NEWS - AI, Marketing, Health News")
    try:
        result = subprocess.run(['python3', 'rss_news_scanner.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            rss_section = "\n## 📰 RSS News Feed\n\n"
            for line in lines:
                if line.strip().startswith(('**', '- ', 'Link:', '🔗', 'https://')):
                    rss_section += line + "\n"
                elif line.strip() == "":
                    rss_section += "\n"
            combined_md += rss_section
            print(f"✅ RSS complete\n")
        else:
            combined_md += "\n## 📰 RSS News Feed\n\n_No RSS articles found_\n\n"
            print(f"❌ RSS failed\n")
    except Exception as e:
        print(f"❌ RSS failed: {e}\n")
        combined_md += "\n## 📰 RSS News Feed\n\n_No RSS articles found_\n\n"

    # 7. GitHub Trending
    print("⚫ GITHUB - Trending Repos")
    try:
        result = subprocess.run(['python3', 'github_trending_scanner.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            github_section = "\n## ⚫ GitHub Trending Repos\n\n"
            for line in lines:
                if any(line.strip().startswith(f"{i}.") for i in range(1, 100)):
                    github_section += line + "\n"
                elif line.strip().startswith(('📝', '⭐', '🏷', '🔗')):
                    github_section += line + "\n"
                elif line.strip() == "":
                    github_section += "\n"
            combined_md += github_section
            print(f"✅ GitHub complete\n")
        else:
            combined_md += "\n## ⚫ GitHub Trending Repos\n\n_No GitHub repos found_\n\n"
            print(f"❌ GitHub failed\n")
    except Exception as e:
        print(f"❌ GitHub failed: {e}\n")
        combined_md += "\n## ⚫ GitHub Trending Repos\n\n_No GitHub repos found_\n\n"

    # Filter duplicates from prior runs
    combined_md, filter_stats = filter_markdown(combined_md)

    combined_md += f"\n---\n\n_Generated by Bishop • Last updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}_\n"

    # Save markdown
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_file = f"Exports/full_digest_{timestamp}.md"
    os.makedirs("Exports", exist_ok=True)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(combined_md)
    print(f"✅ Saved markdown to: {md_file}\n")

    # Generate HTML
    print("🌐 Generating HTML...")
    from html_generator import DigestHTMLGenerator
    html_gen = DigestHTMLGenerator()

    # Archive old version
    html_gen.archive_current_html()

    # Convert to HTML
    html = html_gen.markdown_to_html(combined_md, "Daily Business Dossier")
    html_gen.save_html(html)

    # Apply custom formatting BEFORE deploying (engagement metrics, link previews, etc.)
    print("\n🎨 Applying custom formatting...")
    subprocess.run(['python3', 'add_engagement_and_logos.py'], check=True)
    subprocess.run(['python3', 'add_link_previews.py'], check=True)
    subprocess.run(['python3', 'add_screenshot_previews.py'], check=True)

    # Create database with summaries (needed for URL count in nav)
    print("\n📊 Creating database with summaries...")
    subprocess.run(['python3', 'complete_with_titles.py'], timeout=180)
    print(f"✅ Database created: Database/complete_with_titles.html")

    # Add top navigation links (needs database to exist for URL count)
    print("\n🔝 Adding top navigation...")
    subprocess.run(['python3', 'add_top_navigation.py'], check=True)

    # Add footer links to main dossier
    print("\n🔗 Adding footer links...")
    subprocess.run(['python3', 'add_footer_links.py'], check=True)

    # Create Daily folder structure
    print("\n📁 Creating Daily folder structure...")
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%I%p').lstrip('0')  # "6AM" or "5PM"
    daily_folder = f'Daily/{date_str}-{time_str}'

    os.makedirs(daily_folder, exist_ok=True)

    # Copy digest
    if os.path.exists('dossier.html'):
        shutil.copy('dossier.html', f'{daily_folder}/digest.html')
        print(f"✅ Copied highlights: {daily_folder}/digest.html")

    print(f"\n✅ Daily folder complete: {daily_folder}/")

    # NOW deploy to GitHub with all formatting applied
    print("\n📤 Deploying to GitHub Pages...")
    url = html_gen.deploy_to_github()

    if url:
        print(f"\n✅ COMPLETE! View at: {url}")

if __name__ == "__main__":
    run_full_digest()
