#!/usr/bin/env python3
"""
Main RSS Search Demo - Complete business lead detection workflow
"""
from datetime import datetime
from pathlib import Path

from reddit_rss_client import RedditRSSClient
from subreddit_scorer import SubredditScorer
from business_lead_detector import BusinessLeadDetector


def main():
    """Run complete business lead detection workflow"""
    
    print("=" * 80)
    print("REDDIT HELPER HELPER - RSS Edition")
    print("Business Lead Detection System")
    print("=" * 80)
    
    # Step 1: Score all subreddits
    print("\n" + "=" * 80)
    print("STEP 1: SCORING SUBREDDITS")
    print("=" * 80)
    
    scorer = SubredditScorer()
    scorer.score_all_subreddits()
    
    # Show stats
    stats = scorer.get_stats()
    print(f"\n📊 DATABASE STATISTICS:")
    print(f"   Total subreddits:        {stats['total_subreddits']:,}")
    print(f"   Business-relevant:       {stats['scored_subreddits']:,}")
    print(f"   Perfect match (100):     {stats['score_100']:,}")
    print(f"   High value (90+):        {stats['score_90_plus']:,}")
    
    # Get top subreddits
    top_subreddits = scorer.get_top_subreddits(n=15, min_score=70)
    
    print(f"\n🎯 SELECTED TOP {len(top_subreddits)} SUBREDDITS:")
    for i, (sub, score) in enumerate(top_subreddits, 1):
        print(f"   {i:2}. r/{sub:25} [Score: {score}]")
    
    # Step 2: Search for business leads
    print("\n" + "=" * 80)
    print("STEP 2: SEARCHING FOR BUSINESS LEADS")
    print("=" * 80)
    
    detector = BusinessLeadDetector()
    
    # Extract just the subreddit names
    subreddit_names = [sub for sub, score in top_subreddits]
    
    # Search with minimum 2 keyword matches
    results = detector.search_subreddits(
        subreddits=subreddit_names,
        min_score=2,
        sort='new',
        limit_per_sub=25
    )
    
    # Step 3: Show results
    print("\n" + "=" * 80)
    print("STEP 3: RESULTS")
    print("=" * 80)
    
    if not results:
        print("\n❌ No business leads found matching criteria")
        return
    
    print(f"\n✅ Found {len(results)} business leads!")
    
    # Show top 15 results
    detector.print_top_results(results, 15)
    
    # Step 4: Export results
    print("\n" + "=" * 80)
    print("STEP 4: EXPORTING RESULTS")
    print("=" * 80)
    
    # Create Exports directory if it doesn't exist
    Path('Exports').mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    detector.export_to_csv(results, f'Exports/business_leads_{timestamp}.csv')
    detector.export_to_json(results, f'Exports/business_leads_{timestamp}.json')
    detector.export_to_markdown(results, f'Exports/business_leads_{timestamp}.md')
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 RESULTS:")
    print(f"   Subreddits searched:     {len(subreddit_names)}")
    print(f"   Business leads found:    {len(results)}")
    print(f"   Top lead score:          {results[0]['score']} keywords")
    print(f"   Average score:           {sum(r['score'] for r in results) / len(results):.1f} keywords")
    
    print(f"\n📁 FILES SAVED TO: Exports/")
    print(f"   - business_leads_{timestamp}.csv")
    print(f"   - business_leads_{timestamp}.json")
    print(f"   - business_leads_{timestamp}.md")
    
    print("\n✅ Business lead detection complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Search interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
