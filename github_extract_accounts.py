#!/usr/bin/env python3
"""
Extract unique account owners from the 100 projects discovered
Then get their details to build the accounts list
"""

import json
import requests
import time
from collections import defaultdict

def load_projects():
    with open('Database/github_discoveries.json', 'r') as f:
        data = json.load(f)
    return data.get('projects', [])

def get_user_details(username):
    """Get detailed user info"""
    url = f"https://api.github.com/users/{username}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print(f"  ⚠️  Rate limited")
            return None
    except Exception as e:
        print(f"  ⚠️  Error getting {username}: {e}")
    
    return None

def extract_accounts_from_projects():
    """Get account details from project owners"""
    print("🔍 EXTRACTING ACCOUNTS FROM PROJECT OWNERS")
    print("=" * 60)
    
    projects = load_projects()
    
    # Get unique owners
    owners = {}
    for proj in projects:
        owner = proj.get('owner')
        if owner and owner not in owners:
            owners[owner] = {
                'username': owner,
                'projects': []
            }
        if owner:
            owners[owner]['projects'].append({
                'name': proj.get('name'),
                'stars': proj.get('stars', 0),
                'url': proj.get('url')
            })
    
    print(f"Found {len(owners)} unique account owners")
    
    # Get details for each
    accounts = []
    for i, (username, data) in enumerate(owners.items(), 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(owners)}")
        
        details = get_user_details(username)
        if details:
            accounts.append({
                'username': username,
                'profile_url': details.get('html_url', ''),
                'avatar_url': details.get('avatar_url', ''),
                'type': details.get('type', 'User'),
                'followers': details.get('followers', 0),
                'following': details.get('following', 0),
                'public_repos': details.get('public_repos', 0),
                'public_gists': details.get('public_gists', 0),
                'bio': details.get('bio', ''),
                'blog': details.get('blog', ''),
                'twitter': details.get('twitter_username', ''),
                'company': details.get('company', ''),
                'location': details.get('location', ''),
                'created_at': details.get('created_at', ''),
                'updated_at': details.get('updated_at', ''),
                'discovered_projects': data['projects']
            })
        
        time.sleep(1)  # Rate limiting
        
        if len(accounts) >= 100:
            break
    
    return accounts

def update_discoveries(accounts):
    """Update the discoveries JSON with accounts"""
    with open('Database/github_discoveries.json', 'r') as f:
        data = json.load(f)
    
    # Sort accounts by followers + repos
    accounts_sorted = sorted(
        accounts,
        key=lambda x: x.get('followers', 0) + (x.get('public_repos', 0) * 10),
        reverse=True
    )
    
    data['accounts'] = accounts_sorted
    data['total_accounts'] = len(accounts_sorted)
    data['top_accounts'] = accounts_sorted[:20]
    
    with open('Database/github_discoveries.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Updated with {len(accounts)} accounts")
    print(f"\n🏆 TOP 10 ACCOUNTS:")
    for i, acc in enumerate(accounts_sorted[:10], 1):
        print(f"  {i}. @{acc['username']} ({acc['followers']} followers, {acc['public_repos']} repos)")

if __name__ == '__main__':
    accounts = extract_accounts_from_projects()
    update_discoveries(accounts)
