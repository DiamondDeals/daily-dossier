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
