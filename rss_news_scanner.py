#!/usr/bin/env python3
"""
RSS News Feed Scanner
Monitors news feeds for AI, Marketing, Health content
"""

import feedparser
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

class RSSNewsScanner:
    def __init__(self):
        self.feeds_file = "rss_news_feeds.json"
        self.load_feeds()
        
    def load_feeds(self):
        """Load RSS feeds from JSON file"""
        if os.path.exists(self.feeds_file):
            with open(self.feeds_file, 'r') as f:
                self.feeds = json.load(f)
        else:
            self.feeds = {"ai_news": [], "marketing": [], "health": []}
    
    def fetch_feed(self, feed_url: str, hours_back: int = 24) -> List[Dict]:
        """Fetch articles from an RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            articles = []
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                # Parse published date
                try:
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed'):
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                except:
                    pub_date = datetime.now()
                
                if pub_date > cutoff_time:
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else 'Untitled',
                        'url': entry.link if hasattr(entry, 'link') else '',
                        'published': pub_date.isoformat(),
                        'summary': entry.summary if hasattr(entry, 'summary') else ''
                    }
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error fetching {feed_url}: {str(e)}")
            return []
    
    def scan_all_feeds(self, hours_back: int = 24) -> Dict[str, List[Dict]]:
        """Scan all configured feeds"""
        results = {}
        
        print(f"📰 Scanning RSS news feeds...")
        
        for category, feeds in self.feeds.items():
            print(f"\n  Category: {category}")
            category_articles = []
            
            for feed in feeds:
                print(f"    Checking {feed['name']}...")
                articles = self.fetch_feed(feed['url'], hours_back)
                
                for article in articles:
                    article['source'] = feed['name']
                    article['category'] = feed['category']
                    category_articles.append(article)
                
                print(f"      Found {len(articles)} article(s)")
            
            results[category] = category_articles
        
        return results
    
    def format_digest(self, results: Dict[str, List[Dict]]) -> str:
        """Format results into digest format"""
        all_articles = []
        for articles in results.values():
            all_articles.extend(articles)
        
        if not all_articles:
            return "No new articles found in the last 24 hours."
        
        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x['published'], reverse=True)
        
        digest = f"# 📰 RSS News Digest ({len(all_articles)} articles)\n\n"
        
        # Group by category
        categories = {}
        for article in all_articles:
            cat = article['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        for category, articles in sorted(categories.items()):
            digest += f"\n## {category} ({len(articles)})\n\n"
            
            for article in articles[:10]:  # Top 10 per category
                pub_date = datetime.fromisoformat(article['published'])
                hours_ago = int((datetime.now() - pub_date).total_seconds() / 3600)
                
                digest += f"**{article['title']}**\n"
                digest += f"- Source: {article['source']}\n"
                digest += f"- Published: {hours_ago}h ago\n"
                digest += f"- Link: {article['url']}\n\n"
        
        return digest

def main():
    scanner = RSSNewsScanner()
    results = scanner.scan_all_feeds(hours_back=24)
    digest = scanner.format_digest(results)
    
    print("\n" + "="*80)
    print(digest)
    print("="*80)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Exports/rss_news_{timestamp}.md"
    os.makedirs("Exports", exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(digest)
    
    print(f"\n✅ Digest saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
