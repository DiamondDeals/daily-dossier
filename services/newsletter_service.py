"""
Newsletter Service for PersonalizedReddit
Generates AI-powered daily digests of business opportunities
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.logging_config import get_logger, log_performance

class NewsletterService:
    """
    Service for generating AI-powered newsletters and daily digests
    """
    
    def __init__(self, reddit_service, ai_service, database):
        self.reddit_service = reddit_service
        self.ai_service = ai_service
        self.database = database
        self.logger = get_logger(__name__)
        
        # Newsletter configuration
        self.config = {
            'min_business_score': 2.0,
            'max_posts_per_digest': 25,
            'summary_length': 100,
            'categories': ['automation', 'integration', 'scaling', 'process_improvement'],
            'subreddits': [
                'entrepreneur', 'smallbusiness', 'freelance', 'productivity',
                'automation', 'excel', 'business', 'startups', 'solopreneurs'
            ]
        }
    
    @log_performance
    def generate_daily_digest(self, user_preferences: Dict = None) -> Dict[str, Any]:
        """
        Generate daily digest of business opportunities
        
        Returns:
            Dictionary containing digest data and metadata
        """
        try:
            self.logger.info("Generating daily digest...")
            
            # Get recent posts with business opportunities
            opportunities = self._fetch_business_opportunities()
            
            # Filter and rank opportunities
            top_opportunities = self._rank_opportunities(opportunities)
            
            # Generate summaries for top opportunities
            summaries = self._generate_summaries(top_opportunities)
            
            # Create digest structure
            digest = {
                'generated_at': datetime.now().isoformat(),
                'total_posts_analyzed': len(opportunities),
                'opportunities_found': len(top_opportunities),
                'trending_score': self._calculate_trending_score(top_opportunities),
                'last_update': self._get_last_update_time(),
                'match_rate': self._calculate_match_rate(opportunities, top_opportunities),
                'categories': self._categorize_opportunities(top_opportunities),
                'top_opportunities': summaries,
                'statistics': self._generate_statistics(opportunities, top_opportunities)
            }
            
            # Save digest to database
            self._save_digest(digest)
            
            self.logger.info(f"Daily digest generated with {len(top_opportunities)} opportunities")
            return digest
            
        except Exception as e:
            self.logger.error(f"Failed to generate daily digest: {e}", exc_info=True)
            return self._get_empty_digest()
    
    def _fetch_business_opportunities(self) -> List[Any]:
        """Fetch recent posts and analyze for business opportunities"""
        opportunities = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_subreddit = {
                executor.submit(self._fetch_from_subreddit, subreddit): subreddit
                for subreddit in self.config['subreddits']
            }
            
            for future in as_completed(future_to_subreddit):
                subreddit = future_to_subreddit[future]
                try:
                    posts = future.result()
                    opportunities.extend(posts)
                except Exception as e:
                    self.logger.error(f"Failed to fetch from {subreddit}: {e}")
        
        return opportunities
    
    def _fetch_from_subreddit(self, subreddit: str) -> List[Any]:
        """Fetch and analyze posts from a single subreddit"""
        try:
            # Get recent posts
            posts = self.reddit_service.get_real_time_posts([subreddit], limit=20)
            
            # Filter posts with business opportunities
            business_posts = []
            for post in posts:
                if hasattr(post, 'business_score') and post.business_score >= self.config['min_business_score']:
                    business_posts.append(post)
            
            return business_posts
            
        except Exception as e:
            self.logger.error(f"Error fetching from {subreddit}: {e}")
            return []
    
    def _rank_opportunities(self, opportunities: List[Any]) -> List[Any]:
        """Rank opportunities by business score and relevance"""
        # Sort by business score, urgency, and engagement
        ranked = sorted(
            opportunities,
            key=lambda x: (
                getattr(x, 'business_score', 0),
                1 if getattr(x, 'urgency_level', 'low') == 'high' else 0.5,
                getattr(x, 'score', 0) + getattr(x, 'num_comments', 0)
            ),
            reverse=True
        )
        
        return ranked[:self.config['max_posts_per_digest']]
    
    def _generate_summaries(self, opportunities: List[Any]) -> List[Dict]:
        """Generate AI summaries for opportunities"""
        summaries = []
        
        for opportunity in opportunities:
            try:
                # Generate summary
                text_to_summarize = f"{opportunity.title}\n\n{opportunity.text}"
                summary_result = self.ai_service.summarize_text(
                    text_to_summarize, 
                    max_length=self.config['summary_length']
                )
                
                # Create opportunity card
                card = {
                    'id': opportunity.id,
                    'title': opportunity.title,
                    'summary': summary_result['summary'],
                    'subreddit': opportunity.subreddit,
                    'author': opportunity.author,
                    'business_score': getattr(opportunity, 'business_score', 0),
                    'urgency_level': getattr(opportunity, 'urgency_level', 'low'),
                    'problem_indicators': getattr(opportunity, 'problem_indicators', []),
                    'automation_keywords': getattr(opportunity, 'automation_keywords', []),
                    'engagement': {
                        'score': opportunity.score,
                        'comments': opportunity.num_comments,
                        'upvote_ratio': getattr(opportunity, 'upvote_ratio', 0)
                    },
                    'permalink': opportunity.permalink,
                    'created_utc': opportunity.created_utc,
                    'priority': self._calculate_priority(opportunity)
                }
                
                summaries.append(card)
                
            except Exception as e:
                self.logger.error(f"Failed to generate summary for post {opportunity.id}: {e}")
        
        return summaries
    
    def _calculate_priority(self, opportunity) -> str:
        """Calculate priority level for opportunity"""
        score = getattr(opportunity, 'business_score', 0)
        urgency = getattr(opportunity, 'urgency_level', 'low')
        
        if score >= 7 or urgency == 'high':
            return 'high'
        elif score >= 4 or urgency == 'medium':
            return 'medium'
        else:
            return 'low'
    
    def _calculate_trending_score(self, opportunities: List[Any]) -> float:
        """Calculate overall trending score"""
        if not opportunities:
            return 0.0
        
        total_score = sum(getattr(opp, 'business_score', 0) for opp in opportunities)
        return round(total_score / len(opportunities), 1)
    
    def _get_last_update_time(self) -> str:
        """Get last update time"""
        now = datetime.now()
        return f"{(now.minute % 10)} min ago"  # Simulated update time
    
    def _calculate_match_rate(self, all_posts: List[Any], matches: List[Any]) -> str:
        """Calculate match rate percentage"""
        if not all_posts:
            return "0%"
        
        rate = (len(matches) / len(all_posts)) * 100
        return f"{int(rate)}%"
    
    def _categorize_opportunities(self, opportunities: List[Any]) -> Dict[str, List[Dict]]:
        """Categorize opportunities by type"""
        categories = {
            'Manual Process Solutions': [],
            'Workflow Automation': [],
            'Time Management': [],
            'System Integration': []
        }
        
        category_keywords = {
            'Manual Process Solutions': ['manual', 'data entry', 'copy paste', 'repetitive'],
            'Workflow Automation': ['workflow', 'automate', 'process', 'streamline'],
            'Time Management': ['time', 'hours', 'daily', 'schedule'],
            'System Integration': ['integrate', 'connect', 'sync', 'api']
        }
        
        for opp in opportunities:
            # Get keywords from opportunity
            opp_keywords = getattr(opp, 'automation_keywords', [])
            opp_text = f"{opp.title} {opp.text}".lower()
            
            # Categorize based on keywords
            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in opp_text for keyword in keywords):
                    categories[category].append({
                        'title': opp.title,
                        'subreddit': opp.subreddit,
                        'business_score': getattr(opp, 'business_score', 0),
                        'id': opp.id
                    })
                    categorized = True
                    break
            
            # Default category if not categorized
            if not categorized:
                categories['Manual Process Solutions'].append({
                    'title': opp.title,
                    'subreddit': opp.subreddit,
                    'business_score': getattr(opp, 'business_score', 0),
                    'id': opp.id
                })
        
        return categories
    
    def _generate_statistics(self, all_posts: List[Any], opportunities: List[Any]) -> Dict:
        """Generate digest statistics"""
        return {
            'posts_analyzed': len(all_posts),
            'opportunities_found': len(opportunities),
            'high_priority_count': len([o for o in opportunities if self._calculate_priority(o) == 'high']),
            'medium_priority_count': len([o for o in opportunities if self._calculate_priority(o) == 'medium']),
            'low_priority_count': len([o for o in opportunities if self._calculate_priority(o) == 'low']),
            'subreddits_scanned': len(self.config['subreddits']),
            'avg_business_score': round(
                sum(getattr(o, 'business_score', 0) for o in opportunities) / len(opportunities)
                if opportunities else 0, 1
            )
        }
    
    def _save_digest(self, digest: Dict) -> None:
        """Save digest to database"""
        try:
            # This could be enhanced to save full digest data
            # For now, just log that it would be saved
            self.logger.debug("Digest saved to database (placeholder)")
        except Exception as e:
            self.logger.error(f"Failed to save digest: {e}")
    
    def _get_empty_digest(self) -> Dict[str, Any]:
        """Return empty digest structure for error cases"""
        return {
            'generated_at': datetime.now().isoformat(),
            'total_posts_analyzed': 0,
            'opportunities_found': 0,
            'trending_score': 0.0,
            'last_update': '0 min ago',
            'match_rate': '0%',
            'categories': {},
            'top_opportunities': [],
            'statistics': {
                'posts_analyzed': 0,
                'opportunities_found': 0,
                'high_priority_count': 0,
                'medium_priority_count': 0,
                'low_priority_count': 0,
                'subreddits_scanned': 0,
                'avg_business_score': 0.0
            }
        }
    
    def get_saved_digests(self, days: int = 7) -> List[Dict]:
        """Get previously saved digests"""
        # Placeholder for database query
        # Would return saved digests from database
        return []
    
    def customize_feed(self, preferences: Dict) -> None:
        """Customize newsletter feed based on user preferences"""
        if 'subreddits' in preferences:
            self.config['subreddits'] = preferences['subreddits']
        
        if 'min_business_score' in preferences:
            self.config['min_business_score'] = preferences['min_business_score']
        
        if 'categories' in preferences:
            self.config['categories'] = preferences['categories']
        
        self.logger.info("Newsletter feed customized")
    
    def close(self):
        """Clean up service resources"""
        self.logger.info("Newsletter service closed")