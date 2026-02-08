#!/usr/bin/env python3
"""
Detailed Reddit API authentication test
"""
import os
from dotenv import load_dotenv
import praw
from prawcore import ResponseException

# Load environment variables
load_dotenv()

client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
username = os.getenv('REDDIT_USERNAME')
password = os.getenv('REDDIT_PASSWORD')
user_agent = os.getenv('REDDIT_USER_AGENT')

print("Testing credentials...")
print(f"Client ID: {client_id}")
print(f"Client Secret length: {len(client_secret) if client_secret else 0}")
print(f"Username: {username}")
print(f"Password length: {len(password) if password else 0}")
print(f"User Agent: {user_agent}")
print()

try:
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent
    )
    
    # Try to get authenticated user
    me = reddit.user.me()
    print(f"✅ SUCCESS! Authenticated as: {me}")
    
except ResponseException as e:
    print(f"❌ ResponseException: {e}")
    print(f"Status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
    print(f"\nPossible issues:")
    print("1. Wrong username or password")
    print("2. 2FA enabled on account (Reddit apps don't support 2FA)")
    print("3. Account suspended or restricted")
    print("4. Wrong client_id or client_secret")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"Type: {type(e).__name__}")
