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
