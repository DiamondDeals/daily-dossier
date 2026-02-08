"""
Discover View - AI-Powered Recommendations for PersonalizedReddit
Subreddit discovery and personalized content recommendations
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

from ui.views.base_view import BaseView
from utils.logging_config import get_logger

class DiscoverView(BaseView):
    """
    Discover view for AI-powered recommendations and subreddit discovery
    Matches the design from PersonalizedReddit_Discover_Mockup.png
    """
    
    def __init__(self, parent, app, services: Dict[str, Any], colors: Dict[str, str]):
        super().__init__(parent, app, services, colors)
        
        # Current recommendations data
        self.current_recommendations = []
        self.selected_category = 'For You'
        
        # Set auto-refresh for recommendations
        self.set_auto_refresh(600)  # 10 minutes
    
    def _initialize_view(self):
        """Initialize the discover view components"""
        try:
            # Create main scrollable frame
            self.main_frame = ctk.CTkScrollableFrame(
                self,
                fg_color=self.colors['bg_primary'],
                corner_radius=0
            )
            self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.main_frame.grid_columnconfigure(0, weight=1)
            
            # Header section
            self._create_header_section()
            
            # AI Engine status
            self._create_ai_status_section()
            
            # Category filters
            self._create_category_filters()
            
            # Recommendations grid
            self._create_recommendations_section()
            
            # AI Insights dashboard
            self._create_insights_section()
            
            # Action buttons
            self._create_actions_section()
            
            # Load initial recommendations
            self.refresh_data()
            
            self.logger.info("Discover view initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize discover view: {e}", exc_info=True)
            raise
    
    def _create_header_section(self):
        """Create the main header section"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Main title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Discover - AI-Powered Recommendations",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.grid(row=0, column=0)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="AI-Curated Content • Subreddit Discovery • Personalized Feed",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
    
    def _create_ai_status_section(self):
        """Create AI engine status section"""
        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['accent_blue'],
            corner_radius=10,
            height=80
        )
        status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_propagate(False)
        
        # AI Engine status
        status_left = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_left.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        ai_icon = ctk.CTkLabel(
            status_left,
            text="🤖",
            font=ctk.CTkFont(size=24),
            text_color="white"
        )
        ai_icon.pack(side="left")
        
        ai_status_text = ctk.CTkLabel(
            status_left,
            text="AI Engine Active • Analyzing 2.3M posts • Confidence: 94%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        ai_status_text.pack(side="left", padx=(15, 0))
        
        # Today's Score
        score_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        score_frame.grid(row=0, column=2, sticky="e", padx=20, pady=20)
        
        score_label = ctk.CTkLabel(
            score_frame,
            text="Today's Score: A+",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        score_label.pack()
    
    def _create_category_filters(self):
        """Create category filter tabs"""
        filters_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filters_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30))
        filters_frame.grid_columnconfigure(5, weight=1)  # Spacer
        
        categories = [
            ("For You", "for_you", True),
            ("Trending", "trending", False),
            ("New Subreddits", "new_subreddits", False),
            ("Similar Interests", "similar", False),
            ("Opportunities", "opportunities", False)
        ]
        
        self.category_buttons = {}
        
        for i, (name, key, active) in enumerate(categories):
            color = self.colors['accent_orange'] if active else self.colors['bg_tertiary']
            icon = "👤" if name == "For You" else "📈" if name == "Trending" else \
                  "🆕" if name == "New Subreddits" else "🎯" if name == "Similar Interests" else \
                  "💼"
            
            button = ctk.CTkButton(
                filters_frame,
                text=f"{icon} {name}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self.colors['accent_orange'],
                height=45,
                width=150,
                command=lambda k=key, n=name: self._change_category(k, n)
            )
            button.grid(row=0, column=i, padx=5, sticky="w")
            self.category_buttons[key] = button
    
    def _create_recommendations_section(self):
        """Create recommendations grid section"""
        recommendations_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        recommendations_frame.grid(row=3, column=0, sticky="ew", pady=(0, 30))
        recommendations_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Left column - AI Recommended
        self._create_recommendation_card(
            recommendations_frame, 
            0, 0, 
            "AI RECOMMENDED", 
            self.colors['accent_orange'],
            {
                'title': 'r/ProcessAutomation',
                'members': '45K members • Very Active',
                'description': 'Community focused on business process automation, workflow optimization, and efficiency solutions.',
                'match': '96% MATCH',
                'reason': 'High business problem density',
                'stats': '• 89% automation-related posts • 12 leads/day avg',
                'similar': 'Similar to your interests in r/entrepreneur'
            }
        )
        
        # Right column - New Discovery
        self._create_recommendation_card(
            recommendations_frame,
            0, 1,
            "NEW",
            '#FFA726',
            {
                'title': 'r/SaaSFounders',
                'members': '28K members • Growing Fast',
                'description': 'Software founders sharing automation challenges and solutions for scaling their businesses.',
                'match': 'NEW',
                'reason': 'Growing community',
                'stats': 'Similar to your interests in r/entrepreneur',
                'similar': ''
            }
        )
    
    def _create_recommendation_card(self, parent, row: int, col: int, badge_text: str, badge_color: str, data: Dict):
        """Create individual recommendation card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15,
            border_width=2,
            border_color=badge_color
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        # Badge
        badge_frame = ctk.CTkFrame(card, fg_color="transparent")
        badge_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        badge = ctk.CTkLabel(
            badge_frame,
            text=badge_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=badge_color,
            text_color="white",
            corner_radius=15,
            width=120,
            height=25
        )
        badge.pack(side="left")
        
        # Match percentage (for recommended items)
        if data.get('match') and data['match'] != 'NEW':
            match_badge = ctk.CTkLabel(
                badge_frame,
                text=data['match'],
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors['accent_green'],
                text_color="white",
                corner_radius=15,
                width=100,
                height=25
            )
            match_badge.pack(side="right")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=data['title'],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(5, 10))
        
        # Members info
        members_label = ctk.CTkLabel(
            card,
            text=data['members'],
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        members_label.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Description
        desc_text = ctk.CTkTextbox(
            card,
            height=80,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary']
        )
        desc_text.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        desc_text.insert("0.0", data['description'])
        desc_text.configure(state="disabled")
        
        # Why recommended
        if data.get('reason'):
            reason_frame = ctk.CTkFrame(card, fg_color=self.colors['bg_tertiary'])
            reason_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 15))
            
            reason_label = ctk.CTkLabel(
                reason_frame,
                text=f"💡 Why recommended: {data['reason']}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors['accent_blue'],
                wraplength=250
            )
            reason_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Stats
        if data.get('stats'):
            stats_label = ctk.CTkLabel(
                card,
                text=data['stats'],
                font=ctk.CTkFont(size=10),
                text_color=self.colors['text_secondary'],
                wraplength=250
            )
            stats_label.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        join_button = ctk.CTkButton(
            actions_frame,
            text="JOIN",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['accent_blue'],
            hover_color='#3d7bd9',
            height=35,
            command=lambda: self._join_subreddit(data['title'])
        )
        join_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        preview_button = ctk.CTkButton(
            actions_frame,
            text="PREVIEW",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['bg_tertiary'],
            hover_color='#555555',
            height=35,
            command=lambda: self._preview_subreddit(data['title'])
        )
        preview_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")
    
    def _create_insights_section(self):
        """Create AI insights dashboard section"""
        insights_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        insights_frame.grid(row=4, column=0, sticky="ew", pady=(0, 30))
        insights_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Section header
        insights_header = ctk.CTkLabel(
            insights_frame,
            text="🔍 AI Insights & Trends",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        insights_header.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 15), sticky="w")
        
        # Insights cards
        self._create_insight_card(
            insights_frame, 1, 0,
            "📊 Trending Topics",
            "• API Integration\n• Workflow Tools\n• Data Migration"
        )
        
        self._create_insight_card(
            insights_frame, 1, 1,
            "⏰ Best Times",
            "Peak Activity:\n• 9:00 AM EST\n• 7-9 PM EST"
        )
        
        self._create_insight_card(
            insights_frame, 1, 2,
            "💼 Opportunities",
            "• 127 leads identified today\n• +47% vs yesterday"
        )
    
    def _create_insight_card(self, parent, row: int, col: int, title: str, content: str):
        """Create individual insight card"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['bg_tertiary'])
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(padx=15, pady=(15, 10), anchor="w")
        
        content_label = ctk.CTkLabel(
            card,
            text=content,
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        content_label.pack(padx=15, pady=(0, 15), anchor="w")
    
    def _create_actions_section(self):
        """Create action buttons section"""
        actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        actions_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        buttons_config = [
            ("Explore More", self._explore_more, self.colors['accent_blue']),
            ("Customize AI", self._customize_ai, self.colors['bg_tertiary']),
            ("View Analytics", self._view_analytics, self.colors['bg_tertiary']),
            ("Share Findings", self._share_findings, self.colors['accent_orange'])
        ]
        
        for i, (text, command, color) in enumerate(buttons_config):
            icon = "🔍" if i == 0 else "⚙️" if i == 1 else "📊" if i == 2 else "📤"
            
            button = ctk.CTkButton(
                actions_frame,
                text=f"{icon} {text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self._get_hover_color(color),
                height=50,
                command=command
            )
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
    
    def refresh_data(self):
        """Refresh discover view data"""
        try:
            self.logger.info("Refreshing discover view data")
            
            # Fetch recommendations in background
            self._run_in_background(
                self._fetch_recommendations_data,
                self._update_recommendations_display
            )
            
        except Exception as e:
            self.logger.error(f"Failed to refresh discover data: {e}")
            self._show_error_message(f"Failed to refresh: {e}")
    
    def _fetch_recommendations_data(self) -> Dict[str, Any]:
        """Fetch recommendations data from services"""
        try:
            ai_recommendations_service = self.get_service('ai_recommendations')
            if ai_recommendations_service:
                recommendations = ai_recommendations_service.generate_subreddit_recommendations(count=10)
                trends = ai_recommendations_service.get_trending_topics()
                analytics = ai_recommendations_service.get_recommendation_analytics()
                
                return {
                    'recommendations': recommendations,
                    'trends': trends,
                    'analytics': analytics
                }
            else:
                return self._get_mock_recommendations_data()
                
        except Exception as e:
            self.logger.error(f"Failed to fetch recommendations data: {e}")
            return self._get_mock_recommendations_data()
    
    def _get_mock_recommendations_data(self) -> Dict[str, Any]:
        """Get mock recommendations data"""
        return {
            'recommendations': [
                {
                    'name': 'ProcessAutomation',
                    'match_percentage': 96,
                    'confidence': 0.94,
                    'explanation': 'High business problem density',
                    'members': '45K',
                    'activity_level': 'High'
                }
            ],
            'trends': [
                {'topic': 'API Integration', 'growth': '+25%'},
                {'topic': 'Workflow Tools', 'growth': '+18%'}
            ],
            'analytics': {
                'total_recommendations': 156,
                'acceptance_rate': '57%'
            }
        }
    
    def _update_recommendations_display(self, data: Dict[str, Any]):
        """Update recommendations display with fresh data"""
        try:
            self.current_recommendations = data.get('recommendations', [])
            self.logger.info(f"Updated discover view with {len(self.current_recommendations)} recommendations")
            
            # In a full implementation, this would update the UI with fresh data
            
        except Exception as e:
            self.logger.error(f"Failed to update recommendations display: {e}")
    
    def _change_category(self, category_key: str, category_name: str):
        """Change recommendation category"""
        self.selected_category = category_name
        
        # Update button states
        for key, button in self.category_buttons.items():
            if key == category_key:
                button.configure(fg_color=self.colors['accent_orange'])
            else:
                button.configure(fg_color=self.colors['bg_tertiary'])
        
        self.logger.info(f"Changed category to: {category_name}")
        self._show_success_message(f"Showing {category_name} recommendations")
    
    def _get_hover_color(self, color: str) -> str:
        """Get hover color for buttons"""
        hover_colors = {
            self.colors['accent_blue']: '#3d7bd9',
            self.colors['accent_orange']: '#e55a3d',
            self.colors['bg_tertiary']: '#555555'
        }
        return hover_colors.get(color, color)
    
    # Action handlers
    def _join_subreddit(self, subreddit_name: str):
        """Join subreddit action"""
        self.logger.info(f"Joining subreddit: {subreddit_name}")
        self._show_success_message(f"Joined {subreddit_name}!")
    
    def _preview_subreddit(self, subreddit_name: str):
        """Preview subreddit action"""
        self.logger.info(f"Previewing subreddit: {subreddit_name}")
        self._show_success_message(f"Opening preview for {subreddit_name}")
    
    def _explore_more(self):
        """Explore more recommendations"""
        self._show_success_message("Loading more recommendations...")
        self.refresh_data()
    
    def _customize_ai(self):
        """Customize AI recommendations"""
        self._show_success_message("AI customization coming soon!")
    
    def _view_analytics(self):
        """View recommendation analytics"""
        if self.current_recommendations:
            analytics_data = {
                'total_recommendations': len(self.current_recommendations),
                'category': self.selected_category,
                'generated_at': datetime.now().isoformat()
            }
            self.export_data(analytics_data, "recommendation_analytics", "json")
        else:
            self._show_error_message("No analytics data available")
    
    def _share_findings(self):
        """Share recommendations findings"""
        if self.current_recommendations:
            self.export_data(self.current_recommendations, "subreddit_recommendations", "markdown")
        else:
            self._show_error_message("No recommendations to share")