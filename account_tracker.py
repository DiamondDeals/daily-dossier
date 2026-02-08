#!/usr/bin/env python3
"""
Track all accounts encountered across platforms
Learn which accounts consistently produce good content
"""

import json
from datetime import datetime
from collections import defaultdict
import os

ACCOUNTS_FILE = 'Database/account_tracker.json'

def load_accounts():
    """Load account tracking database"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return {
        'reddit': {},
        'twitter': {},
        'moltbook': {},
        'youtube': {},
        'last_updated': None
    }

def track_account(platform, username, item_data):
    """Track an account appearance with engagement data"""
    accounts = load_accounts()
    
    if platform not in accounts:
        accounts[platform] = {}
    
    if username not in accounts[platform]:
        accounts[platform][username] = {
            'first_seen': datetime.now().isoformat(),
            'appearances': 0,
            'total_engagement': 0,
            'avg_engagement': 0,
            'best_post': None,
            'posts': []
        }
    
    account = accounts[platform][username]
    account['appearances'] += 1
    account['last_seen'] = datetime.now().isoformat()
    
    # Calculate engagement
    engagement = 0
    if 'upvotes' in item_data:
        engagement += item_data['upvotes']
    if 'comments' in item_data:
        engagement += item_data['comments']
    if 'score' in item_data:
        engagement += item_data['score']
    
    account['total_engagement'] += engagement
    account['avg_engagement'] = account['total_engagement'] / account['appearances']
    
    # Track best post
    if account['best_post'] is None or engagement > account['best_post'].get('engagement', 0):
        account['best_post'] = {
            'title': item_data.get('title', 'Untitled'),
            'url': item_data.get('url', ''),
            'engagement': engagement,
            'date': datetime.now().isoformat()
        }
    
    # Add to posts list (keep last 10)
    account['posts'].append({
        'title': item_data.get('title', 'Untitled'),
        'url': item_data.get('url', ''),
        'engagement': engagement,
        'date': datetime.now().isoformat()
    })
    account['posts'] = account['posts'][-10:]  # Keep only last 10
    
    accounts['last_updated'] = datetime.now().isoformat()
    
    # Save
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)
    
    return accounts

def generate_top_accounts_page():
    """Generate HTML page showing top accounts to follow"""
    accounts = load_accounts()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Accounts to Follow - Daily Dossier</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1d1d1f;
            color: #f5f5f7;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
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
        .platform-section {{
            margin: 40px 0;
            padding: 30px;
            background: #1d1d1f;
            border-radius: 12px;
            border-left: 4px solid #0a84ff;
        }}
        .platform-section h2 {{
            color: #0a84ff;
            font-size: 28px;
            margin-bottom: 20px;
        }}
        .account-card {{
            background: #2d2d2f;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 3px solid #30d158;
        }}
        .account-name {{
            color: #0a84ff;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .account-stats {{
            display: flex;
            gap: 20px;
            margin: 10px 0;
            flex-wrap: wrap;
        }}
        .stat {{
            color: #a1a1a6;
            font-size: 14px;
        }}
        .stat-value {{
            color: #30d158;
            font-weight: 700;
        }}
        .best-post {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #424245;
        }}
        .best-post-title {{
            color: #f5f5f7;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        a {{
            color: #0a84ff;
            text-decoration: none;
            word-break: break-all;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Top Accounts to Follow</h1>
        <p style="color: #a1a1a6; font-size: 18px;">Ranked by consistent quality content</p>
        <p style="color: #a1a1a6; font-size: 14px; margin-top: 5px;">Last updated: {str(accounts.get('last_updated', 'Never'))[:10]}</p>
"""
    
    platform_names = {
        'reddit': '🟠 Reddit Users',
        'twitter': '🔵 Twitter Accounts',
        'moltbook': '🤖 Moltbook Agents',
        'youtube': '🎥 YouTube Channels'
    }
    
    for platform, name in platform_names.items():
        if platform in accounts and accounts[platform]:
            # Sort by avg engagement
            sorted_accounts = sorted(
                accounts[platform].items(),
                key=lambda x: x[1].get('avg_engagement', 0),
                reverse=True
            )[:20]  # Top 20
            
            html += f'<div class="platform-section"><h2>{name}</h2>'
            
            for username, data in sorted_accounts:
                html += f'''
                <div class="account-card">
                    <div class="account-name">@{username}</div>
                    <div class="account-stats">
                        <div class="stat">Appearances: <span class="stat-value">{data['appearances']}</span></div>
                        <div class="stat">Avg Engagement: <span class="stat-value">{int(data['avg_engagement'])}</span></div>
                        <div class="stat">Total: <span class="stat-value">{data['total_engagement']}</span></div>
                    </div>
'''
                
                if data.get('best_post'):
                    best = data['best_post']
                    html += f'''
                    <div class="best-post">
                        <div class="best-post-title">🏆 Best Post ({best['engagement']} engagement):</div>
                        <div style="color: #a1a1a6; font-size: 14px; margin-top: 5px;">{best['title']}</div>
                        <a href="{best['url']}" target="_blank" style="font-size: 13px;">{best['url']}</a>
                    </div>
'''
                
                html += '</div>'
            
            html += '</div>'
    
    html += '''
        <div style="margin-top: 40px; text-align: center;">
            <p style="color: #a1a1a6;">
                <a href="dossier.html">← Back to Main Dossier</a> | 
                <a href="stats.html">View Statistics</a>
            </p>
        </div>
    </div>
</body>
</html>'''
    
    with open('top_accounts.html', 'w') as f:
        f.write(html)
    
    print(f"✅ Generated top_accounts.html")
    return 'top_accounts.html'

if __name__ == '__main__':
    print("✅ Account tracker system created")
    # Test generation
    generate_top_accounts_page()
