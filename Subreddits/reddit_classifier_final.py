#!/usr/bin/env python3
"""
Reddit Subreddit NSFW Classifier - Final Version
Uses requests + BeautifulSoup for reliable description scraping.
"""

import csv
import requests
import time
import re
import os
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Optional
import random
import json


class FinalRedditClassifier:
    """Final Reddit subreddit NSFW classifier using requests and BeautifulSoup."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.nsfw_keywords = self.load_nsfw_keywords()
        self.safe_keywords = self.load_safe_keywords()
        
    def load_nsfw_keywords(self) -> List[str]:
        """Load comprehensive NSFW detection keywords."""
        return [
            # Explicit content
            'porn', 'nsfw', 'adult', 'sex', 'nude', 'naked', 'xxx', 'gonewild',
            'fetish', 'kink', 'bdsm', 'hentai', 'erotic', 'sexual', 'amateur',
            'milf', 'mature', 'boobs', 'tits', 'ass', 'dick', 'cock', 'pussy',
            'cumshot', 'blowjob', 'anal', 'orgasm', 'masturbation', 'hardcore',
            
            # Suggestive content
            'curves', 'bikini', 'lingerie', 'cleavage', 'upskirt', 'thong',
            'revealing', 'seductive', 'provocative', 'sensual', 'intimate',
            'slutty', 'sexy', 'hot', 'naughty', 'wild', 'bare', 'exposed',
            
            # Adult services/content  
            'escort', 'cam', 'onlyfans', 'premium', 'tribute', 'rate me',
            'selling', 'custom', 'private', 'snapchat', 'dirty', 'horny',
            'hookup', 'fwb', 'sugar', 'daddy', 'meetup', 'sexting',
            
            # Age/content markers
            '18+', '18 plus', 'adults only', 'mature audience', 'not safe for work',
            'over 18', 'nsfw content', '21+', 'adult content', 'explicit',
            
            # Body-focused terms
            'titties', 'breasts', 'nipples', 'vagina', 'penis', 'genitals',
            'butt', 'chest', 'body', 'physique', 'figure', 'topless'
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
            'nonprofit', 'charity', 'volunteer', 'educational', 'wholesome',
            'family-friendly', 'clean', 'appropriate', 'respectful'
        ]
        
    def get_subreddit_info(self, subreddit_name: str) -> tuple[Optional[str], bool]:
        """Get subreddit info using both API and web scraping."""
        
        # Try Reddit JSON API first
        api_url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
        
        try:
            print(f"  Fetching API data for r/{subreddit_name}...")
            response = self.session.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data']:
                    subreddit_data = data['data']
                    
                    # Get description
                    description = subreddit_data.get('public_description', '') or subreddit_data.get('description', '')
                    title = subreddit_data.get('title', '')
                    display_name = subreddit_data.get('display_name', subreddit_name)
                    subscribers = subreddit_data.get('subscribers', 0)
                    over_18 = subreddit_data.get('over18', False)
                    
                    # Combine info
                    full_description = f"{display_name}"
                    if title and title != display_name:
                        full_description += f" - {title}"
                    if description:
                        full_description += f" | {description}"
                    if subscribers > 0:
                        full_description += f" | Subscribers: {subscribers:,}"
                        
                    return full_description, over_18
                    
        except Exception as e:
            print(f"    API error for r/{subreddit_name}: {e}")
            
        # Fallback to web scraping
        return self.scrape_subreddit_web(subreddit_name), False
        
    def scrape_subreddit_web(self, subreddit_name: str) -> Optional[str]:
        """Fallback web scraping method."""
        url = f"https://www.reddit.com/r/{subreddit_name}/"
        
        try:
            print(f"  Web scraping r/{subreddit_name}...")
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                description_parts = []
                
                # Try to find title
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.text.strip()
                    if title_text and 'reddit' not in title_text.lower():
                        description_parts.append(title_text)
                
                # Try meta description
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    description_parts.append(meta_desc['content'])
                    
                # Try OpenGraph description
                og_desc = soup.find('meta', {'property': 'og:description'})
                if og_desc and og_desc.get('content'):
                    description_parts.append(og_desc['content'])
                
                if description_parts:
                    return " | ".join(description_parts[:2])  # Combine first 2 parts
                    
        except Exception as e:
            print(f"    Web scraping error for r/{subreddit_name}: {e}")
            
        return None
        
    def analyze_nsfw_content(self, description: str, subreddit_name: str, over_18: bool = False) -> Dict:
        """Comprehensive NSFW content analysis."""
        
        # If Reddit marks it as over 18, it's definitely NSFW
        if over_18:
            return {
                'nsfw_flag': 'YES',
                'reason': 'Marked as Over 18+ by Reddit',
                'confidence': 10,
                'keywords_found': ['over18_flag']
            }
            
        if not description:
            return {
                'nsfw_flag': 'UNKNOWN',
                'reason': 'No description available for analysis',
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
                
        # NSFW regex patterns
        nsfw_patterns = [
            (r'\b(18\+|18 plus|21\+|adults? only|mature audience)\b', 'age_restriction'),
            (r'\b(nsfw|not safe for work)\b', 'nsfw_explicit'),
            (r'\b(selling|custom|premium)\s+(content|pics?|videos?|photos?)\b', 'selling_content'),
            (r'\b(rate\s*me|tribute)\b', 'rating_content'),
            (r'\b(cam|onlyfans|premium\s*snap)\b', 'adult_platforms'),
            (r'\b(gone\s*wild|real\s*girls?)\b', 'adult_communities'),
            (r'\b(nude|naked|xxx|porn)\b', 'explicit_terms'),
            (r'\b(hookup|fwb|sugar\s*daddy)\b', 'dating_adult'),
            (r'\b(fetish|kink|bdsm)\b', 'fetish_content')
        ]
        
        pattern_matches = []
        pattern_types = []
        for pattern, pattern_type in nsfw_patterns:
            matches = re.findall(pattern, combined_text)
            if matches:
                pattern_matches.extend([match if isinstance(match, str) else match[0] for match in matches])
                pattern_types.append(pattern_type)
                
        # Subreddit name analysis
        high_risk_name_indicators = [
            'gone', 'wild', 'nude', 'nsfw', 'xxx', 'porn', 'sex', 'adult',
            'real', 'amateur', 'milf', 'teen', 'ass', 'tits', 'boobs', 'curves'
        ]
        
        medium_risk_name_indicators = [
            'girls', 'ladies', 'babes', 'hotties', 'rate', 'tribute', 'selfie',
            'cute', 'beautiful', 'gorgeous', 'sexy', 'hot'
        ]
        
        high_risk_name_matches = []
        medium_risk_name_matches = []
        
        for indicator in high_risk_name_indicators:
            if indicator in subreddit_lower:
                high_risk_name_matches.append(indicator)
                
        for indicator in medium_risk_name_indicators:
            if indicator in subreddit_lower and indicator not in high_risk_name_matches:
                medium_risk_name_matches.append(indicator)
        
        # Calculate confidence scores
        content_score = len(nsfw_matches) * 2
        pattern_score = len(pattern_matches) * 4
        high_risk_name_score = len(high_risk_name_matches) * 5
        medium_risk_name_score = len(medium_risk_name_matches) * 2
        safe_score = len(safe_matches)
        
        total_nsfw_score = content_score + pattern_score + high_risk_name_score + medium_risk_name_score
        
        # Enhanced classification logic
        all_indicators = nsfw_matches + pattern_matches + high_risk_name_matches + medium_risk_name_matches
        
        if total_nsfw_score >= 10 or pattern_score >= 8 or high_risk_name_score >= 5:
            classification = 'YES'
            reason = f"High confidence NSFW: {', '.join(all_indicators[:5])}"
            confidence = min(10, total_nsfw_score)
            
        elif total_nsfw_score >= 6 or high_risk_name_score >= 3 or pattern_score >= 4:
            classification = 'MAYBE'
            reason = f"Likely NSFW content: {', '.join(all_indicators[:4])}"
            confidence = min(8, total_nsfw_score)
            
        elif safe_score >= 4 and total_nsfw_score <= 2:
            classification = 'NO'
            reason = f"Safe content indicators: {', '.join(safe_matches[:3])}"
            confidence = 0
            
        elif safe_score >= 2 and total_nsfw_score <= 1:
            classification = 'NO'
            reason = f"Appears safe: {', '.join(safe_matches[:2])}"
            confidence = 0
            
        else:
            classification = 'UNKNOWN'
            if total_nsfw_score > 0:
                reason = f"Ambiguous content, some indicators: {', '.join(all_indicators[:3])}"
            else:
                reason = "Insufficient information for reliable classification"
            confidence = total_nsfw_score
            
        return {
            'nsfw_flag': classification,
            'reason': reason,
            'confidence': confidence,
            'keywords_found': all_indicators
        }
        
    def process_subreddits(self, input_file: str, output_file: str):
        """Process all subreddits from CSV file."""
        results = []
        processed_count = 0
        errors = []
        
        # Read input CSV
        print(f"Reading subreddits from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            subreddits = list(reader)
            
        total_count = len(subreddits)
        print(f"Found {total_count} subreddits to process\n")
        
        for row in subreddits:
            subreddit_name = row['Subreddit']
            processed_count += 1
            
            print(f"[{processed_count}/{total_count}] Processing r/{subreddit_name}")
            
            try:
                # Get description and over18 flag
                description, over_18 = self.get_subreddit_info(subreddit_name)
                
                # Analyze for NSFW
                analysis = self.analyze_nsfw_content(description, subreddit_name, over_18)
                
                # Create result
                result_row = {
                    'Subreddit': subreddit_name,
                    'Link': f'https://www.reddit.com/r/{subreddit_name}/',
                    'Description': description or 'No description found',
                    'NSFW_Flag': analysis['nsfw_flag'],
                    'NSFW_Reason': analysis['reason'],
                    'Confidence_Score': analysis['confidence'],
                    'Keywords_Found': ', '.join(analysis['keywords_found'][:10])  # Limit to first 10
                }
                
                results.append(result_row)
                print(f"  Result: {analysis['nsfw_flag']} (confidence: {analysis['confidence']})")
                
            except Exception as e:
                print(f"  Error processing r/{subreddit_name}: {e}")
                errors.append(f"r/{subreddit_name}: {e}")
                
                # Add error entry
                results.append({
                    'Subreddit': subreddit_name,
                    'Link': f'https://www.reddit.com/r/{subreddit_name}/',
                    'Description': f'Error: {e}',
                    'NSFW_Flag': 'ERROR',
                    'NSFW_Reason': f'Processing error: {e}',
                    'Confidence_Score': 0,
                    'Keywords_Found': ''
                })
                
            # Save progress every 100 subreddits
            if processed_count % 100 == 0:
                self.save_results(results, output_file)
                print(f"\n*** Progress saved: {processed_count}/{total_count} ***\n")
                
            # Rate limiting
            time.sleep(random.uniform(1.5, 3.0))
            
        # Final save
        self.save_results(results, output_file)
        
        # Print summary
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Total processed: {processed_count}/{total_count}")
        if errors:
            print(f"Errors encountered: {len(errors)}")
            
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
        print(f"\nCreating separate files from: {classified_file}")
        
        df = pd.read_csv(classified_file)
        
        # NSFW file (YES and MAYBE)
        nsfw_df = df[df['NSFW_Flag'].isin(['YES', 'MAYBE'])].copy()
        nsfw_file = classified_file.replace('.csv', '_NSFW.csv')
        nsfw_df.to_csv(nsfw_file, index=False)
        print(f"✓ NSFW file created: {nsfw_file} ({len(nsfw_df)} subreddits)")
        
        # Safe file (NO only)
        safe_df = df[df['NSFW_Flag'] == 'NO'].copy()
        safe_file = classified_file.replace('.csv', '_SAFE.csv')
        safe_df.to_csv(safe_file, index=False)
        print(f"✓ Safe file created: {safe_file} ({len(safe_df)} subreddits)")
        
        # Statistics
        summary = df['NSFW_Flag'].value_counts()
        print(f"\n=== CLASSIFICATION SUMMARY ===")
        total = len(df)
        for flag, count in summary.items():
            percentage = (count / total) * 100
            print(f"{flag:>8}: {count:>5} ({percentage:5.1f}%)")
        print(f"{'TOTAL':>8}: {total:>5}")
        
        return nsfw_file, safe_file


def main():
    """Main execution function."""
    print("=== Reddit NSFW Classifier - Final Version ===\n")
    
    classifier = FinalRedditClassifier()
    
    try:
        # File paths
        input_file = "Reddit SubReddits - ALL SUBREDDITS.csv"
        output_file = "Reddit_SubReddits_Classified_Final.csv"
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"ERROR: Input file '{input_file}' not found!")
            print("Please make sure the file exists in the current directory.")
            return
            
        # Process subreddits
        results = classifier.process_subreddits(input_file, output_file)
        
        # Create separate files
        nsfw_file, safe_file = classifier.create_separate_files(output_file)
        
        print(f"\n🎉 CLASSIFICATION COMPLETED! 🎉")
        print(f"📁 Main file: {output_file}")
        print(f"🔞 NSFW file: {nsfw_file}")
        print(f"✅ Safe file: {safe_file}")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()