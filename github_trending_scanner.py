#!/usr/bin/env python3
"""
GitHub Trending Scanner - Daily dossier scanner #7
Finds trending repos in AI, SaaS, and dev tools created or active in the last week.
Runs as subprocess, prints formatted output to stdout.
"""

import sys
import io
import requests
import time
import os
from datetime import datetime, timedelta

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GITHUB_API = "https://api.github.com/search/repositories"
HEADERS = {}

# Use token if available for higher rate limits
token = os.environ.get('GITHUB_TOKEN')
if token:
    HEADERS['Authorization'] = f'token {token}'

# Topic keyword groups (kept short to avoid GitHub 422 query complexity limit)
TOPICS = {
    'ai': 'llm OR gpt OR ai-tools OR langchain',
    'ai2': 'machine-learning OR agents OR ai',
    'saas': 'saas OR boilerplate OR template OR indie-hacking',
    'devtools': 'automation OR cli OR developer-tools OR scraping',
}

def search_repos(query, per_page=30):
    """Search GitHub repositories with rate limit handling."""
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': per_page
    }
    try:
        response = requests.get(GITHUB_API, params=params, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json().get('items', [])
        elif response.status_code == 403:
            print("  Rate limited, waiting 60s...", flush=True)
            time.sleep(60)
            return search_repos(query, per_page)
    except Exception as e:
        print(f"  Error: {e}", flush=True)
    return []

def score_repo(repo):
    """Score a repo favoring new breakout repos over established giants.

    Uses log-scaled stars so a 200-star new repo can outrank a 100k-star giant.
    Heavy recency bonus rewards repos created in the last few days.
    """
    import math
    stars = repo.get('stargazers_count', 0)
    forks = repo.get('forks_count', 0)

    # Log scale: 100 stars = 4.6, 1000 = 6.9, 100k = 11.5 (diminishing returns)
    score = math.log1p(stars) * 10 + math.log1p(forks) * 5

    created = repo.get('created_at', '')
    if created:
        try:
            created_dt = datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ')
            age_days = (datetime.utcnow() - created_dt).days
            if age_days <= 1:
                score += 200
            elif age_days <= 3:
                score += 150
            elif age_days <= 7:
                score += 100
            elif age_days <= 14:
                score += 50
            elif age_days <= 30:
                score += 20
        except ValueError:
            pass

    return score

def run_scanner():
    """Run all queries, dedup, score, and print top 10."""
    now = datetime.utcnow()
    seven_days_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    two_days_ago = (now - timedelta(days=2)).strftime('%Y-%m-%d')

    queries = []
    # New breakout repos per topic (created in last 7 days, 20+ stars)
    for label, topics in TOPICS.items():
        queries.append(f'stars:>20 created:>{seven_days_ago} {topics}')

    # Active popular repos with recent pushes (per topic to avoid query length limit)
    for label, topics in TOPICS.items():
        queries.append(f'stars:>100 pushed:>{two_days_ago} {topics}')

    # Collect and dedup
    seen = {}
    for query in queries:
        repos = search_repos(query, per_page=15)
        for repo in repos:
            full_name = repo.get('full_name', '')
            if not full_name:
                continue
            s = score_repo(repo)
            if full_name not in seen or s > seen[full_name]['_score']:
                seen[full_name] = repo
                seen[full_name]['_score'] = s
        time.sleep(2)  # Stay well within rate limits

    # Sort by score, take top 10
    ranked = sorted(seen.values(), key=lambda r: r.get('_score', 0), reverse=True)[:10]

    if not ranked:
        print("No trending repos found.")
        return

    for i, repo in enumerate(ranked, 1):
        name = repo.get('full_name', '')
        desc = repo.get('description', '') or 'No description'
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        lang = repo.get('language', '') or 'Unknown'
        topics = repo.get('topics', [])
        url = repo.get('html_url', '')

        tags = ', '.join(topics[:5]) if topics else 'none'

        print(f"{i}. {name}")
        print(f"   \U0001f4dd {desc}")
        print(f"   \u2b50 {stars} stars | \U0001f374 {forks} forks | {lang}")
        print(f"   \U0001f3f7\ufe0f {tags}")
        print(f"   \U0001f517 {url}")
        print()

if __name__ == '__main__':
    run_scanner()
