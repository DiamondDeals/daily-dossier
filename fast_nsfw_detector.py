import csv
import time
import random
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Tuple
from urllib.parse import urljoin

class FastNSFWDetector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Enhanced NSFW detection patterns
        self.nsfw_indicators = {
            'explicit_content': [
                'adult content', 'nsfw', '18+', 'over 18', 'adult only', 'mature content',
                'explicit', 'pornography', 'sexual content', 'nude', 'nudity', 'xxx',
                'not safe for work', 'adults only', 'mature audiences'
            ],
            'sexual_terms': [
                'erotic', 'fetish', 'kink', 'bdsm', 'sex', 'sexual', 'porn', 'masturbation',
                'orgasm', 'arousal', 'intimate', 'sensual', 'seduction', 'adult entertainment'
            ],
            'community_markers': [
                'gonewild', 'hookup', 'dating', 'personals', 'singles', 'meet', 'chat',
                'verification required', 'must verify', 'age verification', 'tribute',
                'rate me', 'am i', 'breeding', 'jerk off'
            ],
            'warning_phrases': [
                'content warning', 'viewer discretion', 'mature theme', 'adult theme',
                'sexual nature', 'graphic content', 'explicit material'
            ]
        }
    
    def get_subreddit_info(self, subreddit_name: str, url: str) -> Tuple[str, bool]:
        """
        Get subreddit description and NSFW status using requests
        """
        try:
            # Try to get the subreddit page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for NSFW indicators in page content
            page_text = soup.get_text().lower()
            
            # Check if subreddit is marked as NSFW
            is_nsfw_marked = any([
                'nsfw' in page_text,
                '18+' in page_text,
                'over 18' in page_text,
                'adult content' in page_text,
                'mature content' in page_text
            ])
            
            # Try to find description
            description = ""
            
            # Multiple selectors to try
            description_selectors = [
                '.subreddit-description',
                '[data-testid="subreddit-sidebar"]',
                '.sidebar .usertext-body',
                '.sidebar-textbox',
                '.description'
            ]
            
            for selector in description_selectors:
                elements = soup.select(selector)
                if elements:
                    text = ' '.join([elem.get_text().strip() for elem in elements])
                    if text and len(text) > 10:
                        description = text[:500]
                        break
            
            # If no description found, look in meta tags
            if not description:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content', '')[:500]
            
            # Fallback to title or any text content
            if not description:
                title = soup.find('title')
                if title:
                    description = title.get_text()[:200]
            
            return description.strip(), is_nsfw_marked
            
        except Exception as e:
            return f"Error fetching: {str(e)[:100]}", False
    
    def detect_nsfw_from_description(self, description: str, is_marked_nsfw: bool) -> Tuple[bool, str, int]:
        """
        Detect NSFW content based on description and page markers
        """
        if is_marked_nsfw:
            return True, "Page explicitly marked as NSFW", 10
        
        if not description or description.startswith("Error fetching"):
            return False, "No description available for analysis", 0
        
        desc_lower = description.lower()
        reasons = []
        confidence = 0
        
        # Check for explicit content markers
        explicit_matches = [term for term in self.nsfw_indicators['explicit_content'] if term in desc_lower]
        if explicit_matches:
            reasons.append(f"Explicit content markers: {', '.join(explicit_matches[:2])}")
            confidence = max(confidence, 9)
        
        # Check for sexual terms
        sexual_matches = [term for term in self.nsfw_indicators['sexual_terms'] if term in desc_lower]
        if sexual_matches:
            reasons.append(f"Sexual terminology: {', '.join(sexual_matches[:2])}")
            confidence = max(confidence, 7)
        
        # Check for community markers
        community_matches = [term for term in self.nsfw_indicators['community_markers'] if term in desc_lower]
        if community_matches:
            reasons.append(f"NSFW community indicators: {', '.join(community_matches[:2])}")
            confidence = max(confidence, 6)
        
        # Check for warning phrases
        warning_matches = [term for term in self.nsfw_indicators['warning_phrases'] if term in desc_lower]
        if warning_matches:
            reasons.append(f"Content warnings: {', '.join(warning_matches[:2])}")
            confidence = max(confidence, 8)
        
        # Multiple indicators boost confidence
        total_matches = len(explicit_matches) + len(sexual_matches) + len(community_matches)
        if total_matches >= 3:
            confidence = max(confidence, 9)
        elif total_matches >= 2:
            confidence = max(confidence, 7)
        
        is_nsfw = confidence >= 6
        reason_text = "; ".join(reasons) if reasons else "No NSFW indicators found"
        
        return is_nsfw, reason_text, confidence
    
    def process_batch(self, input_file: str, output_file: str, start_row: int = 0, batch_size: int = 100):
        """
        Process a batch of subreddits
        """
        processed = 0
        nsfw_count = 0
        
        # Read existing data if output file exists
        existing_data = []
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
                processed = len(existing_data)
                nsfw_count = sum(1 for row in existing_data if row['NSFW_Flag'] == 'YES')
        except FileNotFoundError:
            pass
        
        # Open files
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            all_rows = list(reader)
        
        # Process new batch
        fieldnames = ['Subreddit', 'Link', 'Description', 'NSFW_Flag', 'NSFW_Reason', 'Confidence_Score']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write existing data
            for row in existing_data:
                writer.writerow(row)
            
            # Process new rows
            end_row = min(start_row + batch_size, len(all_rows))
            for i in range(start_row, end_row):
                row = all_rows[i]
                subreddit = row['Subreddit']
                url = row['Link']
                
                print(f"Processing {processed + 1}: {subreddit}")
                
                # Get description and NSFW status
                description, is_marked_nsfw = self.get_subreddit_info(subreddit, url)
                is_nsfw, reason, confidence = self.detect_nsfw_from_description(description, is_marked_nsfw)
                
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
                time.sleep(random.uniform(0.5, 1.5))
        
        return processed, nsfw_count

def main():
    input_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit SubReddits - ALL SUBREDDITS.csv'
    output_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit_SubReddits_With_Descriptions.csv'
    
    detector = FastNSFWDetector()
    
    print("Starting fast NSFW detection with subreddit descriptions...")
    print("Processing first 50 subreddits as test batch...")
    
    try:
        processed, nsfw_count = detector.process_batch(
            input_file, output_file, start_row=0, batch_size=50
        )
        
        print(f"\nBatch completed!")
        print(f"Processed: {processed} subreddits")
        print(f"NSFW found: {nsfw_count}")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()