#!/usr/bin/env python3
"""
Test just username/password login to Reddit
"""
import praw

print("Testing bishop_openclaw account credentials...")
print()

# Try with minimal reddit instance - just to verify username/password
try:
    # Use a generic client_id/secret just to test the username/password
    reddit = praw.Reddit(
        client_id="M3NDEsfIctAruCSgFgDA",
        client_secret="f9FWIjxY-AJ-EN_y8VbOUlot0Rc1QA",
        username="bishop_openclaw",
        password="tYok52pw8OhsEa",
        user_agent="test/1.0"
    )
    
    me = reddit.user.me()
    print(f"✅ Account login successful: {me}")
    print(f"Karma: {me.link_karma} link, {me.comment_karma} comment")
    print(f"Created: {me.created_utc}")
    
except Exception as e:
    print(f"❌ Login failed: {e}")
    print()
    print("Possible reasons:")
    print("1. Wrong password (double-check: tYok52pw8OhsEa)")
    print("2. Account has 2FA enabled")
    print("3. Account is suspended/shadowbanned")
    print("4. Password was changed")
    print()
    print("Drew - can you verify the bishop_openclaw password is correct?")
