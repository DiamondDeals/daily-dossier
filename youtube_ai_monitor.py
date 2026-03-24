#!/usr/bin/env python3
"""
YouTube AI Channel Monitor (RSS-based)
Monitors AI-focused YouTube channels for new content
"""

import feedparser
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import re

class YouTubeAIMonitor:
    def __init__(self):
        self.channels_file = "youtube_ai_channels.json"
        self.load_channels()
        
    def load_channels(self):
        """Load monitored channels from JSON file"""
        if os.path.exists(self.channels_file):
            with open(self.channels_file, 'r') as f:
                self.channels = json.load(f)
        else:
            # Default AI-focused channels
            self.channels = [
                {
                    "name": "Matt Wolfe",
                    "channel_id": "UCbX3Ud3T0czfS7FTu90EbJg",
                    "category": "AI News & Tools"
                },
                {
                    "name": "AI Jason",
                    "channel_id": "UC1-Hdic6V7Jc7M8hBOKK-Mg",
                    "category": "AI Business"
                },
                {
                    "name": "Wes Roth",
                    "channel_id": "UCnFEGGGu5w_z1AEDCRmqYBw",
                    "category": "AI News"
                },
                {
                    "name": "Matt Berman",
                    "channel_id": "UCbhJVU6SzQQ4cLhJXhG8Ywg",
                    "category": "AI Coding"
                },
                {
                    "name": "AI Explained",
                    "channel_id": "UCNJ1Ymd5yFuUPtn21xtRbbw",
                    "category": "Technical Deep Dives"
                },
                {
                    "name": "Fireship",
                    "channel_id": "UCsBjURrPoezykLs9EqgamOA",
                    "category": "Tech & AI"
                },
                {
                    "name": "Theo - t3.gg",
                    "channel_id": "UCF1hKZhGVl8xsJpWlIvJkjQ",
                    "category": "Coding & AI"
                },
                {
                    "name": "David Ondrej",
                    "channel_id": "UCCGPPOh6xI7Yq8BEIefDODQ",
                    "category": "AI Business"
                },
                {
                    "name": "Cole Medin",
                    "channel_id": "UCchvKtRjL2HVWDfFD5_3FnA",
                    "category": "AI Tools"
                },
                {
                    "name": "AI Advantage",
                    "channel_id": "UCx6nQDILk9bEn8jH4Z-K9Xg",
                    "category": "AI Tools"
                }
            ]
            self.save_channels()
    
    def save_channels(self):
        """Save channels to JSON file"""
        with open(self.channels_file, 'w') as f:
            json.dump(self.channels, f, indent=2)
    
    def fetch_channel_videos(self, channel_id: str, hours_back: int = 48) -> List[Dict]:
        """Fetch recent videos from a YouTube channel via RSS"""
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        try:
            feed = feedparser.parse(rss_url)
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            videos = []
            for entry in feed.entries:
                # Parse published date
                pub_date = datetime(*entry.published_parsed[:6])
                
                if pub_date > cutoff_time:
                    # Extract video data
                    video = {
                        'title': entry.title,
                        'url': entry.link,
                        'published': pub_date.isoformat(),
                        'author': entry.author,
                        'video_id': entry.yt_videoid,
                        'description': entry.summary if hasattr(entry, 'summary') else '',
                        'thumbnail': entry.media_thumbnail[0]['url'] if hasattr(entry, 'media_thumbnail') else ''
                    }
                    videos.append(video)
            
            return videos
            
        except Exception as e:
            print(f"Error fetching channel {channel_id}: {str(e)}")
            return []
    
    def categorize_video(self, video: Dict) -> str:
        """Categorize video based on title/description keywords"""
        text = (video['title'] + ' ' + video['description']).lower()
        
        # Product launch indicators
        if any(word in text for word in ['launch', 'released', 'introducing', 'new tool', 'announcement']):
            return 'Product Launch'
        
        # Tutorial indicators
        elif any(word in text for word in ['tutorial', 'how to', 'guide', 'step by step', 'build']):
            return 'Tutorial'
        
        # Business/strategy indicators
        elif any(word in text for word in ['business', 'revenue', 'startup', 'make money', 'saas', 'profit']):
            return 'Business Strategy'
        
        # Tool review indicators
        elif any(word in text for word in ['review', 'test', 'compared', 'vs', 'best tools']):
            return 'Tool Review'
        
        # News/update indicators
        elif any(word in text for word in ['news', 'update', 'breaking', 'latest']):
            return 'AI News'
        
        else:
            return 'General'
    
    def scan_all_channels(self, hours_back: int = 48) -> Dict[str, List[Dict]]:
        """Scan all monitored channels for new videos"""
        results = {}
        
        print(f"🎥 Scanning {len(self.channels)} YouTube channels...")
        
        for channel in self.channels:
            print(f"  Checking {channel['name']}...")
            videos = self.fetch_channel_videos(channel['channel_id'], hours_back)
            
            if videos:
                for video in videos:
                    video['channel_name'] = channel['name']
                    video['channel_category'] = channel['category']
                    video['content_category'] = self.categorize_video(video)
                
                results[channel['name']] = videos
                print(f"    Found {len(videos)} new video(s)")
        
        return results
    
    def format_digest(self, results: Dict[str, List[Dict]]) -> str:
        """Format results into digest format"""
        all_videos = []
        for channel_videos in results.values():
            all_videos.extend(channel_videos)
        
        if not all_videos:
            return "No new AI videos found in the last 48 hours."
        
        # Sort by published date (newest first)
        all_videos.sort(key=lambda x: x['published'], reverse=True)
        
        digest = f"# 🎥 YouTube AI Digest ({len(all_videos)} videos)\n\n"
        
        # Group by content category
        categories = {}
        for video in all_videos:
            cat = video['content_category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(video)
        
        for category, videos in sorted(categories.items()):
            digest += f"\n## {category} ({len(videos)})\n\n"
            
            for video in videos:
                pub_date = datetime.fromisoformat(video['published'])
                hours_ago = int((datetime.now() - pub_date).total_seconds() / 3600)
                
                digest += f"**{video['title']}**\n"
                digest += f"- Channel: {video['channel_name']} ({video['channel_category']})\n"
                digest += f"- Published: {hours_ago}h ago\n"
                digest += f"- Link: {video['url']}\n\n"
        
        return digest

def main():
    monitor = YouTubeAIMonitor()
    results = monitor.scan_all_channels(hours_back=48)
    digest = monitor.format_digest(results)
    
    print("\n" + "="*80)
    print(digest)
    print("="*80)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Exports/youtube_digest_{timestamp}.md"
    os.makedirs("Exports", exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(digest)
    
    print(f"\n✅ Digest saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
