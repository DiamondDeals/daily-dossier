import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.reddit.com/best/communities/{}/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_FILE = "subreddits.csv"

def extract_subreddits(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    links = soup.find_all('a', href=True)
    subreddits = set()

    for link in links:
        href = link['href']
        text = link.text.strip()

        if href.startswith("/r/") and text.startswith("r/") and href == link.get("id", ""):
            name = text.replace("r/", "")
            full_url = f"https://www.reddit.com{href}"
            subreddits.add((name, full_url))

    return subreddits

def scrape_pages():
    page = 1
    all_subreddits = set()

    try:
        while True:
            url = BASE_URL.format(page)
            print(f"🔎 Scraping page {page}: {url}")

            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"⚠️ Page {page} failed to load (status {response.status_code})")
                break

            subs = extract_subreddits(response.text)
            new_subs = subs - all_subreddits

            if not new_subs:
                print("✅ No new subreddits found. Finished.")
                break

            print(f"➕ Found {len(new_subs)} new subreddits.")
            all_subreddits.update(new_subs)
            page += 1
            time.sleep(1)  # Be respectful to Reddit servers

    except KeyboardInterrupt:
        print("\n🛑 Scraper stopped manually. Saving what we have...")

    return sorted(all_subreddits)

def save_to_csv(subreddits):
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Subreddit', 'Link'])
        for name, link in subreddits:
            writer.writerow([name, link])
    print(f"✅ Saved {len(subreddits)} subreddits to {OUTPUT_FILE}")

if __name__ == "__main__":
    data = scrape_pages()
    save_to_csv(data)
