#!/usr/bin/env python3
"""
Moltbook Scanner - READ ONLY MODE
Scans your 17 subscribed submolts for interesting builds, security, and insights
ZERO INTERACTION - View and report only
"""
import json
import requests
from datetime import datetime
from pathlib import Path

class MoltbookScanner:
    def __init__(self):
        self.base_url = "https://www.moltbook.com/api/v1"
        self.credentials_path = Path.home() / ".config/moltbook/credentials.json"
        self.api_key = None
        self.agent_name = None
        self._load_credentials()
        
        # Interest keywords
        self.keywords = {
            'builds': ['built', 'launched', 'shipped', 'released', 'project', 'product'],
            'security': ['security', 'vulnerability', 'exploit', 'patch', 'bug', 'credential'],
            'money': ['revenue', 'mrr', 'arr', '$', 'paid', 'earn', 'profit'],
            'automation': ['automate', 'workflow', 'script', 'integration'],
            'learning': ['learned', 'lesson', 'tip', 'how to', 'guide']
        }
    
    def _load_credentials(self):
        """Load API credentials"""
        try:
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)
                self.api_key = creds.get('api_key')
                self.agent_name = creds.get('agent_name', 'BishopLizard')
                
                # Verify security posture
                security_posture = creds.get('security_posture', '')
                if security_posture != 'READ_ONLY_NO_INTERACTION':
                    print(f"⚠️ WARNING: Security posture is {security_posture}")
                    
        except FileNotFoundError:
            raise Exception(f"Credentials not found at {self.credentials_path}")
        except json.JSONDecodeError:
            raise Exception("Invalid credentials JSON")
    
    def scan_feed(self, limit=50):
        """
        Scan personalized feed (READ ONLY)
        Returns top interesting posts
        """
        try:
            # Get feed endpoint with authentication
            feed_url = f"{self.base_url}/feed"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'User-Agent': f'MoltbookPatrol/1.0 ({self.agent_name})'
            }
            
            response = requests.get(
                feed_url,
                headers=headers,
                params={'sort': 'hot', 'limit': limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response structures
                if isinstance(data, dict) and 'posts' in data:
                    posts = data['posts']
                elif isinstance(data, list):
                    posts = data
                else:
                    posts = []
                
                # Score and filter interesting posts
                interesting = []
                for post in posts:
                    scored = self._score_post(post)
                    if scored and scored['score'] > 0:
                        interesting.append(scored)
                
                # Sort by score
                interesting.sort(key=lambda x: x['score'], reverse=True)
                
                return interesting
            else:
                print(f"⚠️ Feed fetch failed: {response.status_code}")
                if response.status_code == 401:
                    print("   API key might be invalid or expired")
                return []
                
        except Exception as e:
            print(f"❌ Error scanning Moltbook: {e}")
            return []
    
    def _score_post(self, post):
        """Score a post for interestingness"""
        try:
            title = post.get('title', '').lower()
            content = post.get('content', '').lower()
            combined = title + ' ' + content
            
            score = 0
            categories = []
            matched_keywords = []
            
            # Score by category
            for category, keywords in self.keywords.items():
                for keyword in keywords:
                    if keyword in combined:
                        score += 10
                        if category not in categories:
                            categories.append(category)
                        if keyword not in matched_keywords:
                            matched_keywords.append(keyword)
            
            # Skip if no matches
            if score == 0:
                return None
            
            # Engagement bonus
            upvotes = post.get('upvotes', 0)
            comments = post.get('comments', 0)
            score += upvotes + (comments * 2)
            
            # Build/ship bonus
            if any(x in combined for x in ['launched', 'shipped', 'built', 'released']):
                score += 20
            
            # Revenue/money bonus
            if any(x in combined for x in ['$', 'revenue', 'mrr', 'paid']):
                score += 15
            
            return {
                'title': post.get('title', 'Untitled'),
                'content': content[:200],
                'author': post.get('author', 'unknown'),
                'submolt': post.get('submolt', 'unknown'),
                'url': f"https://moltbook.com/post/{post.get('id', '')}",
                'upvotes': upvotes,
                'comments': comments,
                'score': score,
                'categories': categories,
                'keywords': matched_keywords[:5]
            }
            
        except Exception as e:
            return None
    
    def generate_report(self, posts, top_n=10):
        """Generate markdown report"""
        if not posts:
            return "⚠️ No interesting posts found on Moltbook"
        
        report = []
        report.append(f"## 🦞 Moltbook - Top {min(len(posts), top_n)}\n")
        
        for i, post in enumerate(posts[:top_n], 1):
            categories = ' • '.join([f"#{cat}" for cat in post['categories']])
            
            report.append(f"**{i}. {post['title']}**")
            report.append(f"- m/{post['submolt']} • @{post['author']}")
            report.append(f"- {categories}")
            report.append(f"- ↑{post['upvotes']} • 💬{post['comments']} • Score: {post['score']}")
            report.append(f"- {post['url']}\n")
        
        return '\n'.join(report)

if __name__ == '__main__':
    print("=" * 70)
    print("MOLTBOOK SCANNER - READ ONLY MODE")
    print("Scanning feed for interesting builds & insights")
    print("=" * 70)
    print()
    
    scanner = MoltbookScanner()
    
    print(f"⚠️ SECURITY MODE: READ ONLY - No interaction with posts/agents")
    print(f"📡 Connected as: {scanner.agent_name}")
    print()
    
    posts = scanner.scan_feed(limit=100)
    
    if posts:
        print(f"✅ Found {len(posts)} interesting posts")
        print("\n" + scanner.generate_report(posts, top_n=10))
    else:
        print("⚠️ No interesting posts found matching criteria")
    
    print("\n" + "=" * 70)
    print(f"✅ Moltbook scan complete - Found {len(posts)} posts (READ ONLY)")
    print("=" * 70)
