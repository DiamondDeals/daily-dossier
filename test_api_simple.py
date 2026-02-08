#!/usr/bin/env python3
"""
Simple Reddit API test - minimal dependencies
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
username = os.getenv('REDDIT_USERNAME')
password = os.getenv('REDDIT_PASSWORD')
user_agent = os.getenv('REDDIT_USER_AGENT')

print("=" * 60)
print("REDDIT API CREDENTIALS TEST")
print("=" * 60)
print(f"Client ID: {client_id}")
print(f"Username: {username}")
print(f"User Agent: {user_agent}")
print(f"Secret: {'*' * len(client_secret) if client_secret else 'NOT SET'}")
print("=" * 60)

try:
    import praw
    print("\n✅ PRAW library installed")
    
    # Create Reddit instance
    print("\n🔄 Authenticating with Reddit API...")
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent
    )
    
    # Test authentication
    print(f"✅ Authenticated as: {reddit.user.me()}")
    
    # Test basic search
    print("\n🔍 Testing search in r/entrepreneur...")
    subreddit = reddit.subreddit("entrepreneur")
    print(f"✅ Found subreddit: r/{subreddit.display_name}")
    print(f"   Subscribers: {subreddit.subscribers:,}")
    
    # Get 3 hot posts
    print("\n📝 Fetching 3 hot posts...")
    for i, post in enumerate(subreddit.hot(limit=3), 1):
        print(f"\n{i}. {post.title[:60]}...")
        print(f"   Score: {post.score} | Comments: {post.num_comments}")
        print(f"   URL: {post.url}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Reddit API is working!")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ Missing dependency: {e}")
    print("Install with: pip3 install praw python-dotenv --break-system-packages")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
