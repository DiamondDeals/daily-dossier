import csv
import json
from datetime import datetime

def convert_csv_to_json():
    """Convert subreddits.csv to subreddit_master.json"""
    
    # Read the CSV file
    subreddits = []
    skipped_lines = 0
    
    print("Reading subreddits.csv...")
    
    with open('subreddits.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            subreddit = row.get('Subreddit', '').strip()
            link = row.get('Link', '').strip()
            
            if subreddit and link:
                subreddits.append({
                    'name': subreddit,
                    'url': link
                })
            else:
                skipped_lines += 1
    
    # Create the JSON structure
    master_json = {
        'meta': {
            'total_count': len(subreddits),
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Reddit subreddit list for Reddit Helper Helper',
            'format_version': '1.0',
            'processing_info': {
                'processed_subreddits': len(subreddits),
                'skipped_lines': skipped_lines
            }
        },
        'subreddits': subreddits
    }
    
    # Write to JSON file
    with open('subreddit_master.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(master_json, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"✅ Conversion complete!")
    print(f"   Total subreddits: {len(subreddits)}")
    print(f"   Skipped lines: {skipped_lines}")
    print(f"   Output file: subreddit_master.json")
    
    # Show first 3 examples
    print("\nFirst 3 subreddits:")
    for i, sub in enumerate(subreddits[:3]):
        print(f"  {i+1}. {sub['name']} -> {sub['url']}")

if __name__ == "__main__":
    try:
        convert_csv_to_json()
    except FileNotFoundError:
        print("❌ Error: subreddits.csv file not found!")
        print("   Make sure the CSV file is in the same folder as this script.")
    except Exception as e:
        print(f"❌ Error: {e}")