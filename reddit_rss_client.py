#!/usr/bin/env python3
"""
Reddit RSS Client - NO authentication needed!
Uses RSS feeds to scrape Reddit without API credentials.
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from typing import List, Dict, Optional
import html


class RedditRSSClient:
    """Client for fetching Reddit posts via RSS feeds"""
    
    def __init__(self, rate_limit_seconds: float = 2.0):
        """
        Initialize RSS client
        
        Args:
            rate_limit_seconds: Minimum seconds between requests (default: 2)
        """
        self.rate_limit = rate_limit_seconds
        self.last_request_time = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def _rate_limit_wait(self):
        """Ensure rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
        
    def fetch_subreddit_posts(
        self, 
        subreddit: str, 
        sort: str = 'new',
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch posts from a subreddit via RSS
        
        Args:
            subreddit: Name of subreddit (without r/)
            sort: Sort method - 'new', 'hot', 'top', 'rising'
            limit: Maximum posts to return (None = all in feed)
            
        Returns:
            List of post dictionaries with keys:
                - title: Post title
                - author: Username
                - link: Reddit post URL
                - content: Post text/description
                - published: ISO timestamp
                - subreddit: Subreddit name
        """
        self._rate_limit_wait()
        
        # Build RSS URL
        base_url = f"https://www.reddit.com/r/{subreddit}"
        if sort != 'hot':
            base_url += f"/{sort}"
        rss_url = f"{base_url}/.rss"
        
        try:
            response = requests.get(
                rss_url, 
                headers=self.headers, 
                timeout=10
            )
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Find all entries (posts)
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            posts = []
            for entry in entries:
                # Extract post data
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                author_elem = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
                link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
                
                # Build post dict
                post = {
                    'title': html.unescape(title_elem.text) if title_elem is not None else '',
                    'author': author_elem.text if author_elem is not None else '',
                    'link': link_elem.get('href') if link_elem is not None else '',
                    'published': published_elem.text if published_elem is not None else '',
                    'subreddit': subreddit,
                    'content': ''
                }
                
                # Extract and clean content
                if content_elem is not None and content_elem.text:
                    # Content is HTML, extract text
                    content_html = content_elem.text
                    # Simple HTML tag removal
                    import re
                    content_text = re.sub(r'<[^>]+>', '', content_html)
                    post['content'] = html.unescape(content_text).strip()
                
                posts.append(post)
                
                if limit and len(posts) >= limit:
                    break
            
            return posts
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching r/{subreddit}: {e}")
            return []
        except ET.ParseError as e:
            print(f"❌ Error parsing XML for r/{subreddit}: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error for r/{subreddit}: {e}")
            return []
    
    def search_multiple_subreddits(
        self,
        subreddits: List[str],
        sort: str = 'new',
        limit_per_sub: Optional[int] = 25
    ) -> Dict[str, List[Dict]]:
        """
        Search multiple subreddits and return all posts
        
        Args:
            subreddits: List of subreddit names
            sort: Sort method
            limit_per_sub: Posts per subreddit
            
        Returns:
            Dict mapping subreddit name to list of posts
        """
        results = {}
        
        for i, subreddit in enumerate(subreddits, 1):
            print(f"📡 Fetching r/{subreddit} ({i}/{len(subreddits)})...")
            posts = self.fetch_subreddit_posts(subreddit, sort, limit_per_sub)
            results[subreddit] = posts
            print(f"   ✓ Found {len(posts)} posts")
        
        return results
    
    def get_all_posts(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Flatten multi-subreddit results into single list
        
        Args:
            results: Dict from search_multiple_subreddits
            
        Returns:
            List of all posts across all subreddits
        """
        all_posts = []
        for posts in results.values():
            all_posts.extend(posts)
        return all_posts


if __name__ == "__main__":
    # Test with r/entrepreneur
    print("=" * 60)
    print("TESTING REDDIT RSS CLIENT")
    print("=" * 60)
    
    client = RedditRSSClient(rate_limit_seconds=2.0)
    
    print("\n🔍 Testing with r/entrepreneur...")
    posts = client.fetch_subreddit_posts('entrepreneur', limit=5)
    
    print(f"\n✅ Fetched {len(posts)} posts:\n")
    
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title']}")
        print(f"   Author: u/{post['author']}")
        print(f"   Link: {post['link']}")
        print(f"   Published: {post['published']}")
        if post['content']:
            preview = post['content'][:150].replace('\n', ' ')
            print(f"   Preview: {preview}...")
        print()
    
    print("=" * 60)
    print("✅ RSS CLIENT WORKS!")
    print("=" * 60)
