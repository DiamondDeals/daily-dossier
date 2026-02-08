import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
from typing import Dict, List, Tuple

class SubredditDescriptionScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
        # Enhanced NSFW detection patterns for descriptions
        self.nsfw_indicators = {
            'explicit_content': [
                'adult content', 'nsfw', '18+', 'over 18', 'adult only', 'mature content',
                'explicit', 'pornography', 'sexual content', 'nude', 'nudity', 'xxx'
            ],
            'sexual_terms': [
                'erotic', 'fetish', 'kink', 'bdsm', 'sex', 'sexual', 'porn', 'masturbation',
                'orgasm', 'arousal', 'intimate', 'sensual', 'seduction'
            ],
            'community_markers': [
                'gonewild', 'hookup', 'dating', 'personals', 'singles', 'meet', 'chat',
                'verification required', 'must verify', 'age verification'
            ],
            'body_related': [
                'body', 'curves', 'physique', 'anatomy', 'figure', 'attractive',
                'beautiful', 'gorgeous', 'hot', 'sexy'
            ]
        }
    
    def setup_driver(self):
        """Setup headless Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver initialized successfully")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            raise
    
    def get_subreddit_description(self, subreddit_name: str, url: str) -> str:
        """
        Scrape the description of a subreddit
        """
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try multiple selectors for subreddit description
            description_selectors = [
                '[data-testid="subreddit-sidebar"] p',
                '.sidebar .usertext-body p',
                '.subreddit-description',
                '.sidebar-textbox p',
                '[data-click-id="text"] p',
                '.description p'
            ]
            
            description = ""
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        description = " ".join([elem.text.strip() for elem in elements[:3]])  # First 3 paragraphs
                        if description:
                            break
                except:
                    continue
            
            # Fallback: look for any text that might be a description
            if not description:
                try:
                    # Look for sidebar content
                    sidebar = self.driver.find_element(By.CSS_SELECTOR, '[role="complementary"], .sidebar')
                    text_content = sidebar.text.strip()
                    
                    # Extract first meaningful paragraph
                    lines = text_content.split('\n')
                    for line in lines:
                        if len(line) > 20 and not line.isupper():  # Skip short lines and headers
                            description = line
                            break
                except:
                    pass
            
            # Clean up description
            if description:
                description = re.sub(r'\s+', ' ', description).strip()
                description = description[:500]  # Limit length
            
            return description if description else "No description found"
            
        except TimeoutException:
            return "Timeout loading page"
        except Exception as e:
            return f"Error: {str(e)[:100]}"
    
    def detect_nsfw_from_description(self, description: str) -> Tuple[bool, str, int]:
        """
        Detect NSFW content based on description text
        """
        if not description or description in ["No description found", "Timeout loading page"]:
            return False, "No description available", 0
        
        desc_lower = description.lower()
        reasons = []
        confidence = 0
        
        # Check for explicit content markers
        explicit_count = 0
        for term in self.nsfw_indicators['explicit_content']:
            if term in desc_lower:
                explicit_count += 1
                if explicit_count == 1:
                    reasons.append("Contains explicit content markers")
                confidence = max(confidence, 9)
        
        # Check for sexual terms
        sexual_count = 0
        for term in self.nsfw_indicators['sexual_terms']:
            if term in desc_lower:
                sexual_count += 1
                if sexual_count == 1:
                    reasons.append("Contains sexual terminology")
                confidence = max(confidence, 7)
        
        # Check for community markers
        community_count = 0
        for term in self.nsfw_indicators['community_markers']:
            if term in desc_lower:
                community_count += 1
                if community_count == 1:
                    reasons.append("Contains NSFW community indicators")
                confidence = max(confidence, 6)
        
        # Check for body-related terms (lower confidence)
        body_count = 0
        for term in self.nsfw_indicators['body_related']:
            if term in desc_lower:
                body_count += 1
                if body_count == 1:
                    reasons.append("Contains body-related terms")
                confidence = max(confidence, 4)
        
        # Age restrictions mentioned
        if any(term in desc_lower for term in ['18+', 'over 18', 'must be 18', 'adult only']):
            reasons.append("Age restrictions mentioned")
            confidence = max(confidence, 8)
        
        # Multiple indicators boost confidence
        total_indicators = explicit_count + sexual_count + community_count
        if total_indicators >= 2:
            confidence = max(confidence, 8)
        
        is_nsfw = confidence >= 6  # Higher threshold for description-based detection
        reason_text = "; ".join(reasons) if reasons else "No NSFW indicators in description"
        
        return is_nsfw, reason_text, confidence
    
    def process_subreddits_with_descriptions(self, input_file: str, output_file: str, max_subreddits: int = None):
        """
        Process subreddits, fetch descriptions, and classify NSFW status
        """
        processed = 0
        nsfw_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Add new columns for description and updated classification
            fieldnames = ['Subreddit', 'Link', 'Description', 'NSFW_Flag', 'NSFW_Reason', 'Confidence_Score']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    if max_subreddits and processed >= max_subreddits:
                        break
                    
                    subreddit = row['Subreddit']
                    url = row['Link']
                    
                    print(f"Processing {processed + 1}: {subreddit}")
                    
                    # Get description
                    description = self.get_subreddit_description(subreddit, url)
                    
                    # Classify based on description
                    is_nsfw, reason, confidence = self.detect_nsfw_from_description(description)
                    
                    # Write to output
                    output_row = {
                        'Subreddit': subreddit,
                        'Link': url,
                        'Description': description,
                        'NSFW_Flag': 'YES' if is_nsfw else 'NO',
                        'NSFW_Reason': reason,
                        'Confidence_Score': confidence
                    }
                    writer.writerow(output_row)
                    
                    if is_nsfw:
                        nsfw_count += 1
                    
                    processed += 1
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                    # Progress update
                    if processed % 100 == 0:
                        print(f"Processed {processed} subreddits. NSFW found: {nsfw_count}")
        
        return processed, nsfw_count
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    # Start with a smaller batch for testing
    input_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit SubReddits - ALL SUBREDDITS.csv'
    output_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit_SubReddits_With_Descriptions.csv'
    
    scraper = SubredditDescriptionScraper()
    
    try:
        print("Starting subreddit description scraping and NSFW classification...")
        print("Processing first 1000 subreddits as test batch...")
        
        processed, nsfw_count = scraper.process_subreddits_with_descriptions(
            input_file, output_file, max_subreddits=1000
        )
        
        print(f"\nCompleted!")
        print(f"Processed: {processed} subreddits")
        print(f"NSFW found: {nsfw_count}")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()