#!/usr/bin/env python3
"""
Enhanced Reddit RSS Client - Version 2
Includes engagement scoring (upvotes + comments)
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import time

class RedditRSSClient:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_posts(self, subreddit, limit=25, sort='new'):
        """
        Fetch posts from a subreddit via RSS
        sort: 'new', 'hot', 'top', 'rising'
        """
        rss_url = f"https://www.reddit.com/r/{subreddit}/{sort}/.rss?limit={limit}"
        
        try:
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            posts = []
            for entry in entries:
                post = self._parse_entry(entry, subreddit)
                if post:
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            return []
    
    def _parse_entry(self, entry, subreddit):
        """Parse RSS entry into structured post data with engagement scoring"""
        try:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            author = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name').text
            link = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            
            # Get content
            content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
            content_html = content_elem.text if content_elem is not None else ""
            
            # Extract plain text from HTML
            text = self._extract_text(content_html)
            
            # Extract upvotes and comments from content
            upvotes = self._extract_upvotes(content_html)
            comments = self._extract_comments(content_html)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement(upvotes, comments)
            
            # Detect if this is a service offer (should be filtered)
            is_service_offer = self._is_service_offer(title, text)
            
            return {
                'title': title,
                'author': author.replace('/u/', ''),
                'subreddit': subreddit,
                'link': link,
                'published': published,
                'text': text[:500],  # First 500 chars
                'upvotes': upvotes,
                'comments': comments,
                'engagement_score': engagement_score,
                'is_service_offer': is_service_offer
            }
            
        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None
    
    def _extract_text(self, html):
        """Extract plain text from HTML content"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    def _extract_upvotes(self, html):
        """Extract upvote count from HTML"""
        # Look for patterns like "23 points" or "score: 45"
        match = re.search(r'(\d+)\s+points?', html)
        if match:
            return int(match.group(1))
        
        match = re.search(r'score:\s*(\d+)', html)
        if match:
            return int(match.group(1))
        
        return 0  # Default if not found
    
    def _extract_comments(self, html):
        """Extract comment count from HTML"""
        # Look for patterns like "15 comments"
        match = re.search(r'(\d+)\s+comments?', html)
        if match:
            return int(match.group(1))
        
        return 0  # Default if not found
    
    def _calculate_engagement(self, upvotes, comments):
        """
        Calculate engagement score
        Upvotes + (Comments * 2) - comments are 2x valuable as they indicate discussion
        """
        return upvotes + (comments * 2)
    
    def _is_service_offer(self, title, text):
        """
        Detect if post is someone offering services (not looking for solutions)
        """
        offer_keywords = [
            'will do', 'available for', 'offering', 'can help',
            'looking to work', 'hire me', 'freelancer available',
            'dm me', 'reach out', 'contact me', 'for hire',
            '$1', 'free consultation', 'book a call'
        ]
        
        combined = (title + ' ' + text).lower()
        
        for keyword in offer_keywords:
            if keyword in combined:
                return True
        
        return False

if __name__ == '__main__':
    print("Testing Enhanced Reddit RSS Client (v2)")
    print("=" * 60)
    
    client = RedditRSSClient()
    posts = client.fetch_posts('entrepreneur', limit=10, sort='hot')
    
    print(f"\nFound {len(posts)} posts from r/entrepreneur\n")
    
    # Sort by engagement score
    posts.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    for i, post in enumerate(posts[:5], 1):
        service_flag = "🚫 SERVICE OFFER" if post['is_service_offer'] else ""
        print(f"{i}. {post['title']}")
        print(f"   👤 u/{post['author']}")
        print(f"   📊 Engagement: {post['engagement_score']} (↑{post['upvotes']} + 💬{post['comments']})")
        print(f"   {service_flag}")
        print(f"   🔗 {post['link']}")
        print()
