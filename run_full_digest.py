#!/usr/bin/env python3
"""
Full Digest Runner - All 6 Platforms
No subprocess issues - direct imports and execution
"""

import sys
import os
import shutil
import subprocess
import json
import io
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Handle encoding for Task Scheduler (no console attached)
# Force UTF-8 to avoid emoji encoding errors
if hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except:
        pass  # If it fails, continue anyway

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / '.env')

# Import all scanners
from reddit_json_client import RedditJSONClient
from bluesky_scanner import BlueskyScanner
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
    
    # 1. Reddit - Business pain points, AI, tech, cybersecurity, opportunities
    print("🟠 REDDIT - Pain Points, AI, Business & Opportunities")
    try:
        reddit = RedditJSONClient()
        subreddits = [
            # Core Business & Pain Points (from Reddit Helper Helper project)
            'entrepreneur', 'smallbusiness', 'startups', 'ecommerce',
            'freelance', 'solopreneur', 'SideProject', 'passive_income',
            'SmallBusinessOwners', 'sweatystartup',
            # Marketing & Sales (Drew's expertise)
            'digitalmarketing', 'SEO', 'marketing', 'sales',
            'digital_marketing', 'MarketingHelp', 'agency', 'growth',
            # Pain Point Discovery
            'SomebodyMakeThis', 'AppIdeas', 'automation',
            'productivity', 'workflow', 'excel',
            # AI & Tech
            'artificial', 'LocalLLaMA', 'ChatGPT', 'ClaudeAI',
            'MachineLearning', 'singularity',
            # Cybersecurity (Drew's interest)
            'netsec', 'cybersecurity', 'hacking',
            # Business Operations
            'consulting', 'SaaS', 'projectmanagement',
            'Bookkeeping', 'customerservice',
            # Industry Opportunities
            'realestate', 'restaurantowners', 'msp',
        ]
        reddit_posts = []
        for sub in subreddits:
            try:
                posts = reddit.fetch_posts(sub, limit=15)
                reddit_posts.extend(posts)
            except Exception:
                pass
        results['reddit'] = {'count': len(reddit_posts), 'posts': reddit_posts}
        print(f"✅ Found {len(reddit_posts)} Reddit leads\n")
    except Exception as e:
        print(f"❌ Reddit failed: {e}\n")
        results['reddit'] = {'count': 0, 'posts': []}

    # 2. Bluesky - Building in Public (replaces dead Twitter/Nitter)
    print("🦋 BLUESKY - Building in Public")
    try:
        bluesky = BlueskyScanner()
        bluesky_updates = bluesky.scan_builders(max_accounts=20)
        results['twitter'] = {'count': len(bluesky_updates), 'posts': bluesky_updates}
        print(f"✅ Found {len(bluesky_updates)} Bluesky builder updates\n")
    except Exception as e:
        print(f"❌ Bluesky failed: {e}\n")
        results['twitter'] = {'count': 0, 'posts': []}
    
    # 3. YouTube
    print("🎥 YOUTUBE - AI Videos")
    try:
        youtube = YouTubeAIMonitor()
        youtube_videos = youtube.scan_all_channels()
        # Flatten with max 2 per channel so no one dominates
        all_videos = youtube.cap_per_channel(youtube_videos, max_per_channel=2)
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
    
    # 5. Health (Reddit + RSS, no Twitter API needed)
    print("🟢 HEALTH - Pritikin, Heart Health & WFPB")
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
        rss_articles = rss.scan_all_feeds(hours_back=48)
        # Flatten with max 3 per source so no one dominates
        all_articles = rss.cap_per_source(rss_articles, max_per_source=3)
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
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"✅ Saved markdown to: {md_file}\n")

    # Save dated database files for Daily folder archiving
    date_str = datetime.now().strftime('%Y-%m-%d')
    os.makedirs("Database", exist_ok=True)

    # Save complete JSON database
    database = {
        'date': datetime.now().isoformat(),
        'total_count': total,
        'results': results
    }
    json_file = f'Database/complete_{date_str}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved database JSON: {json_file}")

    # Save all_items HTML database
    html_file = f'Database/all_items_{date_str}.html'
    all_items_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Complete Database - {date_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #1d1d1f; color: #f5f5f7; padding: 20px; max-width: 980px; margin: 0 auto; }}
        h1 {{ color: #0a84ff; }}
        h2 {{ color: #0a84ff; margin-top: 40px; }}
        .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .count {{ color: #30d158; font-size: 20px; font-weight: bold; }}
        .item {{ margin: 12px 0; padding: 15px; background: #2d2d2f; border-radius: 8px;
                 display: flex; align-items: flex-start; gap: 12px; }}
        .item-content {{ flex: 1; }}
        .platform {{ display: inline-block; padding: 4px 8px; border-radius: 4px;
                     font-size: 12px; font-weight: bold; margin-right: 10px; }}
        .reddit {{ background: #ff4500; }}
        .twitter {{ background: #0085ff; }}
        .youtube {{ background: #ff0000; }}
        .moltbook {{ background: #8b5cf6; }}
        .health {{ background: #10b981; }}
        .rss {{ background: #f59e0b; }}
        a {{ color: #0a84ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .bm {{ cursor: pointer; font-size: 20px; opacity: 0.5; border: none;
               background: none; color: #ffd60a; padding: 4px; flex-shrink: 0; }}
        .bm:hover {{ opacity: 1; }}
        .bm.saved {{ opacity: 1; color: #ffd60a; }}
        .back-link {{ color: #0a84ff; font-size: 15px; }}
        .saved-toggle {{ background: #2d2d2f; border: 1px solid #424245; border-radius: 20px;
                         padding: 8px 16px; color: #f5f5f7; cursor: pointer; font-size: 14px; }}
        .saved-toggle:hover {{ background: #0a84ff; color: white; }}
        .saved-panel {{ display: none; position: fixed; top: 0; right: 0; width: 420px;
                        height: 100vh; background: #2d2d2f; border-left: 1px solid #424245;
                        z-index: 2000; overflow-y: auto; padding: 24px;
                        box-shadow: -4px 0 20px rgba(0,0,0,0.5); }}
        .saved-panel.open {{ display: block; }}
        .saved-panel h2 {{ font-size: 22px; margin: 0 0 16px 0; }}
        .close-btn {{ position: absolute; top: 20px; right: 20px; background: none;
                      border: none; color: #a1a1a6; font-size: 24px; cursor: pointer; }}
        .si {{ padding: 12px 0; border-bottom: 1px solid #424245; }}
        .si a {{ font-weight: 600; font-size: 15px; display: block; margin-bottom: 4px; }}
        .si .meta {{ font-size: 12px; color: #a1a1a6; }}
        .si .rm {{ cursor: pointer; color: #a1a1a6; font-size: 12px; border: none;
                   background: none; padding: 2px 6px; margin-top: 4px; }}
        .si .rm:hover {{ color: #ff453a; }}
        .filter-bar {{ margin: 20px 0; display: flex; gap: 8px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 6px 14px; border-radius: 16px; border: 1px solid #424245;
                       background: none; color: #a1a1a6; cursor: pointer; font-size: 13px; }}
        .filter-btn:hover, .filter-btn.active {{ background: #0a84ff; color: white; border-color: #0a84ff; }}
        .scroll-top {{ position: fixed; bottom: 30px; right: 30px; width: 48px; height: 48px;
                       border-radius: 50%; background: #0a84ff; color: white; border: none;
                       font-size: 22px; cursor: pointer; z-index: 1000; opacity: 0;
                       pointer-events: none; transition: opacity 0.3s ease;
                       box-shadow: 0 2px 10px rgba(0,0,0,0.4); }}
        .scroll-top.visible {{ opacity: 1; pointer-events: auto; }}
        .scroll-top:hover {{ transform: scale(1.1); }}
    </style>
</head>
<body>
    <div class="top-bar">
        <a class="back-link" href="../dossier.html">&larr; Back to Dossier</a>
        <button class="saved-toggle" onclick="togglePanel()">Saved (0)</button>
    </div>
    <button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&uarr;</button>
    <h1>Complete Database - {date_str}</h1>
    <p class="count">Total Items: {total}</p>

    <div class="filter-bar">
        <button class="filter-btn active" onclick="filterPlatform('all', this)">All</button>
        <button class="filter-btn" onclick="filterPlatform('reddit', this)">Reddit</button>
        <button class="filter-btn" onclick="filterPlatform('twitter', this)">Bluesky</button>
        <button class="filter-btn" onclick="filterPlatform('youtube', this)">YouTube</button>
        <button class="filter-btn" onclick="filterPlatform('moltbook', this)">Moltbook</button>
        <button class="filter-btn" onclick="filterPlatform('health', this)">Health</button>
        <button class="filter-btn" onclick="filterPlatform('rss', this)">RSS</button>
    </div>

    <div class="saved-panel" id="sp">
        <button class="close-btn" onclick="togglePanel()">&times;</button>
        <h2>Saved Items</h2>
        <div id="sl"></div>
    </div>
"""

    # Add all items by platform
    for platform_name, platform_data in [
        ('reddit', '🟠 Reddit'), ('twitter', '🦋 Bluesky'), ('youtube', '🎥 YouTube'),
        ('moltbook', '🤖 Moltbook'), ('health', '🟢 Health'), ('rss', '📰 RSS')
    ]:
        count = results[platform_name]['count']
        all_items_html += f"\n<h2>{platform_data} ({count} items)</h2>\n"

        if count > 0:
            items = results[platform_name].get('posts', results[platform_name].get('videos', results[platform_name].get('articles', [])))
            for item in items:
                title = item.get('title', 'Untitled').replace('"', '&quot;').replace("'", "&#39;")
                url = item.get('url', '#')
                all_items_html += f'<div class="item" data-platform="{platform_name}"><button class="bm" data-title="{title}" data-url="{url}" data-section="{platform_data}" onclick="tbm(this)">&#9734;</button><div class="item-content"><span class="platform {platform_name}">{platform_data}</span><strong>{title}</strong><br><a href="{url}" target="_blank">{url}</a></div></div>\n'
        else:
            all_items_html += "<p>No items found</p>\n"

    all_items_html += """
<script>
function gBm(){try{return JSON.parse(localStorage.getItem('dossier_bookmarks')||'[]')}catch{return[]}}
function sBm(b){localStorage.setItem('dossier_bookmarks',JSON.stringify(b));uBadge()}
function uBadge(){document.querySelector('.saved-toggle').textContent='Saved ('+gBm().length+')'}
function togglePanel(){var p=document.getElementById('sp');p.classList.toggle('open');if(p.classList.contains('open'))rList()}
function rList(){var l=document.getElementById('sl'),b=gBm();
if(!b.length){l.innerHTML='<p style="color:#a1a1a6;font-style:italic">No saved items yet.</p>';return}
l.innerHTML=b.map((m,i)=>'<div class="si"><a href="'+m.url+'" target="_blank">'+m.title+'</a><span class="meta">'+
(m.section||'')+' &middot; '+( m.date||'')+'</span><br><button class="rm" onclick="rbm('+i+')">&times; Remove</button></div>').join('')}
function rbm(i){var b=gBm();b.splice(i,1);sBm(b);rList();syncBtns()}
function tbm(btn){var t=btn.getAttribute('data-title'),u=btn.getAttribute('data-url'),
s=btn.getAttribute('data-section'),b=gBm(),x=b.findIndex(m=>m.title===t);
if(x>=0){b.splice(x,1);btn.classList.remove('saved');btn.innerHTML='&#9734;'}
else{b.push({title:t,url:u,section:s,date:new Date().toLocaleDateString()});btn.classList.add('saved');btn.innerHTML='&#9733;'}
sBm(b)}
function syncBtns(){var b=gBm();document.querySelectorAll('.bm').forEach(btn=>{
var t=btn.getAttribute('data-title'),s=b.some(m=>m.title===t);
btn.classList.toggle('saved',s);btn.innerHTML=s?'&#9733;':'&#9734;'})}
function filterPlatform(p,btn){document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
btn.classList.add('active');document.querySelectorAll('.item').forEach(el=>{
el.style.display=(p==='all'||el.getAttribute('data-platform')===p)?'flex':'none'})}
window.addEventListener('scroll',function(){document.getElementById('scrollTop').classList.toggle('visible',window.scrollY>400)});
document.addEventListener('DOMContentLoaded',function(){uBadge();syncBtns()});
</script>
</body></html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(all_items_html)
    print(f"✅ Saved all items HTML: {html_file}\n")
    
    # Generate HTML
    print("🌐 Generating HTML...")
    html_gen = DigestHTMLGenerator()
    
    # Archive old version
    html_gen.archive_current_html()
    
    # Convert to HTML
    html = html_gen.markdown_to_html(markdown, "Daily Business Dossier")
    html_gen.save_html(html)

    print(f"\n✅ Digest generated! (deployment happens after post-processing)")

    return results, html_gen

def generate_combined_markdown(results):
    """Generate combined markdown digest"""
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p PST")
    total = sum(r['count'] for r in results.values())

    # NOTE: Title and date are in HTML template, don't duplicate in markdown body
    date_str_db = datetime.now().strftime('%Y-%m-%d')
    md = f"""**Total Opportunities: {total}**

<div style="background: var(--bg-secondary); border: 2px solid var(--accent); border-radius: 12px; padding: 20px 30px; margin: 20px 0 30px 0; text-align: center;">
<a href="Database/all_items_{date_str_db}.html" style="color: var(--accent); text-decoration: none; font-size: 20px; font-weight: 700;">
VIEW ALL {total} ITEMS &rarr;
</a>
<p style="color: var(--text-secondary); font-size: 14px; margin: 8px 0 0 0;">
The dossier below shows top 10 per section. Click above to see everything.
</p>
</div>

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
    
    md += "\n---\n\n## 🦋 Bluesky Builder Updates\n"

    if results['twitter']['count'] > 0:
        for i, post in enumerate(results['twitter']['posts'][:10], 1):
            name = post.get('display_name', post.get('username', 'unknown'))
            md += f"\n**{i}. {name}** (@{post.get('username', 'unknown')})\n"
            md += f"- {post.get('text', '')[:200]}...\n"
            md += f"- ❤️{post.get('likes', 0)} 🔁{post.get('reposts', 0)} 💬{post.get('replies', 0)}\n"
            md += f"- {post.get('url', '')}\n"
    else:
        md += "\n_No Bluesky updates found_\n"
    
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
    results, html_gen = run_full_digest()

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
    subprocess.run([sys.executable, 'add_footer_links.py'], check=True)

    print(f"\n✅ Daily folder complete: {daily_folder}/")

    # After generating digest, create database with summaries
    print("\n📊 Creating database with summaries...")
    date_str_time = datetime.now().strftime('%Y-%m-%d_%H%M')
    subprocess.run([sys.executable, 'complete_with_titles.py'], timeout=180)
    print(f"✅ Database created: Database/complete_with_titles.html")

    # NOW deploy to GitHub (after ALL post-processing)
    print("\n📤 Deploying to GitHub Pages...")
    url = html_gen.deploy_to_github()

    if url:
        print(f"\n✅ COMPLETE! View at: {url}")
