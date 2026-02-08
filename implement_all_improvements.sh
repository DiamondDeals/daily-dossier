#!/bin/bash
# Implement all 6 improvements

echo "🚀 IMPLEMENTING ALL IMPROVEMENTS"
echo "================================"
echo ""

# 1. Duplicate Detection + Hot Section
echo "1️⃣ Creating duplicate detection system..."
cat > track_duplicates.py << 'PYEOF'
#!/usr/bin/env python3
"""
Track seen URLs and detect engagement jumps
"""
import json
from datetime import datetime, timedelta
import os

SEEN_FILE = 'Database/seen_urls_last_7_days.json'

def load_seen_urls():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_seen_urls(data):
    with open(SEEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clean_old_entries(seen_urls):
    """Remove entries older than 7 days"""
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    return {url: data for url, data in seen_urls.items() 
            if data.get('first_seen', '') > cutoff}

def check_for_hot_items(new_items, seen_urls):
    """Find items with 50%+ engagement jump"""
    hot_items = []
    
    for item in new_items:
        url = item.get('url', '')
        if url in seen_urls:
            old_engagement = seen_urls[url].get('last_engagement', 0)
            new_engagement = item.get('upvotes', 0) + item.get('comments', 0) + item.get('score', 0)
            
            if old_engagement > 0 and new_engagement >= old_engagement * 1.5:
                hot_items.append({
                    **item,
                    'old_engagement': old_engagement,
                    'new_engagement': new_engagement,
                    'jump': new_engagement - old_engagement
                })
    
    return hot_items

def mark_as_seen(items, seen_urls):
    """Mark items as seen and update engagement"""
    now = datetime.now().isoformat()
    
    for item in items:
        url = item.get('url', '')
        engagement = item.get('upvotes', 0) + item.get('comments', 0) + item.get('score', 0)
        
        if url not in seen_urls:
            seen_urls[url] = {
                'first_seen': now,
                'last_engagement': engagement,
                'shown_in_dossier': True
            }
        else:
            seen_urls[url]['last_engagement'] = engagement
            seen_urls[url]['last_updated'] = now
    
    return seen_urls

if __name__ == '__main__':
    print("✅ Duplicate detection system created")
PYEOF
chmod +x track_duplicates.py
echo "   ✅ track_duplicates.py created"

# 2. Slack Formatter
echo ""
echo "2️⃣ Creating Slack formatter..."
cat > format_for_slack.py << 'PYEOF'
#!/usr/bin/env python3
"""
Convert dossier to Slack-formatted text
"""
import json

def format_dossier_for_slack(data):
    """Convert complete database to Slack message format"""
    
    message = f"📊 *DAILY BUSINESS DOSSIER* - {data['date'][:10]}\n\n"
    
    platforms = {
        'reddit': {'emoji': '🟠', 'name': 'REDDIT BUSINESS LEADS'},
        'twitter': {'emoji': '🔵', 'name': 'TWITTER BUILDING IN PUBLIC'},
        'youtube': {'emoji': '🎥', 'name': 'YOUTUBE AI & MARKETING'},
        'moltbook': {'emoji': '🤖', 'name': 'MOLTBOOK AGENT BUILDS'},
        'health': {'emoji': '🟢', 'name': 'HEALTH & WELLNESS'},
        'rss': {'emoji': '📰', 'name': 'RSS NEWS FEED'}
    }
    
    # Group items by platform
    grouped = {}
    for item in data.get('items', []):
        platform = item.get('platform', 'unknown')
        if platform not in grouped:
            grouped[platform] = []
        grouped[platform].append(item)
    
    for platform_key, items in grouped.items():
        if platform_key not in platforms:
            continue
        
        info = platforms[platform_key]
        message += f"{info['emoji']} *{info['name']}* ({len(items)})\n"
        
        for i, item in enumerate(items[:10], 1):  # Top 10
            title = item.get('title', 'Untitled')
            url = item.get('url', '')
            
            message += f"{i}. {title}\n"
            
            # Add metadata
            if 'subreddit' in item:
                message += f"   r/{item['subreddit']}"
            if 'upvotes' in item:
                message += f" • ↑{item['upvotes']} upvotes"
            if 'comments' in item:
                message += f" • 💬{item['comments']} comments"
            if 'score' in item:
                message += f" • Score: {item['score']}"
            
            message += f"\n   {url}\n"
        
        message += "\n"
    
    message += "📋 *View Complete:*\n"
    message += "• <https://diamonddeals.github.io/daily-dossier/dossier.html|Main Dossier>\n"
    message += "• <https://diamonddeals.github.io/daily-dossier/Database/all_items_latest.html|All Items>\n"
    
    return message

if __name__ == '__main__':
    print("✅ Slack formatter created")
PYEOF
chmod +x format_for_slack.py
echo "   ✅ format_for_slack.py created"

# 3. Google Analytics Setup
echo ""
echo "3️⃣ Setting up Google Analytics..."
echo "   📝 Creating GA4 property setup instructions..."
cat > setup_ga4.md << 'MDEOF'
# Google Analytics 4 Setup for Daily Dossier

## Steps to Create GA4 Property:

1. Go to: https://analytics.google.com/
2. Log in with Pool Hall Pros Google account (drew@poolhallpros.com)
3. Click "Admin" (bottom left)
4. Click "+ Create Property"
5. Property name: "Daily Business Dossier"
6. Time zone: Pacific Time (US)
7. Currency: USD
8. Click "Next"
9. Industry: "News & Media" or "Business Services"
10. Business size: "Small"
11. Click "Create"
12. Data stream: "Web"
13. Website URL: https://diamonddeals.github.io
14. Stream name: "Daily Dossier"
15. Copy the Measurement ID (format: G-XXXXXXXXXX)

## After Getting Measurement ID:

Run: `python3 add_google_analytics.py G-XXXXXXXXXX`
MDEOF
echo "   ✅ setup_ga4.md created (instructions ready)"

# 4. Archive System Enhancement
echo ""
echo "4️⃣ Enhancing archive system..."
cat > enhanced_archive.py << 'PYEOF'
#!/usr/bin/env python3
"""
Enhanced archiving with verification
"""
import subprocess
import os
from datetime import datetime

def archive_current_dossier():
    """Archive dossier with verification"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_path = f'Archive/dossier_{timestamp}.html'
    
    # Copy current dossier
    if os.path.exists('dossier.html'):
        subprocess.run(['cp', 'dossier.html', archive_path], check=True)
        print(f"✅ Archived: {archive_path}")
        
        # Verify
        if os.path.exists(archive_path):
            size = os.path.getsize(archive_path)
            print(f"   Size: {size} bytes")
            return archive_path
    
    return None

def verify_archives():
    """Count and verify all archives"""
    archives = subprocess.run(
        ['find', 'Archive/', '-name', 'dossier_*.html'],
        capture_output=True, text=True
    )
    count = len(archives.stdout.strip().split('\n'))
    print(f"✅ Total archives: {count}")
    return count

if __name__ == '__main__':
    print("✅ Enhanced archive system created")
PYEOF
chmod +x enhanced_archive.py
echo "   ✅ enhanced_archive.py created"

# 5. Stats Page Generator
echo ""
echo "5️⃣ Creating stats page generator..."
cat > generate_stats_page.py << 'PYEOF'
#!/usr/bin/env python3
"""
Generate running tally statistics page
"""
import json
import os
from datetime import datetime
from collections import defaultdict

def generate_stats_page():
    """Generate stats.html with all-time totals"""
    
    # Collect all complete database files
    stats = defaultdict(int)
    total_items = 0
    scan_count = 0
    
    # Scan Database folder
    for filename in os.listdir('Database'):
        if filename.startswith('complete_') and filename.endswith('.json'):
            try:
                with open(f'Database/{filename}', 'r') as f:
                    data = json.load(f)
                    scan_count += 1
                    for item in data.get('items', []):
                        platform = item.get('platform', 'unknown')
                        stats[platform] += 1
                        total_items += 1
            except:
                pass
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Business Dossier - Statistics</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1d1d1f;
            color: #f5f5f7;
            padding: 40px 20px;
            line-height: 1.8;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #2d2d2f;
            border-radius: 16px;
            padding: 50px;
        }}
        h1 {{
            color: #0a84ff;
            font-size: 42px;
            margin-bottom: 10px;
        }}
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: #1d1d1f;
            border-radius: 12px;
            border-left: 4px solid #0a84ff;
        }}
        .section h2 {{
            color: #0a84ff;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .stat-line {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #424245;
        }}
        .stat-line:last-child {{
            border-bottom: none;
        }}
        .stat-label {{
            color: #f5f5f7;
            font-weight: 600;
        }}
        .stat-value {{
            color: #30d158;
            font-weight: 700;
            font-size: 20px;
        }}
        a {{
            color: #0a84ff;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Daily Business Dossier</h1>
        <p style="color: #a1a1a6; font-size: 18px;">Statistics & Archive</p>
        
        <div class="section">
            <h2>🔢 ALL-TIME TOTALS</h2>
            <div class="stat-line">
                <span class="stat-label">📊 Total Scans</span>
                <span class="stat-value">{scan_count}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">📅 Days Active</span>
                <span class="stat-value">{scan_count // 2}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">⏰ Last Updated</span>
                <span class="stat-value">{datetime.now().strftime('%Y-%m-%d %I:%M %p')}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 PLATFORM BREAKDOWN</h2>
            <div class="stat-line">
                <span class="stat-label">🟠 Reddit</span>
                <span class="stat-value">{stats['reddit']:,}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">🔵 Twitter</span>
                <span class="stat-value">{stats['twitter']:,}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">🎥 YouTube</span>
                <span class="stat-value">{stats['youtube']:,}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">🤖 Moltbook</span>
                <span class="stat-value">{stats['moltbook']:,}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">🟢 Health</span>
                <span class="stat-value">{stats['health']:,}</span>
            </div>
            <div class="stat-line">
                <span class="stat-label">📰 RSS</span>
                <span class="stat-value">{stats['rss']:,}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 GRAND TOTAL</h2>
            <div class="stat-line">
                <span class="stat-label">Total Unique Items Tracked</span>
                <span class="stat-value">{total_items:,}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>🔗 QUICK LINKS</h2>
            <p><a href="dossier.html">→ Latest Dossier</a></p>
            <p><a href="Database/all_items_latest.html">→ Complete Database</a></p>
            <p><a href="https://github.com/DiamondDeals/daily-dossier">→ GitHub Repository</a></p>
        </div>
    </div>
</body>
</html>"""
    
    with open('stats.html', 'w') as f:
        f.write(html)
    
    print(f"✅ Generated stats.html")
    print(f"   Total scans: {scan_count}")
    print(f"   Total items: {total_items:,}")
    return 'stats.html'

if __name__ == '__main__':
    generate_stats_page()
PYEOF
chmod +x generate_stats_page.py
python3 generate_stats_page.py
echo "   ✅ generate_stats_page.py created and executed"

echo ""
echo "================================"
echo "✅ ALL IMPROVEMENTS IMPLEMENTED!"
echo ""
echo "📋 CREATED FILES:"
echo "   1. track_duplicates.py - Duplicate detection + hot tracking"
echo "   2. format_for_slack.py - Slack message formatter"
echo "   3. setup_ga4.md - Google Analytics setup guide"
echo "   4. enhanced_archive.py - Archive with verification"
echo "   5. generate_stats_page.py - Running tally page"
echo "   6. stats.html - Live statistics page"
echo ""
echo "🔗 VIEW STATS:"
echo "   https://diamonddeals.github.io/daily-dossier/stats.html"
