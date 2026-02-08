#!/usr/bin/env python3
"""
Quick test to debug the scraper and see what's actually happening
"""
import requests
from bs4 import BeautifulSoup
import csv
import time

def test_single_subreddit():
    """Test scraping a single subreddit to see if it works"""
    print("Testing single subreddit scraping...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Test with a known subreddit
    test_url = "https://www.reddit.com/r/entrepreneur/"
    
    try:
        print(f"Fetching: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Try to find description
            description_selectors = [
                '[data-testid="subreddit-sidebar"] p',
                '.sidebar .usertext-body p',
                '.subreddit-description',
                '.sidebar-textbox p',
                '[data-click-id="text"] p',
                '.description p',
                '.sidebar .md p'
            ]
            
            description = ""
            for selector in description_selectors:
                elements = soup.select(selector)
                if elements:
                    texts = [elem.get_text().strip() for elem in elements[:3]]
                    description = " ".join(texts)
                    print(f"Found description with selector '{selector}': {description[:100]}...")
                    if description:
                        break
            
            if not description:
                print("No description found with standard selectors")
                # Try to find any text content
                all_text = soup.get_text()
                print(f"Page text length: {len(all_text)} characters")
                print(f"First 500 chars: {all_text[:500]}...")
            
            return description
        else:
            print(f"Failed to fetch page: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_csv_loading():
    """Test loading the CSV file"""
    print("\nTesting CSV file loading...")
    
    csv_file = "Subreddits/Reddit SubReddits - ALL SUBREDDITS.csv"
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"CSV loaded successfully: {len(rows)} rows")
            
            # Show first few rows
            for i, row in enumerate(rows[:5]):
                print(f"Row {i}: {row}")
                
            return rows
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def test_scraping_batch():
    """Test scraping first 5 subreddits from CSV"""
    print("\nTesting batch scraping...")
    
    rows = test_csv_loading()
    if not rows:
        return
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for i, row in enumerate(rows[:5]):
        if 'Subreddit' not in row or 'Link' not in row:
            print(f"Row {i}: Missing required columns")
            continue
            
        subreddit = row['Subreddit']
        url = row['Link']
        
        print(f"\n--- Processing {i+1}/5: r/{subreddit} ---")
        print(f"URL: {url}")
        
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            fetch_time = time.time() - start_time
            
            print(f"Response: {response.status_code} ({fetch_time:.2f}s)")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find description
                description = ""
                description_selectors = [
                    '[data-testid="subreddit-sidebar"] p',
                    '.sidebar .usertext-body p',
                    '.subreddit-description',
                    '.sidebar-textbox p'
                ]
                
                for selector in description_selectors:
                    elements = soup.select(selector)
                    if elements:
                        texts = [elem.get_text().strip() for elem in elements[:2]]
                        description = " ".join(texts)
                        if description:
                            break
                
                if description:
                    print(f"Description: {description[:200]}...")
                else:
                    print("No description found")
                    
            else:
                print(f"Failed to fetch: HTTP {response.status_code}")
                
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing {subreddit}: {e}")

if __name__ == "__main__":
    print("=== Reddit Scraper Debug Test ===")
    
    # Test 1: Single subreddit
    test_single_subreddit()
    
    # Test 2: CSV loading
    test_csv_loading()
    
    # Test 3: Batch scraping
    test_scraping_batch()
    
    print("\n=== Debug test complete ===")