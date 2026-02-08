#!/usr/bin/env python3
"""
Improved Reddit Subreddit NSFW Classifier
Uses Selenium to scrape subreddit descriptions for better classification accuracy.
"""

import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from typing import Dict, List, Tuple, Optional
import json


class ImprovedRedditClassifier:
    """Enhanced Reddit subreddit classifier using description-based analysis."""
    
    def __init__(self):
        self.setup_selenium()
        self.nsfw_keywords = self.load_nsfw_keywords()
        self.safe_keywords = self.load_safe_keywords()
        
    def setup_selenium(self):
        """Initialize headless Chrome driver."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
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
            
            # Age markers (concerning)
            '18+', '18 plus', 'adults only', 'mature audience', 'not safe for work',
            
            # Body parts (contextual)
            'titties', 'tits', 'breasts', 'nipples', 'vagina', 'penis', 'genitals'
        ]
        
    def load_safe_keywords(self) -> List[str]:
        """Load keywords that indicate safe content."""
        return [
            'help', 'support', 'community', 'discussion', 'advice', 'tips',
            'learning', 'education', 'tutorial', 'guide', 'news', 'information',
            'technology', 'science', 'art', 'music', 'gaming', 'sports',
            'food', 'cooking', 'travel', 'photography', 'books', 'movies',
            'fitness', 'health', 'business', 'career', 'finance', 'investing',
            'diy', 'crafts', 'gardening', 'pets', 'family', 'parenting'
        ]
        
    def get_subreddit_description(self, subreddit_name: str) -> Optional[str]:
        """Scrape subreddit description using Selenium."""
        url = f"https://www.reddit.com/r/{subreddit_name}/"
        
        try:
            self.driver.get(url)
            time.sleep(2)  # Allow page to load
            
            # Look for description in sidebar
            description_selectors = [
                '[data-testid="subreddit-about-card"] p',
                '.subreddit-description p',
                '.sidebar .usertext-body p',
                '.subreddit-header-bottom .subreddit-description',
                '.subreddit-description',
                '[data-click-id="subreddit"]',
                '.community-description p'
            ]
            
            description_text = ""
            
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        description_text = " ".join([elem.text for elem in elements[:3]])  # First 3 paragraphs
                        if description_text.strip():
                            break
                except:
                    continue
                    
            # If no description found, try title/header
            if not description_text.strip():
                try:
                    title_element = self.driver.find_element(By.CSS_SELECTOR, 'h1')
                    description_text = title_element.text
                except:
                    pass
                    
            return description_text.strip() if description_text else None
            
        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {e}")
            return None
            
    def analyze_description(self, description: str, subreddit_name: str) -> Dict:
        """Analyze description text for NSFW content."""
        if not description:
            return {
                'nsfw_flag': 'UNKNOWN',
                'reason': 'No description found',
                'confidence': 0,
                'keywords_found': []
            }
            
        description_lower = description.lower()
        subreddit_lower = subreddit_name.lower()
        
        # Check for explicit NSFW keywords
        nsfw_matches = []
        for keyword in self.nsfw_keywords:
            if keyword in description_lower or keyword in subreddit_lower:
                nsfw_matches.append(keyword)
                
        # Check for safe keywords
        safe_matches = []
        for keyword in self.safe_keywords:
            if keyword in description_lower:
                safe_matches.append(keyword)
                
        # Special patterns
        nsfw_patterns = [
            r'\b(18\+|18 plus|adults? only)\b',
            r'\b(not safe for work|nsfw)\b',
            r'\b(selling|custom|premium)\b.*\b(content|pics?|videos?)\b',
            r'\b(rate me|tribute)\b',
            r'\b(cam|onlyfans)\b'
        ]
        
        pattern_matches = []
        for pattern in nsfw_patterns:
            if re.search(pattern, description_lower):
                pattern_matches.append(pattern)
                
        # Calculate confidence score
        nsfw_score = len(nsfw_matches) * 2 + len(pattern_matches) * 3
        safe_score = len(safe_matches)
        
        # Decision logic
        if nsfw_score >= 4 or len(pattern_matches) >= 1:
            classification = 'YES'
            reason = f"NSFW keywords/patterns found: {', '.join(nsfw_matches + pattern_matches)}"
            confidence = min(10, nsfw_score)
        elif nsfw_score >= 2:
            classification = 'MAYBE'
            reason = f"Some suggestive content detected: {', '.join(nsfw_matches)}"
            confidence = nsfw_score
        elif safe_score >= 2:
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
            'keywords_found': nsfw_matches + pattern_matches,
            'safe_keywords': safe_matches
        }
        
    def process_subreddits_from_csv(self, input_file: str, output_file: str):
        """Process subreddits from CSV file and add descriptions."""
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
            
            # Get description
            description = self.get_subreddit_description(subreddit_name)
            
            # Analyze description
            analysis = self.analyze_description(description, subreddit_name)
            
            # Create result row
            result_row = {
                'Subreddit': subreddit_name,
                'Link': row.get('Link', f'https://www.reddit.com/r/{subreddit_name}/'),
                'Description': description or 'No description found',
                'NSFW_Flag': analysis['nsfw_flag'],
                'NSFW_Reason': analysis['reason'],
                'Confidence_Score': analysis['confidence'],
                'Keywords_Found': ', '.join(analysis['keywords_found']),
                'Safe_Keywords': ', '.join(analysis['safe_keywords'])
            }
            
            results.append(result_row)
            processed_count += 1
            
            # Save progress every 50 subreddits
            if processed_count % 50 == 0:
                self.save_results(results, output_file)
                print(f"Progress saved: {processed_count}/{total_count}")
                
            # Rate limiting
            time.sleep(1)
            
        # Final save
        self.save_results(results, output_file)
        print(f"Completed processing {processed_count} subreddits")
        
        return results
        
    def save_results(self, results: List[Dict], output_file: str):
        """Save results to CSV file."""
        if not results:
            return
            
        fieldnames = [
            'Subreddit', 'Link', 'Description', 'NSFW_Flag', 
            'NSFW_Reason', 'Confidence_Score', 'Keywords_Found', 'Safe_Keywords'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    def create_separate_files(self, classified_file: str):
        """Create separate NSFW and Safe CSV files."""
        df = pd.read_csv(classified_file)
        
        # NSFW file (YES and MAYBE)
        nsfw_df = df[df['NSFW_Flag'].isin(['YES', 'MAYBE'])]
        nsfw_file = classified_file.replace('.csv', '_NSFW_ONLY.csv')
        nsfw_df.to_csv(nsfw_file, index=False)
        print(f"Created NSFW file with {len(nsfw_df)} subreddits: {nsfw_file}")
        
        # Safe file (NO)
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
            
    def cleanup(self):
        """Close browser and cleanup resources."""
        if hasattr(self, 'driver'):
            self.driver.quit()


def main():
    """Main execution function."""
    classifier = ImprovedRedditClassifier()
    
    try:
        # Input and output files
        input_file = "Reddit SubReddits - ALL SUBREDDITS.csv"
        output_file = "Reddit_SubReddits_With_Descriptions_Classified.csv"
        
        # Process subreddits
        results = classifier.process_subreddits_from_csv(input_file, output_file)
        
        # Create separate files
        classifier.create_separate_files(output_file)
        
        # Print summary
        df = pd.read_csv(output_file)
        summary = df['NSFW_Flag'].value_counts()
        print("\nClassification Summary:")
        for flag, count in summary.items():
            print(f"{flag}: {count}")
            
    finally:
        classifier.cleanup()


if __name__ == "__main__":
    main()