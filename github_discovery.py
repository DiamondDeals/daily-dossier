#!/usr/bin/env python3
"""
Discover 100 GitHub accounts + 100 projects relevant to Drew's interests
"""

import requests
import json
from datetime import datetime
import time

# GitHub topics relevant to Drew's interests
TOPICS = [
    'saas', 'business', 'entrepreneur', 'indie-hacking', 'startup',
    'marketing', 'seo', 'automation', 'ai', 'machine-learning',
    'monetization', 'revenue', 'bootstrapped', 'side-project',
    'real-estate', 'flipper', 'digital-marketing', 'analytics',
    'crm', 'lead-generation', 'growth-hacking', 'productivity'
]

KEYWORDS = [
    'saas template', 'boilerplate', 'starter', 'business automation',
    'lead generation', 'seo tool', 'marketing automation', 'ai saas',
    'indie hacker', 'micro saas', 'monetization', 'stripe integration',
    'landing page', 'analytics', 'growth tool', 'productivity'
]

def search_github_repos(query, per_page=30):
    """Search GitHub repositories"""
    url = "https://api.github.com/search/repositories"
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': per_page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('items', [])
        elif response.status_code == 403:
            print(f"  ⚠️  Rate limited, waiting 60s...")
            time.sleep(60)
            return search_github_repos(query, per_page)
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    return []

def search_github_users(query, per_page=30):
    """Search GitHub users"""
    url = "https://api.github.com/search/users"
    params = {
        'q': query,
        'sort': 'followers',
        'order': 'desc',
        'per_page': per_page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('items', [])
        elif response.status_code == 403:
            print(f"  ⚠️  Rate limited, waiting 60s...")
            time.sleep(60)
            return search_github_users(query, per_page)
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    return []

def get_user_details(username):
    """Get detailed user info"""
    url = f"https://api.github.com/users/{username}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  ⚠️  Error getting {username}: {e}")
    
    return None

def discover_accounts():
    """Find 100 relevant GitHub accounts"""
    print("🔍 DISCOVERING GITHUB ACCOUNTS")
    print("=" * 60)
    
    all_accounts = {}
    
    # Search by topics
    for topic in TOPICS[:10]:  # Limit to avoid rate limits
        print(f"  Searching: {topic}")
        users = search_github_users(f"topic:{topic}", per_page=10)
        
        for user in users:
            username = user.get('login')
            if username and username not in all_accounts:
                all_accounts[username] = {
                    'username': username,
                    'profile_url': user.get('html_url', ''),
                    'avatar_url': user.get('avatar_url', ''),
                    'type': user.get('type', 'User'),
                    'followers': 0,
                    'public_repos': 0,
                    'bio': '',
                    'blog': '',
                    'twitter': '',
                    'company': '',
                    'location': '',
                    'discovered_via': topic
                }
        
        time.sleep(2)  # Rate limiting
        
        if len(all_accounts) >= 100:
            break
    
    print(f"\n✅ Found {len(all_accounts)} accounts")
    
    # Get detailed info for top accounts
    print("\n📊 Fetching detailed info...")
    for i, username in enumerate(list(all_accounts.keys())[:100], 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/100")
        
        details = get_user_details(username)
        if details:
            all_accounts[username].update({
                'followers': details.get('followers', 0),
                'public_repos': details.get('public_repos', 0),
                'bio': details.get('bio', ''),
                'blog': details.get('blog', ''),
                'twitter': details.get('twitter_username', ''),
                'company': details.get('company', ''),
                'location': details.get('location', ''),
                'created_at': details.get('created_at', '')
            })
        
        time.sleep(1)  # Rate limiting
    
    return list(all_accounts.values())[:100]

def discover_projects():
    """Find 100 relevant GitHub projects"""
    print("\n🔍 DISCOVERING GITHUB PROJECTS")
    print("=" * 60)
    
    all_projects = {}
    
    # Search by keywords
    for keyword in KEYWORDS[:15]:  # Limit to avoid rate limits
        print(f"  Searching: {keyword}")
        repos = search_github_repos(keyword, per_page=10)
        
        for repo in repos:
            repo_id = repo.get('id')
            if repo_id and repo_id not in all_projects:
                all_projects[repo_id] = {
                    'id': repo_id,
                    'name': repo.get('name', ''),
                    'full_name': repo.get('full_name', ''),
                    'owner': repo.get('owner', {}).get('login', ''),
                    'description': repo.get('description', ''),
                    'url': repo.get('html_url', ''),
                    'homepage': repo.get('homepage', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'watchers': repo.get('watchers_count', 0),
                    'open_issues': repo.get('open_issues_count', 0),
                    'language': repo.get('language', ''),
                    'topics': repo.get('topics', []),
                    'created_at': repo.get('created_at', ''),
                    'updated_at': repo.get('updated_at', ''),
                    'pushed_at': repo.get('pushed_at', ''),
                    'license': repo.get('license', {}).get('name', '') if repo.get('license') else '',
                    'discovered_via': keyword
                }
        
        time.sleep(2)  # Rate limiting
        
        if len(all_projects) >= 100:
            break
    
    print(f"\n✅ Found {len(all_projects)} projects")
    
    return list(all_projects.values())[:100]

def analyze_activity(accounts, projects):
    """Analyze and rank by activity"""
    print("\n📊 ANALYZING ACTIVITY")
    print("=" * 60)
    
    # Rank accounts by followers + repos
    accounts_sorted = sorted(
        accounts,
        key=lambda x: x.get('followers', 0) + (x.get('public_repos', 0) * 10),
        reverse=True
    )
    
    # Rank projects by stars + recent activity
    projects_sorted = sorted(
        projects,
        key=lambda x: x.get('stars', 0) + (x.get('forks', 0) * 5),
        reverse=True
    )
    
    # Pick top 20 of each
    top_accounts = accounts_sorted[:20]
    top_projects = projects_sorted[:20]
    
    print(f"\n🏆 TOP 20 ACCOUNTS:")
    for i, acc in enumerate(top_accounts[:10], 1):
        print(f"  {i}. @{acc['username']} ({acc['followers']} followers, {acc['public_repos']} repos)")
    
    print(f"\n🏆 TOP 20 PROJECTS:")
    for i, proj in enumerate(top_projects[:10], 1):
        print(f"  {i}. {proj['full_name']} (⭐{proj['stars']})")
    
    return {
        'accounts': {
            'all': accounts_sorted,
            'top_20': top_accounts
        },
        'projects': {
            'all': projects_sorted,
            'top_20': top_projects
        }
    }

def save_discoveries(data):
    """Save to JSON"""
    output = {
        'date': datetime.now().isoformat(),
        'total_accounts': len(data['accounts']['all']),
        'total_projects': len(data['projects']['all']),
        'accounts': data['accounts']['all'],
        'projects': data['projects']['all'],
        'top_accounts': data['accounts']['top_20'],
        'top_projects': data['projects']['top_20']
    }
    
    with open('Database/github_discoveries.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Saved: Database/github_discoveries.json")
    return 'Database/github_discoveries.json'

if __name__ == '__main__':
    print("🚀 GITHUB DISCOVERY STARTED")
    print("=" * 60)
    print()
    
    # Discover
    accounts = discover_accounts()
    projects = discover_projects()
    
    # Analyze
    analysis = analyze_activity(accounts, projects)
    
    # Save
    save_discoveries(analysis)
    
    print("\n✅ DISCOVERY COMPLETE!")
    print(f"   Accounts: {len(accounts)}")
    print(f"   Projects: {len(projects)}")
