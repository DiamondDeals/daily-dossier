#!/usr/bin/env python3
"""
Subreddit Scorer - Ranks 95k subreddits by business opportunity potential
"""
import csv
import re
from typing import List, Dict, Tuple
from pathlib import Path


class SubredditScorer:
    """Loads and scores subreddits for business lead potential"""
    
    # Scoring rules by keyword category
    SCORING_RULES = {
        'high_value': {
            'keywords': [
                'entrepreneur', 'business', 'smallbusiness', 'startup', 'startups',
                'businessowners', 'saas', 'marketing', 'digitalnomad', 'sidehustle',
                'passiveincome', 'ecommerce', 'freelance', 'consulting', 'agency'
            ],
            'score': 90
        },
        'medium_high': {
            'keywords': [
                'automation', 'workflow', 'productivity', 'efficiency', 'tools',
                'software', 'apps', 'tech', 'programming', 'webdev', 'development',
                'api', 'integration', 'nocode', 'lowcode'
            ],
            'score': 70
        },
        'medium': {
            'keywords': [
                'help', 'tips', 'advice', 'howto', 'guide', 'tutorial', 'learn',
                'ask', 'question', 'solution', 'problem', 'issue', 'challenge'
            ],
            'score': 50
        },
        'industry': {
            'keywords': [
                'realestate', 'finance', 'accounting', 'legal', 'medical', 'health',
                'fitness', 'education', 'teaching', 'design', 'creative', 'writing',
                'sales', 'crm', 'customer', 'support', 'service'
            ],
            'score': 60
        }
    }
    
    def __init__(self, csv_path: str = 'csvtojson/subreddits.csv'):
        """
        Initialize scorer with subreddit database
        
        Args:
            csv_path: Path to subreddits.csv file
        """
        self.csv_path = csv_path
        self.subreddits = []
        self.scored_subreddits = []
        self.load_subreddits()
        
    def load_subreddits(self):
        """Load subreddits from CSV file"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.subreddits = [row['Subreddit'] for row in reader]
            print(f"✅ Loaded {len(self.subreddits):,} subreddits from database")
        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.csv_path}")
            self.subreddits = []
        except Exception as e:
            print(f"❌ Error loading subreddits: {e}")
            self.subreddits = []
    
    def score_subreddit(self, subreddit: str) -> int:
        """
        Score a single subreddit based on business potential
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            Score from 0-100 (higher = better business opportunity)
        """
        subreddit_lower = subreddit.lower()
        max_score = 0
        
        # Check against all scoring rules
        for category, rules in self.SCORING_RULES.items():
            for keyword in rules['keywords']:
                if keyword in subreddit_lower:
                    # Use highest matching score
                    max_score = max(max_score, rules['score'])
                    break
        
        # Boost score for exact matches to high-value keywords
        if subreddit_lower in ['entrepreneur', 'smallbusiness', 'startups', 'saas']:
            max_score = 100
        
        return max_score
    
    def score_all_subreddits(self) -> List[Tuple[str, int]]:
        """
        Score all subreddits and return sorted by score
        
        Returns:
            List of (subreddit, score) tuples sorted by score descending
        """
        print(f"\n🔍 Scoring {len(self.subreddits):,} subreddits...")
        
        scored = []
        for subreddit in self.subreddits:
            score = self.score_subreddit(subreddit)
            if score > 0:  # Only keep subreddits with some score
                scored.append((subreddit, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        self.scored_subreddits = scored
        print(f"✅ Found {len(scored):,} relevant subreddits for business leads")
        
        return scored
    
    def get_top_subreddits(self, n: int = 50, min_score: int = 50) -> List[Tuple[str, int]]:
        """
        Get top N subreddits above minimum score
        
        Args:
            n: Number of subreddits to return
            min_score: Minimum score threshold
            
        Returns:
            List of (subreddit, score) tuples
        """
        if not self.scored_subreddits:
            self.score_all_subreddits()
        
        # Filter by minimum score
        filtered = [
            (sub, score) for sub, score in self.scored_subreddits
            if score >= min_score
        ]
        
        return filtered[:n]
    
    def filter_by_keywords(self, keywords: List[str]) -> List[Tuple[str, int]]:
        """
        Filter subreddits by specific keywords
        
        Args:
            keywords: List of keywords to match
            
        Returns:
            List of (subreddit, score) tuples
        """
        if not self.scored_subreddits:
            self.score_all_subreddits()
        
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for subreddit, score in self.scored_subreddits:
            subreddit_lower = subreddit.lower()
            if any(keyword in subreddit_lower for keyword in keywords_lower):
                results.append((subreddit, score))
        
        return results
    
    def print_top_subreddits(self, n: int = 25):
        """Print top N subreddits with scores"""
        top = self.get_top_subreddits(n)
        
        print(f"\n🏆 TOP {len(top)} SUBREDDITS FOR BUSINESS LEADS")
        print("=" * 60)
        
        for i, (subreddit, score) in enumerate(top, 1):
            bar = "█" * (score // 5)  # Visual score bar
            print(f"{i:2}. r/{subreddit:30} [{score:3}] {bar}")
        
        print("=" * 60)
    
    def get_stats(self) -> Dict:
        """Get statistics about scored subreddits"""
        if not self.scored_subreddits:
            self.score_all_subreddits()
        
        scores = [score for _, score in self.scored_subreddits]
        
        return {
            'total_subreddits': len(self.subreddits),
            'scored_subreddits': len(self.scored_subreddits),
            'score_100': sum(1 for s in scores if s == 100),
            'score_90_plus': sum(1 for s in scores if s >= 90),
            'score_70_plus': sum(1 for s in scores if s >= 70),
            'score_50_plus': sum(1 for s in scores if s >= 50),
        }


if __name__ == "__main__":
    print("=" * 60)
    print("SUBREDDIT SCORER - Business Lead Detection")
    print("=" * 60)
    
    # Initialize scorer
    scorer = SubredditScorer()
    
    # Score all subreddits
    scorer.score_all_subreddits()
    
    # Show stats
    stats = scorer.get_stats()
    print(f"\n📊 STATISTICS:")
    print(f"   Total subreddits in database: {stats['total_subreddits']:,}")
    print(f"   Relevant for business leads:  {stats['scored_subreddits']:,}")
    print(f"   Perfect score (100):          {stats['score_100']:,}")
    print(f"   High value (90+):             {stats['score_90_plus']:,}")
    print(f"   Medium-high (70+):            {stats['score_70_plus']:,}")
    print(f"   Medium (50+):                 {stats['score_50_plus']:,}")
    
    # Show top subreddits
    scorer.print_top_subreddits(30)
    
    print("\n✅ Subreddit scoring complete!")
