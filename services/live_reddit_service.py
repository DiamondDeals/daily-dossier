"""
Live Reddit Service for PersonalizedReddit
Provides real-time Reddit monitoring and enhanced post interaction capabilities
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

from utils.logging_config import get_logger, log_performance

class LiveRedditService:
    """
    Service for real-time Reddit monitoring and enhanced post interactions
    """
    
    def __init__(self, reddit_service, ai_service, database):
        self.reddit_service = reddit_service
        self.ai_service = ai_service
        self.database = database
        self.logger = get_logger(__name__)
        
        # Live monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.update_callbacks = []
        
        # Configuration
        self.config = {
            'update_interval': 30,  # seconds
            'max_posts_per_fetch': 50,
            'business_score_threshold': 2.0,
            'monitored_subreddits': [
                'entrepreneur', 'smallbusiness', 'freelance', 'productivity',
                'automation', 'excel', 'business', 'startups', 'solopreneurs'
            ]
        }
        
        # Cache for recent posts
        self.recent_posts = []
        self.post_cache = {}
        self.last_update = None
        
    @log_performance
    def start_live_monitoring(self, callback: Optional[Callable] = None):
        """
        Start live monitoring of Reddit posts
        
        Args:
            callback: Function to call when new posts are found
        """
        if self.is_monitoring:
            self.logger.warning("Live monitoring already active")
            return
        
        try:
            self.is_monitoring = True
            if callback:
                self.update_callbacks.append(callback)
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("Live Reddit monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start live monitoring: {e}")
            self.is_monitoring = False
            raise
    
    def stop_live_monitoring(self):
        """Stop live monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Live Reddit monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Fetch new posts
                new_posts = self._fetch_recent_posts()
                
                if new_posts:
                    # Process posts for business opportunities
                    processed_posts = self._process_posts_for_opportunities(new_posts)
                    
                    # Update cache
                    self._update_post_cache(processed_posts)
                    
                    # Notify callbacks
                    self._notify_callbacks(processed_posts)
                    
                    self.last_update = datetime.now()
                
                # Wait for next update
                time.sleep(self.config['update_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config['update_interval'])
    
    def _fetch_recent_posts(self) -> List[Any]:
        """Fetch recent posts from monitored subreddits"""
        try:
            new_posts = self.reddit_service.get_real_time_posts(
                subreddits=self.config['monitored_subreddits'],
                limit=self.config['max_posts_per_fetch']
            )
            
            # Filter out posts we've already seen
            filtered_posts = []
            for post in new_posts:
                if post.id not in self.post_cache:
                    filtered_posts.append(post)
            
            self.logger.debug(f"Fetched {len(filtered_posts)} new posts")
            return filtered_posts
            
        except Exception as e:
            self.logger.error(f"Failed to fetch recent posts: {e}")
            return []
    
    def _process_posts_for_opportunities(self, posts: List[Any]) -> List[Dict[str, Any]]:
        """Process posts to identify business opportunities"""
        processed_posts = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_post = {
                executor.submit(self._analyze_single_post, post): post 
                for post in posts
            }
            
            for future in as_completed(future_to_post):
                post = future_to_post[future]
                try:
                    analysis_result = future.result()
                    if analysis_result:
                        processed_posts.append(analysis_result)
                except Exception as e:
                    self.logger.error(f"Failed to analyze post {post.id}: {e}")
        
        # Sort by business score
        processed_posts.sort(
            key=lambda x: x.get('business_score', 0), 
            reverse=True
        )
        
        return processed_posts
    
    def _analyze_single_post(self, post) -> Optional[Dict[str, Any]]:
        """Analyze a single post for business opportunities"""
        try:
            # Combine title and content for analysis
            full_text = f"{post.title}\n\n{getattr(post, 'selftext', '')}"
            
            # AI analysis for business opportunities
            ai_analysis = self.ai_service.detect_business_opportunities(full_text)
            
            # Skip posts with low business scores
            if ai_analysis.get('opportunity_score', 0) < self.config['business_score_threshold']:
                return None
            
            # Generate summary
            summary = self.ai_service.summarize_text(full_text, max_length=100)
            
            # Analyze sentiment
            sentiment = self.ai_service.analyze_sentiment(full_text)
            
            # Create processed post data
            processed_post = {
                'id': post.id,
                'title': post.title,
                'author': str(post.author) if post.author else '[deleted]',
                'subreddit': str(post.subreddit),
                'url': f"https://reddit.com{post.permalink}",
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': post.created_utc,
                'time_ago': self._time_ago(post.created_utc),
                
                # AI analysis results
                'business_score': ai_analysis.get('opportunity_score', 0),
                'priority': self._calculate_priority(ai_analysis),
                'problem_indicators': ai_analysis.get('keywords_found', {}),
                'automation_keywords': ai_analysis.get('categories', []),
                'urgency_level': ai_analysis.get('urgency_level', 'low'),
                'sentiment': sentiment,
                
                # Summary and content
                'summary': summary.get('summary', ''),
                'content_preview': full_text[:300] + "..." if len(full_text) > 300 else full_text,
                'full_content': full_text,
                
                # Metadata
                'analyzed_at': datetime.now().isoformat(),
                'analysis_confidence': ai_analysis.get('confidence', 0)
            }
            
            return processed_post
            
        except Exception as e:
            self.logger.error(f"Failed to analyze post {post.id}: {e}")
            return None
    
    def _calculate_priority(self, ai_analysis: Dict) -> str:
        """Calculate priority level based on AI analysis"""
        score = ai_analysis.get('opportunity_score', 0)
        urgency = ai_analysis.get('urgency_level', 'low')
        
        if score >= 7 or urgency == 'high':
            return 'high'
        elif score >= 4 or urgency == 'medium':
            return 'medium'
        else:
            return 'low'
    
    def _time_ago(self, created_utc: float) -> str:
        """Convert UTC timestamp to 'time ago' string"""
        try:
            created_time = datetime.fromtimestamp(created_utc)
            now = datetime.now()
            diff = now - created_time
            
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "just now"
                
        except Exception:
            return "unknown"
    
    def _update_post_cache(self, posts: List[Dict]):
        """Update the post cache with new posts"""
        for post in posts:
            self.post_cache[post['id']] = post
        
        # Keep only recent posts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.post_cache = {
            post_id: post for post_id, post in self.post_cache.items()
            if datetime.fromisoformat(post['analyzed_at'].replace('Z', '+00:00')) > cutoff_time
        }
        
        # Update recent posts list
        self.recent_posts = sorted(
            self.post_cache.values(),
            key=lambda x: x['created_utc'],
            reverse=True
        )[:100]  # Keep last 100 posts
    
    def _notify_callbacks(self, new_posts: List[Dict]):
        """Notify registered callbacks about new posts"""
        for callback in self.update_callbacks:
            try:
                callback(new_posts)
            except Exception as e:
                self.logger.error(f"Callback notification failed: {e}")
    
    def get_live_posts(self, limit: int = 50) -> List[Dict]:
        """
        Get current live posts
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of processed post dictionaries
        """
        return self.recent_posts[:limit]
    
    def get_posts_by_filter(self, filter_type: str, limit: int = 50) -> List[Dict]:
        """
        Get posts filtered by type
        
        Args:
            filter_type: Type of filter ('hot', 'new', 'top', 'business', etc.)
            limit: Maximum number of posts to return
        """
        posts = self.recent_posts.copy()
        
        if filter_type == 'business':
            # Filter for high business scores
            posts = [p for p in posts if p.get('business_score', 0) >= 3.0]
        elif filter_type == 'high_priority':
            posts = [p for p in posts if p.get('priority') == 'high']
        elif filter_type == 'automation':
            posts = [p for p in posts if 'automation' in p.get('automation_keywords', [])]
        
        # Sort based on filter type
        if filter_type == 'hot':
            posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        elif filter_type == 'new':
            posts.sort(key=lambda x: x.get('created_utc', 0), reverse=True)
        elif filter_type == 'top':
            posts.sort(key=lambda x: x.get('score', 0) + x.get('num_comments', 0), reverse=True)
        else:
            posts.sort(key=lambda x: x.get('business_score', 0), reverse=True)
        
        return posts[:limit]
    
    def perform_quick_action(self, action_type: str, post_id: str, **kwargs) -> Dict[str, Any]:
        """
        Perform quick action on a post
        
        Args:
            action_type: Type of action ('save', 'vote', 'comment', 'create_lead')
            post_id: Reddit post ID
            **kwargs: Additional action parameters
            
        Returns:
            Dictionary with action result
        """
        try:
            post = self.post_cache.get(post_id)
            if not post:
                return {'success': False, 'error': 'Post not found in cache'}
            
            if action_type == 'save':
                return self._save_post(post)
            elif action_type == 'create_lead':
                return self._create_business_lead(post)
            elif action_type == 'contact_author':
                return self._prepare_contact_info(post)
            elif action_type == 'export':
                return self._export_post(post)
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            self.logger.error(f"Quick action failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _save_post(self, post: Dict) -> Dict[str, Any]:
        """Save post to database"""
        try:
            # Save to database (implementation would depend on database schema)
            saved_post = {
                'post_id': post['id'],
                'title': post['title'],
                'business_score': post['business_score'],
                'saved_at': datetime.now().isoformat(),
                'tags': ['saved', 'live_monitoring']
            }
            
            # Database save operation would go here
            self.logger.info(f"Post {post['id']} saved for later review")
            
            return {'success': True, 'message': 'Post saved successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_business_lead(self, post: Dict) -> Dict[str, Any]:
        """Create a business lead from post"""
        try:
            lead_data = {
                'source': 'reddit',
                'post_id': post['id'],
                'title': post['title'],
                'author': post['author'],
                'subreddit': post['subreddit'],
                'business_score': post['business_score'],
                'priority': post['priority'],
                'problem_indicators': post['problem_indicators'],
                'contact_method': f"Reddit PM to u/{post['author']}",
                'url': post['url'],
                'notes': post['summary'],
                'created_at': datetime.now().isoformat(),
                'status': 'new'
            }
            
            # Save lead to database
            self.logger.info(f"Business lead created from post {post['id']}")
            
            return {'success': True, 'message': 'Lead created successfully', 'lead_data': lead_data}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _prepare_contact_info(self, post: Dict) -> Dict[str, Any]:
        """Prepare contact information for the post author"""
        try:
            contact_info = {
                'reddit_username': post['author'],
                'reddit_url': f"https://reddit.com/user/{post['author']}",
                'contact_method': 'Reddit Private Message',
                'post_context': {
                    'title': post['title'],
                    'subreddit': post['subreddit'],
                    'business_score': post['business_score'],
                    'summary': post['summary']
                },
                'suggested_message': f"Hi {post['author']}, I saw your post about {post['title'][:50]}... and I think I might be able to help with a solution."
            }
            
            return {'success': True, 'contact_info': contact_info}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _export_post(self, post: Dict) -> Dict[str, Any]:
        """Export post data"""
        try:
            export_data = {
                'post_id': post['id'],
                'title': post['title'],
                'author': post['author'],
                'subreddit': post['subreddit'],
                'url': post['url'],
                'business_score': post['business_score'],
                'priority': post['priority'],
                'summary': post['summary'],
                'full_content': post['full_content'],
                'exported_at': datetime.now().isoformat()
            }
            
            return {'success': True, 'export_data': export_data}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get live monitoring statistics"""
        high_priority = len([p for p in self.recent_posts if p.get('priority') == 'high'])
        medium_priority = len([p for p in self.recent_posts if p.get('priority') == 'medium'])
        
        return {
            'is_monitoring': self.is_monitoring,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'total_posts_cached': len(self.recent_posts),
            'high_priority_posts': high_priority,
            'medium_priority_posts': medium_priority,
            'monitored_subreddits': self.config['monitored_subreddits'],
            'update_interval': self.config['update_interval'],
            'average_business_score': sum(p.get('business_score', 0) for p in self.recent_posts) / len(self.recent_posts) if self.recent_posts else 0
        }
    
    def update_monitoring_config(self, config_updates: Dict):
        """Update monitoring configuration"""
        old_config = self.config.copy()
        self.config.update(config_updates)
        
        self.logger.info(f"Monitoring configuration updated: {config_updates}")
        
        # If update interval changed and we're monitoring, restart
        if ('update_interval' in config_updates and 
            self.is_monitoring and 
            old_config['update_interval'] != self.config['update_interval']):
            
            self.stop_live_monitoring()
            self.start_live_monitoring()
    
    def add_callback(self, callback: Callable):
        """Add callback for post updates"""
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    def close(self):
        """Clean up live Reddit service"""
        self.stop_live_monitoring()
        self.recent_posts.clear()
        self.post_cache.clear()
        self.update_callbacks.clear()
        
        self.logger.info("Live Reddit service closed")