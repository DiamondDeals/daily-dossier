#!/usr/bin/env python3
"""
Test the old.reddit.com approach
"""
import requests
from bs4 import BeautifulSoup

def test_old_reddit():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    test_url = "https://old.reddit.com/r/entrepreneur/"
    
    print(f"Testing: {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"Response: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"Title: {soup.title.string if soup.title else 'No title'}")
            
            # Look for description in old reddit format
            selectors = [
                '.sidebar .usertext-body .md p',
                '.sidebar .md p',
                '.sidebar .usertext-body p',
                '.titlebox .usertext-body p'
            ]
            
            description = ""
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    texts = [elem.get_text().strip() for elem in elements[:3]]
                    description = " ".join(texts)
                    print(f"Found with '{selector}': {description[:150]}...")
                    if description:
                        break
            
            if not description:
                # Show what's available
                print("Checking for sidebar content...")
                sidebar = soup.find('div', class_='sidebar')
                if sidebar:
                    print(f"Sidebar text (first 300 chars): {sidebar.get_text()[:300]}...")
                else:
                    print("No sidebar found")
                    
                # Check for titlebox
                titlebox = soup.find('div', class_='titlebox')
                if titlebox:
                    print(f"Titlebox text (first 200 chars): {titlebox.get_text()[:200]}...")
                
            return description
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = test_old_reddit()
    print(f"Final result: {result}")