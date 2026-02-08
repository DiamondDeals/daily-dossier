#!/usr/bin/env python3
"""
Inoreader RSS Feed Scanner
Parses Drew's OPML feed list and aggregates top content
"""
import xml.etree.ElementTree as ET
import feedparser
from datetime import datetime, timedelta
import time

class InoreaderRSSScanner:
    def __init__(self, opml_file):
        self.opml_file = opml_file
        self.feeds = self._parse_opml()
        
        # Priority categories (focus on these)
        self.priority_categories = [
            '💡 Thought Leaders & Influencers',
            '🤖 Artificial Intelligence - 📡 AI News & Research',
            '📰 Tech & Business News - 💼 Business Publications',
            '🛒 E-commerce'
        ]
    
    def _parse_opml(self):
        """Parse OPML file and extract all RSS feeds"""
        tree = ET.parse(self.opml_file)
        root = tree.getroot()
        
        feeds = {}
        
        for outline in root.findall('.//outline[@text]'):
            category = outline.get('text', '')
            
            # Skip Reddit (we handle separately)
            if 'Reddit' in category:
                continue
            
            feeds[category] = []
            
            # Get child feeds
            for feed in outline.findall('outline[@type="rss"]'):
                feeds[category].append({
                    'title': feed.get('title', ''),
                    'url': feed.get('xmlUrl', ''),
                    'site_url': feed.get('htmlUrl', '')
                })
        
        return feeds
    
    def scan_priority_feeds(self, max_feeds_per_category=3, max_articles_per_feed=5):
        """Scan priority categories for latest content"""
        print("=" * 70)
        print("INOREADER RSS SCANNER - PRIORITY FEEDS")
        print(f"{datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}")
        print("=" * 70)
        print()
        
        all_articles = []
        
        for category in self.priority_categories:
            if category not in self.feeds:
                continue
            
            print(f"\n📂 {category}")
            print("-" * 70)
            
            feeds_in_category = self.feeds[category][:max_feeds_per_category]
            
            for feed_info in feeds_in_category:
                print(f"  {feed_info['title']}...", end=" ", flush=True)
                
                try:
                    feed = feedparser.parse(feed_info['url'])
                    
                    if not feed.entries:
                        print("○")
                        continue
                    
                    # Get recent articles (last 24 hours preferred)
                    recent_count = 0
                    for entry in feed.entries[:max_articles_per_feed]:
                        article = self._parse_entry(entry, feed_info, category)
                        if article:
                            all_articles.append(article)
                            recent_count += 1
                    
                    print(f"✅ {recent_count}")
                    
                except Exception as e:
                    print(f"❌ {e}")
                
                time.sleep(0.5)  # Rate limiting
        
        # Sort by recency and relevance
        all_articles.sort(key=lambda x: x['score'], reverse=True)
        
        return all_articles
    
    def _parse_entry(self, entry, feed_info, category):
        """Parse RSS entry into structured article"""
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')[:200]
            
            # Published date
            published = entry.get('published_parsed', None)
            if published:
                pub_date = datetime(*published[:6])
                age_hours = (datetime.now() - pub_date).total_seconds() / 3600
            else:
                age_hours = 999  # Unknown age
            
            # Score by recency and category priority
            score = 100
            
            # Recency bonus
            if age_hours < 24:
                score += 50
            elif age_hours < 72:
                score += 20
            
            # Category priority bonus
            if '💡 Thought Leaders' in category:
                score += 30
            elif '🤖 Artificial Intelligence' in category:
                score += 25
            elif '📰 Tech & Business News' in category:
                score += 20
            
            return {
                'title': title,
                'link': link,
                'summary': summary,
                'source': feed_info['title'],
                'category': category,
                'age_hours': int(age_hours),
                'score': score
            }
            
        except Exception as e:
            return None
    
    def generate_report(self, articles, top_n=15):
        """Generate markdown report of top articles"""
        if not articles:
            return "⚠️ No articles found"
        
        report = []
        report.append("## 📰 Industry News & Insights\n")
        
        # Group by category
        by_category = {}
        for article in articles[:top_n]:
            cat = article['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        for category, articles_in_cat in by_category.items():
            report.append(f"### {category}\n")
            
            for article in articles_in_cat[:5]:  # Max 5 per category
                age = f"{article['age_hours']}h ago" if article['age_hours'] < 999 else "recent"
                
                report.append(f"**{article['title']}**")
                report.append(f"- {article['source']} • {age}")
                if article['summary']:
                    report.append(f"- {article['summary']}...")
                report.append(f"- {article['link']}\n")
        
        report.append(f"\n**Total:** {len(articles)} articles scanned")
        
        return '\n'.join(report)

if __name__ == '__main__':
    opml_file = "/home/drew/.openclaw/workspace/shared/_Otherstuff/OpenClaw/RSS/Inoreader Feeds 20260208.xml"
    
    scanner = InoreaderRSSScanner(opml_file)
    
    print(f"📚 Loaded {sum(len(feeds) for feeds in scanner.feeds.values())} RSS feeds")
    print(f"🎯 Priority categories: {len(scanner.priority_categories)}")
    print()
    
    articles = scanner.scan_priority_feeds(
        max_feeds_per_category=3,
        max_articles_per_feed=5
    )
    
    print("\n" + "=" * 70)
    print(f"✅ FOUND {len(articles)} ARTICLES")
    print("=" * 70)
    
    print("\n" + scanner.generate_report(articles, top_n=15))
    
    print("\n" + "=" * 70)
    print("✅ RSS scan complete!")
    print("=" * 70)
