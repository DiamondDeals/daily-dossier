#!/usr/bin/env python3
"""
Quick Reddit Subreddit NSFW Classifier
Uses requests + BeautifulSoup for faster initial classification
"""

import csv
import requests
import time
import re
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Optional
import random


class QuickRedditClassifier:
    """Quick Reddit subreddit classifier using requests."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.nsfw_keywords = self.load_nsfw_keywords()
        self.safe_keywords = self.load_safe_keywords()
        
    def load_nsfw_keywords(self) -> List[str]:
        """Load NSFW detection keywords."""
        return [
            # Explicit content
            'porn', 'nsfw', 'adult', 'sex', 'nude', 'naked', 'xxx', 'gonewild',
            'fetish', 'kink', 'bdsm', 'hentai', 'erotic', 'sexual', 'amateur',
            'milf', 'teen', 'boobs', 'ass', 'dick', 'cock', 'pussy', 'cumshot',
            
            # Suggestive content  
            'curves', 'bikini', 'lingerie', 'cleavage', 'upskirt', 'thong',
            'revealing', 'seductive', 'provocative', 'sensual', 'intimate',
            
            # Adult services/content
            'escort', 'cam', 'onlyfans', 'premium', 'tribute', 'rate me',
            'selling', 'custom', 'private', 'snapchat', 'dirty', 'horny',
            
            # Age markers
            '18+', '18 plus', 'adults only', 'mature audience', 'not safe for work',
            
            # Body parts
            'titties', 'tits', 'breasts', 'nipples', 'vagina', 'penis', 'genitals',
            
            # Additional NSFW indicators
            'slutty', 'sexy', 'hot', 'naughty', 'wild', 'bare', 'exposed'
        ]
        
    def load_safe_keywords(self) -> List[str]:
        """Load keywords that indicate safe content."""
        return [
            'help', 'support', 'community', 'discussion', 'advice', 'tips',
            'learning', 'education', 'tutorial', 'guide', 'news', 'information',
            'technology', 'science', 'art', 'music', 'gaming', 'sports',
            'food', 'cooking', 'travel', 'photography', 'books', 'movies',
            'fitness', 'health', 'business', 'career', 'finance', 'investing',
            'diy', 'crafts', 'gardening', 'pets', 'family', 'parenting',
            'academic', 'research', 'professional', 'official', 'government'
        ]
        
    def get_subreddit_info(self, subreddit_name: str) -> Optional[str]:
        """Get subreddit info using requests."""
        url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    description = data['data'].get('public_description', '') or data['data'].get('description', '')
                    title = data['data'].get('title', '')
                    over_18 = data['data'].get('over18', False)
                    
                    # If marked as over 18, it's definitely NSFW
                    if over_18:
                        return f"[OVER18] {title} - {description}"
                    
                    return f"{title} - {description}"
                    
        except Exception as e:
            print(f"Error getting info for r/{subreddit_name}: {e}")
            
        # Fallback to web scraping
        return self.scrape_subreddit_web(subreddit_name)
        
    def scrape_subreddit_web(self, subreddit_name: str) -> Optional[str]:
        """Fallback web scraping method."""
        url = f"https://www.reddit.com/r/{subreddit_name}/"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for description in various places
                description_text = ""
                
                # Try meta description
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc:
                    description_text = meta_desc.get('content', '')
                    
                return description_text
                
        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {e}")
            
        return None
        
    def analyze_content(self, content: str, subreddit_name: str) -> Dict:
        """Analyze content for NSFW classification."""
        if not content:
            return {
                'nsfw_flag': 'UNKNOWN',
                'reason': 'No content found',
                'confidence': 0,
                'keywords_found': []
            }
            
        content_lower = content.lower()
        subreddit_lower = subreddit_name.lower()
        
        # Check for over18 marker
        if '[OVER18]' in content:
            return {
                'nsfw_flag': 'YES',
                'reason': 'Marked as Over 18 by Reddit',
                'confidence': 10,
                'keywords_found': ['over18']
            }
        
        # Check for NSFW keywords
        nsfw_matches = []
        for keyword in self.nsfw_keywords:
            if keyword in content_lower or keyword in subreddit_lower:
                nsfw_matches.append(keyword)
                
        # Check for safe keywords
        safe_matches = []
        for keyword in self.safe_keywords:
            if keyword in content_lower:
                safe_matches.append(keyword)
                
        # Special NSFW patterns
        nsfw_patterns = [
            r'\b(18\+|18 plus|adults? only)\b',
            r'\b(not safe for work|nsfw)\b',
            r'\b(selling|custom|premium)\b.*\b(content|pics?|videos?)\b',
            r'\b(rate me|tribute)\b',
            r'\b(cam|onlyfans)\b',
            r'\b(gone ?wild|realgirls?|amateur)\b'
        ]
        
        pattern_matches = []
        for pattern in nsfw_patterns:
            if re.search(pattern, content_lower):
                pattern_matches.append(pattern)
                
        # Enhanced subreddit name analysis
        subreddit_nsfw_indicators = [
            'gone', 'wild', 'nude', 'nsfw', 'xxx', 'porn', 'sex', 'adult',
            'girls', 'ladies', 'babes', 'hotties', 'rate', 'tribute'
        ]
        
        name_nsfw_matches = []
        for indicator in subreddit_nsfw_indicators:
            if indicator in subreddit_lower:
                name_nsfw_matches.append(indicator)
        
        # Calculate scores
        nsfw_score = len(nsfw_matches) * 2 + len(pattern_matches) * 3 + len(name_nsfw_matches) * 2
        safe_score = len(safe_matches)
        
        # Decision logic
        if nsfw_score >= 6 or len(pattern_matches) >= 1:
            classification = 'YES'
            all_matches = nsfw_matches + pattern_matches + name_nsfw_matches
            reason = f"Strong NSFW indicators: {', '.join(all_matches[:5])}"
            confidence = min(10, nsfw_score)
        elif nsfw_score >= 3 or len(name_nsfw_matches) >= 1:
            classification = 'MAYBE'
            all_matches = nsfw_matches + name_nsfw_matches
            reason = f"Possible NSFW content: {', '.join(all_matches[:3])}"
            confidence = nsfw_score
        elif safe_score >= 3:
            classification = 'NO'
            reason = f"Safe content indicators: {', '.join(safe_matches[:3])}"
            confidence = 0
        else:
            classification = 'UNKNOWN'
            reason = "Insufficient information for classification"
            confidence = 0
            
        return {
            'nsfw_flag': classification,
            'reason': reason,
            'confidence': confidence,
            'keywords_found': nsfw_matches + pattern_matches + name_nsfw_matches
        }
        
    def process_subreddits(self, input_file: str, output_file: str):
        """Process subreddits from CSV."""
        results = []
        processed_count = 0
        
        # Read input CSV
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            subreddits = list(reader)
            
        total_count = len(subreddits)
        print(f"Processing {total_count} subreddits...")
        
        for row in subreddits:
            subreddit_name = row['Subreddit']
            print(f"Processing {processed_count + 1}/{total_count}: r/{subreddit_name}")
            
            # Get subreddit info
            content = self.get_subreddit_info(subreddit_name)
            
            # Analyze content
            analysis = self.analyze_content(content, subreddit_name)
            
            # Create result
            result_row = {
                'Subreddit': subreddit_name,
                'Link': row.get('Link', f'https://www.reddit.com/r/{subreddit_name}/'),
                'Description': content or 'No description found',
                'NSFW_Flag': analysis['nsfw_flag'],
                'NSFW_Reason': analysis['reason'], 
                'Confidence_Score': analysis['confidence'],
                'Keywords_Found': ', '.join(analysis['keywords_found'])
            }
            
            results.append(result_row)
            processed_count += 1
            
            # Save progress every 100 subreddits
            if processed_count % 100 == 0:
                self.save_results(results, output_file)
                print(f"Progress saved: {processed_count}/{total_count}")
                
            # Rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
        # Final save
        self.save_results(results, output_file)
        print(f"Completed processing {processed_count} subreddits")
        
        return results
        
    def save_results(self, results: List[Dict], output_file: str):
        """Save results to CSV."""
        if not results:
            return
            
        fieldnames = ['Subreddit', 'Link', 'Description', 'NSFW_Flag', 'NSFW_Reason', 'Confidence_Score', 'Keywords_Found']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    def create_separate_files(self, classified_file: str):
        """Create separate NSFW and Safe CSV files."""
        df = pd.read_csv(classified_file)
        
        # NSFW file
        nsfw_df = df[df['NSFW_Flag'].isin(['YES', 'MAYBE'])]
        nsfw_file = classified_file.replace('.csv', '_NSFW_ONLY.csv')
        nsfw_df.to_csv(nsfw_file, index=False)
        print(f"Created NSFW file with {len(nsfw_df)} subreddits: {nsfw_file}")
        
        # Safe file  
        safe_df = df[df['NSFW_Flag'] == 'NO']
        safe_file = classified_file.replace('.csv', '_SAFE_ONLY.csv')
        safe_df.to_csv(safe_file, index=False)
        print(f"Created Safe file with {len(safe_df)} subreddits: {safe_file}")
        
        # Unknown file
        unknown_df = df[df['NSFW_Flag'] == 'UNKNOWN'] 
        if len(unknown_df) > 0:
            unknown_file = classified_file.replace('.csv', '_UNKNOWN.csv')
            unknown_df.to_csv(unknown_file, index=False)
            print(f"Created Unknown file with {len(unknown_df)} subreddits: {unknown_file}")


def main():
    """Main execution."""
    classifier = QuickRedditClassifier()
    
    # Files
    input_file = "Reddit SubReddits - ALL SUBREDDITS.csv"
    output_file = "Reddit_SubReddits_Quick_Classified.csv"
    
    # Process
    results = classifier.process_subreddits(input_file, output_file)
    
    # Create separate files
    classifier.create_separate_files(output_file)
    
    # Summary
    df = pd.read_csv(output_file)
    summary = df['NSFW_Flag'].value_counts()
    print("\nClassification Summary:")
    for flag, count in summary.items():
        print(f"{flag}: {count}")


if __name__ == "__main__":
    main()