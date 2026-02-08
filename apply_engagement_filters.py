#!/usr/bin/env python3
"""
Apply strict engagement filters to Reddit posts
Only shows posts with REAL engagement (votes + comments)
"""
import json

def load_filters():
    with open('reddit_filter_config.json', 'r') as f:
        return json.load(f)

def filter_reddit_posts(posts):
    """Filter posts by engagement quality"""
    filters = load_filters()['engagement_filters']
    
    filtered = []
    
    for post in posts:
        # Calculate engagement score
        engagement = post['score'] + (post['num_comments'] * 2)
        
        # Apply filters
        if post['score'] < filters['minimum_score']:
            continue  # Too few upvotes
        
        if post['num_comments'] < filters['minimum_comments']:
            continue  # Too few comments
        
        if engagement < filters['minimum_engagement_score']:
            continue  # Not enough total engagement
        
        # Passed all filters
        filtered.append(post)
    
    return filtered

if __name__ == '__main__':
    # Example
    test_posts = [
        {'title': 'Good post', 'score': 100, 'num_comments': 20},  # engagement: 140 ✅
        {'title': 'Bad post', 'score': 2, 'num_comments': 0},      # engagement: 2 ❌
        {'title': 'Mediocre', 'score': 30, 'num_comments': 3},     # engagement: 36 ❌
    ]
    
    filtered = filter_reddit_posts(test_posts)
    print(f"Filtered {len(test_posts)} posts down to {len(filtered)} high-engagement posts")
    
    for post in filtered:
        engagement = post['score'] + (post['num_comments'] * 2)
        print(f"✅ {post['title']} - Engagement: {engagement}")
