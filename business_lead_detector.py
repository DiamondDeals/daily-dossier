#!/usr/bin/env python3
"""
Business Lead Detector - Finds automation opportunities on Reddit
"""
import json
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime
import csv
import re

from reddit_rss_client import RedditRSSClient
from subreddit_scorer import SubredditScorer


class BusinessLeadDetector:
    """Detects business leads by keyword matching in Reddit posts"""
    
    def __init__(self, keywords_file: str = 'keywords.json'):
        """
        Initialize lead detector
        
        Args:
            keywords_file: Path to keywords JSON file
        """
        self.keywords_file = keywords_file
        self.keywords = []
        self.rss_client = RedditRSSClient(rate_limit_seconds=2.0)
        self.load_keywords()
        
    def load_keywords(self):
        """Load business opportunity keywords"""
        try:
            with open(self.keywords_file, 'r') as f:
                self.keywords = json.load(f)
            print(f"✅ Loaded {len(self.keywords)} business keywords")
        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.keywords_file}")
            self.keywords = []
        except Exception as e:
            print(f"❌ Error loading keywords: {e}")
            self.keywords = []
    
    def score_post(self, post: Dict) -> Tuple[int, List[str]]:
        """
        Score a post based on keyword matches
        
        Args:
            post: Post dictionary from RSS client
            
        Returns:
            Tuple of (score, matched_keywords)
        """
        score = 0
        matched_keywords = []
        
        # Combine title and content for searching
        text = f"{post['title']} {post.get('text', '')}".lower()
        
        # Count keyword matches
        for keyword in self.keywords:
            if keyword.lower() in text:
                score += 1
                matched_keywords.append(keyword)
        
        return score, matched_keywords
    
    def search_subreddits(
        self,
        subreddits: List[str],
        min_score: int = 1,
        sort: str = 'new',
        limit_per_sub: int = 25
    ) -> List[Dict]:
        """
        Search multiple subreddits and return scored results
        
        Args:
            subreddits: List of subreddit names
            min_score: Minimum keyword matches required
            sort: Reddit sort method
            limit_per_sub: Posts per subreddit
            
        Returns:
            List of scored posts sorted by score
        """
        print(f"\n🔍 Searching {len(subreddits)} subreddits for business leads...")
        print(f"   Min keyword matches: {min_score}")
        print(f"   Posts per subreddit: {limit_per_sub}")
        print()
        
        # Fetch all posts
        results = self.rss_client.search_multiple_subreddits(
            subreddits, 
            sort=sort, 
            limit_per_sub=limit_per_sub
        )
        
        all_posts = self.rss_client.get_all_posts(results)
        print(f"\n✅ Fetched {len(all_posts)} total posts")
        
        # Score each post
        print(f"🔍 Scoring posts for business opportunities...")
        scored_posts = []
        
        for post in all_posts:
            score, keywords = self.score_post(post)
            if score >= min_score:
                post['score'] = score
                post['matched_keywords'] = keywords
                scored_posts.append(post)
        
        # Sort by score descending
        scored_posts.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Found {len(scored_posts)} posts with {min_score}+ keyword matches")
        
        return scored_posts
    
    def export_to_csv(self, posts: List[Dict], filename: str):
        """
        Export results to CSV file
        
        Args:
            posts: List of scored posts
            filename: Output filename
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'score', 'subreddit', 'title', 'author', 'published', 
                    'link', 'matched_keywords', 'content_preview'
                ])
                writer.writeheader()
                
                for post in posts:
                    writer.writerow({
                        'score': post['score'],
                        'subreddit': post['subreddit'],
                        'title': post['title'],
                        'author': post['author'],
                        'published': post['published'],
                        'link': post['link'],
                        'matched_keywords': ', '.join(post['matched_keywords'][:5]),
                        'content_preview': post['content'][:200].replace('\n', ' ')
                    })
            
            print(f"✅ Exported to CSV: {filename}")
        except Exception as e:
            print(f"❌ Error exporting CSV: {e}")
    
    def export_to_json(self, posts: List[Dict], filename: str):
        """
        Export results to JSON file
        
        Args:
            posts: List of scored posts
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported to JSON: {filename}")
        except Exception as e:
            print(f"❌ Error exporting JSON: {e}")
    
    def export_to_markdown(self, posts: List[Dict], filename: str):
        """
        Export results to Markdown file
        
        Args:
            posts: List of scored posts
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Reddit Business Leads\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Total Leads Found:** {len(posts)}\n\n")
                f.write("---\n\n")
                
                for i, post in enumerate(posts, 1):
                    f.write(f"## {i}. {post['title']}\n\n")
                    f.write(f"**Score:** {post['score']} keyword matches\n\n")
                    f.write(f"**Subreddit:** r/{post['subreddit']}\n\n")
                    f.write(f"**Author:** u/{post['author']}\n\n")
                    f.write(f"**Posted:** {post['published']}\n\n")
                    f.write(f"**Link:** {post['link']}\n\n")
                    f.write(f"**Matched Keywords:** {', '.join(post['matched_keywords'][:10])}\n\n")
                    
                    if post['content']:
                        f.write(f"**Content Preview:**\n\n")
                        preview = post['content'][:500].replace('\n', '\n> ')
                        f.write(f"> {preview}...\n\n")
                    
                    f.write("---\n\n")
            
            print(f"✅ Exported to Markdown: {filename}")
        except Exception as e:
            print(f"❌ Error exporting Markdown: {e}")
    
    def print_top_results(self, posts: List[Dict], n: int = 10):
        """
        Print top N results to console
        
        Args:
            posts: List of scored posts
            n: Number to display
        """
        print(f"\n🏆 TOP {min(n, len(posts))} BUSINESS LEADS")
        print("=" * 80)
        
        for i, post in enumerate(posts[:n], 1):
            print(f"\n{i}. [{post['score']} matches] {post['title']}")
            print(f"   📍 r/{post['subreddit']} · u/{post['author']}")
            print(f"   🔗 {post['link']}")
            print(f"   🔑 Keywords: {', '.join(post['matched_keywords'][:5])}")
            if post['content']:
                preview = post['content'][:150].replace('\n', ' ')
                print(f"   📝 {preview}...")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    print("=" * 80)
    print("BUSINESS LEAD DETECTOR - Reddit Automation Opportunity Finder")
    print("=" * 80)
    
    # Initialize detector
    detector = BusinessLeadDetector()
    
    # Test with r/entrepreneur
    print("\n🧪 TESTING WITH r/entrepreneur")
    results = detector.search_subreddits(
        subreddits=['entrepreneur'],
        min_score=2,
        limit_per_sub=50
    )
    
    # Show top results
    detector.print_top_results(results, 10)
    
    # Export results
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        detector.export_to_csv(results, f'Exports/leads_{timestamp}.csv')
        detector.export_to_json(results, f'Exports/leads_{timestamp}.json')
        detector.export_to_markdown(results, f'Exports/leads_{timestamp}.md')
    
    print("\n✅ Business lead detection complete!")
