#!/usr/bin/env python3
"""
Reddit Subreddit NSFW Classifier
Uses Selenium to scrape subreddit descriptions for accurate classification.
"""

import csv
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from typing import Dict, List, Optional
import random


class RedditNSFWClassifier:
    """Reddit subreddit NSFW classifier using Selenium for description scraping."""
    
    def __init__(self):
        self.setup_selenium()
        self.nsfw_keywords = self.load_nsfw_keywords()
        self.safe_keywords = self.load_safe_keywords()
        
    def setup_selenium(self):
        """Initialize headless Chrome driver with proper setup."""
        print("Setting up Chrome driver...")
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--accept-language=en-US,en;q=0.9')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 15)
            print("Chrome driver initialized successfully")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            raise
        
    def load_nsfw_keywords(self) -> List[str]:
        """Load comprehensive NSFW detection keywords."""
        return [
            # Explicit content
            'porn', 'nsfw', 'adult', 'sex', 'nude', 'naked', 'xxx', 'gonewild',
            'fetish', 'kink', 'bdsm', 'hentai', 'erotic', 'sexual', 'amateur',
            'milf', 'mature', 'boobs', 'tits', 'ass', 'dick', 'cock', 'pussy',
            'cumshot', 'blowjob', 'anal', 'orgasm', 'masturbation',
            
            # Suggestive content
            'curves', 'bikini', 'lingerie', 'cleavage', 'upskirt', 'thong',
            'revealing', 'seductive', 'provocative', 'sensual', 'intimate',
            'slutty', 'sexy', 'hot', 'naughty', 'wild', 'bare', 'exposed',
            
            # Adult services/content
            'escort', 'cam', 'onlyfans', 'premium', 'tribute', 'rate me',
            'selling', 'custom', 'private', 'snapchat', 'dirty', 'horny',
            'hookup', 'fwb', 'sugar', 'daddy', 'meetup',
            
            # Age/content markers
            '18+', '18 plus', 'adults only', 'mature audience', 'not safe for work',
            'over 18', 'nsfw content', '21+', 'adult content',
            
            # Body-focused terms
            'titties', 'breasts', 'nipples', 'vagina', 'penis', 'genitals',
            'butt', 'chest', 'body', 'physique', 'figure'
        ]
        
    def load_safe_keywords(self) -> List[str]:
        """Load keywords indicating safe/educational content."""
        return [
            'help', 'support', 'community', 'discussion', 'advice', 'tips',
            'learning', 'education', 'tutorial', 'guide', 'news', 'information',
            'technology', 'science', 'art', 'music', 'gaming', 'sports',
            'food', 'cooking', 'travel', 'photography', 'books', 'movies',
            'fitness', 'health', 'business', 'career', 'finance', 'investing',
            'diy', 'crafts', 'gardening', 'pets', 'family', 'parenting',
            'academic', 'research', 'professional', 'official', 'government',
            'nonprofit', 'charity', 'volunteer', 'educational', 'wholesome'
        ]
        
    def get_subreddit_description(self, subreddit_name: str) -> Optional[str]:
        """Scrape subreddit description using Selenium."""
        url = f"https://www.reddit.com/r/{subreddit_name}/"
        
        try:
            print(f"  Scraping description for r/{subreddit_name}...")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            description_text = ""
            
            # Multiple selectors to try for description
            description_selectors = [
                # New Reddit selectors
                '[data-testid="subreddit-about-card"] div[data-testid="subreddit-about-card-description"]',
                '[data-testid="subreddit-about-card"] p',
                '[data-testid="community-highlight-card"] p',
                'div[data-adclicklocation="subreddit_about"] p',
                
                # Old Reddit selectors
                '.side .usertext-body .md p',
                '.titlebox .usertext-body .md p',
                '.subreddit-description p',
                '.sidebar .md p',
                
                # General selectors
                '.community-description p',
                '.subreddit-about p',
                '[role="complementary"] p'
            ]
            
            # Try each selector
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        paragraphs = []
                        for elem in elements[:3]:  # First 3 paragraphs
                            text = elem.text.strip()
                            if text and len(text) > 10:  # Meaningful content
                                paragraphs.append(text)
                        
                        if paragraphs:
                            description_text = " | ".join(paragraphs)
                            break
                except Exception as e:
                    continue
                    
            # If no description found, try getting title/header info
            if not description_text:
                try:
                    title_selectors = [
                        'h1[data-testid="subreddit-header-display-name"]',
                        'h1._19JhaP1slDQqu2XgT3vVS0',
                        '.subreddit-header h1',
                        'h1'
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if title_elem:
                                description_text = f"r/{subreddit_name} - {title_elem.text}"
                                break
                        except:
                            continue
                            
                except Exception as e:
                    pass
                    
            return description_text.strip() if description_text else None
            
        except Exception as e:
            print(f"    Error scraping r/{subreddit_name}: {e}")
            return None
            
    def analyze_nsfw_content(self, description: str, subreddit_name: str) -> Dict:
        """Analyze description and subreddit name for NSFW content."""
        if not description:
            return {
                'nsfw_flag': 'UNKNOWN',
                'reason': 'No description available',
                'confidence': 0,
                'keywords_found': []
            }
            
        description_lower = description.lower()
        subreddit_lower = subreddit_name.lower()
        combined_text = f"{description_lower} {subreddit_lower}"
        
        # Find NSFW keywords
        nsfw_matches = []
        for keyword in self.nsfw_keywords:
            if keyword in combined_text:
                nsfw_matches.append(keyword)
                
        # Find safe keywords
        safe_matches = []
        for keyword in self.safe_keywords:
            if keyword in description_lower:
                safe_matches.append(keyword)
                
        # NSFW patterns
        nsfw_patterns = [
            r'\b(18\+|18 plus|21\+|adults? only|mature audience)\b',
            r'\b(nsfw|not safe for work)\b',
            r'\b(selling|custom|premium)\s+(content|pics?|videos?|photos?)\b',
            r'\b(rate\s*me|tribute)\b',
            r'\b(cam|onlyfans|premium\s*snap)\b',
            r'\b(gone\s*wild|real\s*girls?)\b',
            r'\b(nude|naked|xxx)\b',
            r'\b(hookup|fwb|sugar\s*daddy)\b'
        ]
        
        pattern_matches = []
        for pattern in nsfw_patterns:
            matches = re.findall(pattern, combined_text)
            if matches:
                pattern_matches.extend([match if isinstance(match, str) else match[0] for match in matches])
                
        # Special subreddit name analysis
        subreddit_nsfw_indicators = [
            'gone', 'wild', 'nude', 'nsfw', 'xxx', 'porn', 'sex', 'adult',
            'girls', 'ladies', 'babes', 'hotties', 'rate', 'tribute', 'real',
            'amateur', 'milf', 'teen', 'curves', 'ass', 'tits', 'boobs'
        ]
        
        name_matches = []
        for indicator in subreddit_nsfw_indicators:
            if indicator in subreddit_lower:
                name_matches.append(indicator)
        
        # Calculate confidence scores
        content_nsfw_score = len(nsfw_matches) * 2
        pattern_score = len(pattern_matches) * 4
        name_score = len(name_matches) * 3
        safe_score = len(safe_matches)
        
        total_nsfw_score = content_nsfw_score + pattern_score + name_score
        
        # Classification logic
        if total_nsfw_score >= 8 or pattern_score >= 4:
            classification = 'YES'
            all_indicators = nsfw_matches + pattern_matches + name_matches
            reason = f"Strong NSFW indicators: {', '.join(all_indicators[:5])}"
            confidence = min(10, total_nsfw_score)
            
        elif total_nsfw_score >= 4 or name_score >= 3:
            classification = 'MAYBE'
            all_indicators = nsfw_matches + name_matches
            reason = f"Possible NSFW content: {', '.join(all_indicators[:3])}"
            confidence = total_nsfw_score
            
        elif safe_score >= 3 and total_nsfw_score <= 1:
            classification = 'NO' 
            reason = f"Safe content indicators: {', '.join(safe_matches[:3])}"
            confidence = 0
            
        else:
            classification = 'UNKNOWN'
            reason = "Insufficient information for reliable classification"
            confidence = total_nsfw_score
            
        return {
            'nsfw_flag': classification,
            'reason': reason,
            'confidence': confidence,
            'keywords_found': nsfw_matches + pattern_matches + name_matches
        }
        
    def process_subreddits(self, input_file: str, output_file: str):
        """Process subreddits from CSV file."""
        results = []
        processed_count = 0
        
        # Read input CSV
        print(f"Reading subreddits from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            subreddits = list(reader)
            
        total_count = len(subreddits)
        print(f"Found {total_count} subreddits to process")
        
        for row in subreddits:
            subreddit_name = row['Subreddit']
            processed_count += 1
            print(f"Processing {processed_count}/{total_count}: r/{subreddit_name}")
            
            # Get description
            description = self.get_subreddit_description(subreddit_name)
            
            # Analyze for NSFW
            analysis = self.analyze_nsfw_content(description, subreddit_name)
            
            # Create result
            result_row = {
                'Subreddit': subreddit_name,
                'Link': f'https://www.reddit.com/r/{subreddit_name}/',
                'Description': description or 'No description found',
                'NSFW_Flag': analysis['nsfw_flag'],
                'NSFW_Reason': analysis['reason'],
                'Confidence_Score': analysis['confidence'],
                'Keywords_Found': ', '.join(analysis['keywords_found'])
            }
            
            results.append(result_row)
            
            # Save progress every 50 subreddits
            if processed_count % 50 == 0:
                self.save_results(results, output_file)
                print(f"  Progress saved: {processed_count}/{total_count}")
                
            # Rate limiting between requests
            time.sleep(random.uniform(2, 4))
            
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
            'NSFW_Reason', 'Confidence_Score', 'Keywords_Found'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    def create_separate_files(self, classified_file: str):
        """Create separate NSFW and Safe CSV files."""
        print(f"Creating separate files from {classified_file}...")
        
        df = pd.read_csv(classified_file)
        
        # NSFW file (YES and MAYBE)
        nsfw_df = df[df['NSFW_Flag'].isin(['YES', 'MAYBE'])]
        nsfw_file = classified_file.replace('.csv', '_NSFW.csv')
        nsfw_df.to_csv(nsfw_file, index=False)
        print(f"Created NSFW file with {len(nsfw_df)} subreddits: {nsfw_file}")
        
        # Safe file (NO)
        safe_df = df[df['NSFW_Flag'] == 'NO']
        safe_file = classified_file.replace('.csv', '_SAFE.csv')
        safe_df.to_csv(safe_file, index=False)
        print(f"Created Safe file with {len(safe_df)} subreddits: {safe_file}")
        
        # Statistics
        summary = df['NSFW_Flag'].value_counts()
        print("\nClassification Summary:")
        for flag, count in summary.items():
            percentage = (count / len(df)) * 100
            print(f"  {flag}: {count} ({percentage:.1f}%)")
            
        return nsfw_file, safe_file
        
    def cleanup(self):
        """Close browser and cleanup resources."""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {e}")


def main():
    """Main execution function."""
    classifier = None
    
    try:
        print("Starting Reddit NSFW Classifier...")
        classifier = RedditNSFWClassifier()
        
        # File paths
        input_file = "Reddit SubReddits - ALL SUBREDDITS.csv"
        output_file = "Reddit_SubReddits_Classified.csv"
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found!")
            return
            
        # Process subreddits
        results = classifier.process_subreddits(input_file, output_file)
        
        # Create separate files
        nsfw_file, safe_file = classifier.create_separate_files(output_file)
        
        print(f"\nClassification completed!")
        print(f"Main file: {output_file}")
        print(f"NSFW file: {nsfw_file}")
        print(f"Safe file: {safe_file}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        
    finally:
        if classifier:
            classifier.cleanup()


if __name__ == "__main__":
    main()