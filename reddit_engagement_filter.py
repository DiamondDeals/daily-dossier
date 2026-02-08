#!/usr/bin/env python3
"""
STRICT Reddit Engagement Filter
Only returns posts with REAL engagement (upvotes + comments)
Drew's requirement: NO dead posts!
"""

def filter_by_engagement(posts, min_score=50, min_comments=5, min_engagement=100):
    """
    Filter Reddit posts by REAL engagement
    
    Args:
        min_score: Minimum upvotes (default: 50)
        min_comments: Minimum comments (default: 5)
        min_engagement: Minimum total engagement score (default: 100)
    
    Engagement score = upvotes + (comments * 2)
    Comments are 2x weighted because they indicate real discussion
    """
    filtered = []
    
    for post in posts:
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        engagement_score = score + (comments * 2)
        
        # STRICT REQUIREMENTS
        if score < min_score:
            continue  # Not enough upvotes
        
        if comments < min_comments:
            continue  # Not enough discussion
        
        if engagement_score < min_engagement:
            continue  # Not enough total engagement
        
        # Passed all filters
        post['engagement_score'] = engagement_score
        filtered.append(post)
    
    # Sort by engagement (highest first)
    filtered.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    return filtered

def test_filter():
    """Test the filter with example posts"""
    test_posts = [
        # Good posts
        {'title': 'Great discussion', 'score': 200, 'num_comments': 50},  # 300 ✅
        {'title': 'Popular post', 'score': 150, 'num_comments': 25},      # 200 ✅
        {'title': 'Good engagement', 'score': 100, 'num_comments': 20},   # 140 ✅
        
        # Bad posts (should be filtered)
        {'title': 'Dead post', 'score': 5, 'num_comments': 0},            # 5 ❌
        {'title': 'Low engagement', 'score': 20, 'num_comments': 2},      # 24 ❌
        {'title': 'Service offer', 'score': 10, 'num_comments': 1},       # 12 ❌
    ]
    
    print("=" * 70)
    print("TESTING STRICT ENGAGEMENT FILTER")
    print("=" * 70)
    print(f"\nInput: {len(test_posts)} posts")
    
    filtered = filter_by_engagement(test_posts)
    
    print(f"Output: {len(filtered)} posts (passed strict filter)")
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    for i, post in enumerate(filtered, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   ↑{post['score']} upvotes • 💬{post['num_comments']} comments")
        print(f"   📊 Engagement Score: {post['engagement_score']}")
    
    print("\n" + "=" * 70)
    print("✅ Only high-engagement posts included!")
    print("=" * 70)

if __name__ == '__main__':
    test_filter()
