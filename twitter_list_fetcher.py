#!/usr/bin/env python3
"""
Fetch Twitter list members and vet them
"""
import requests
import json
import re

class TwitterListFetcher:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "BishopDailyDossier/1.0"
        }
    
    def get_list_members(self, list_id, max_results=100):
        """Get members of a Twitter list"""
        endpoint = f"{self.base_url}/lists/{list_id}/members"
        
        params = {
            "max_results": min(max_results, 100),
            "user.fields": "description,public_metrics,verified,created_at,url"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            members = data.get('data', [])
            
            # Vet each member
            vetted = []
            for member in members:
                score = self._vet_account(member)
                if score > 0:  # Only include if passes basic vetting
                    member['vet_score'] = score
                    vetted.append(member)
            
            # Sort by vet score
            vetted.sort(key=lambda x: x['vet_score'], reverse=True)
            
            return vetted
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("❌ List not found or private")
            elif e.response.status_code == 403:
                print("❌ Access denied - list might be private")
            else:
                print(f"❌ HTTP Error {e.response.status_code}")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def _vet_account(self, user):
        """
        Vet account quality based on bio, followers, engagement
        Returns score 0-100
        """
        score = 0
        
        bio = user.get('description', '').lower()
        metrics = user.get('public_metrics', {})
        
        followers = metrics.get('followers_count', 0)
        following = metrics.get('following_count', 1)  # Avoid div by 0
        tweets = metrics.get('tweet_count', 0)
        
        # Follower quality (not just count)
        follower_ratio = followers / following if following > 0 else 0
        
        # 1. Follower count (max 30 points)
        if followers > 100000:
            score += 30
        elif followers > 50000:
            score += 25
        elif followers > 10000:
            score += 20
        elif followers > 5000:
            score += 15
        elif followers > 1000:
            score += 10
        
        # 2. Follower ratio (quality signal, max 20 points)
        if follower_ratio > 10:
            score += 20
        elif follower_ratio > 5:
            score += 15
        elif follower_ratio > 2:
            score += 10
        
        # 3. Bio keywords (max 30 points)
        founder_keywords = ['founder', 'ceo', 'co-founder', 'creator', 'building', 'built']
        revenue_keywords = ['$', 'revenue', 'arr', 'mrr', 'million', 'billion']
        success_keywords = ['sold', 'exit', 'acquired', 'exited', 'serial']
        
        for keyword in founder_keywords:
            if keyword in bio:
                score += 10
                break
        
        for keyword in revenue_keywords:
            if keyword in bio:
                score += 10
                break
        
        for keyword in success_keywords:
            if keyword in bio:
                score += 10
                break
        
        # 4. Verified (max 10 points)
        if user.get('verified', False):
            score += 10
        
        # 5. Active tweeter (max 10 points)
        if tweets > 10000:
            score += 10
        elif tweets > 5000:
            score += 7
        elif tweets > 1000:
            score += 5
        
        return min(score, 100)  # Cap at 100

if __name__ == '__main__':
    print("=" * 70)
    print("TWITTER LIST FETCHER - VETTING AI FOUNDERS LIST")
    print("=" * 70)
    
    # Load bearer token
    with open('/home/drew/.openclaw/workspace/shared/credentials/twitter-api.txt', 'r') as f:
        for line in f:
            if line.startswith('BEARER_TOKEN='):
                bearer_token = line.split('=', 1)[1].strip()
                break
    
    fetcher = TwitterListFetcher(bearer_token)
    
    list_id = "1219117707150233605"  # Drew's AI list
    
    print(f"\n🔍 Fetching members from list: {list_id}")
    print()
    
    members = fetcher.get_list_members(list_id, max_results=100)
    
    if members:
        print(f"✅ Found {len(members)} vetted members")
        print("\n" + "=" * 70)
        print("TOP 20 BY VET SCORE")
        print("=" * 70)
        
        for i, member in enumerate(members[:20], 1):
            username = member['username']
            name = member['name']
            bio = member.get('description', '')[:100]
            metrics = member.get('public_metrics', {})
            followers = metrics.get('followers_count', 0)
            score = member['vet_score']
            verified = "✓" if member.get('verified') else ""
            
            print(f"\n{i}. @{username} {verified} (Score: {score}/100)")
            print(f"   👤 {name}")
            print(f"   👥 {followers:,} followers")
            print(f"   📝 {bio}...")
        
        # Save to file
        output = {
            'list_id': list_id,
            'fetched_at': '2026-02-07',
            'total_members': len(members),
            'accounts': [
                {
                    'username': m['username'],
                    'name': m['name'],
                    'bio': m.get('description', ''),
                    'followers': m.get('public_metrics', {}).get('followers_count', 0),
                    'verified': m.get('verified', False),
                    'score': m['vet_score']
                }
                for m in members
            ]
        }
        
        with open('twitter_vetted_accounts.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ Vetted accounts saved to: twitter_vetted_accounts.json")
        print("=" * 70)
    else:
        print("⚠️ No members found (list might be private or empty)")
