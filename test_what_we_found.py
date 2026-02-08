from reddit_json_client import RedditJSONClient
from reddit_engagement_filter import filter_by_engagement

client = RedditJSONClient()

print("Testing r/Entrepreneur with strict engagement filter:")
print()

posts = client.fetch_posts('Entrepreneur', limit=25, sort='hot')
filtered = filter_by_engagement(posts, min_score=50, min_comments=5, min_engagement=100)

print(f"Found {len(filtered)} high-engagement posts:")
for i, post in enumerate(filtered[:5], 1):
    print(f"\n{i}. {post['title'][:60]}...")
    print(f"   ↑{post['score']} • 💬{post['num_comments']} • Engagement: {post['engagement_score']}")
    print(f"   Preview: {post['text'][:100]}...")
