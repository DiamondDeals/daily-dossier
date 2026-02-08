"""
Live View - Enhanced Reddit Experience for PersonalizedReddit
Real-time Reddit browsing with AI analysis and quick actions
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

from ui.views.base_view import BaseView
from utils.logging_config import get_logger

class LiveView(BaseView):
    """
    Live view for enhanced Reddit browsing experience
    Matches the design from PersonalizedReddit_Live_Mockup.png
    """
    
    def __init__(self, parent, app, services: Dict[str, Any], colors: Dict[str, str]):
        super().__init__(parent, app, services, colors)
        
        # Live monitoring state
        self.is_monitoring = False
        self.current_posts = []
        self.selected_filters = {'Business': True}
        
        # Set auto-refresh for live updates
        self.set_auto_refresh(30)  # 30 seconds for live updates
    
    def _initialize_view(self):
        """Initialize the live view components"""
        try:
            # Create main container
            self.main_frame = ctk.CTkFrame(
                self,
                fg_color=self.colors['bg_primary'],
                corner_radius=0
            )
            self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.main_frame.grid_columnconfigure(1, weight=1)
            self.main_frame.grid_rowconfigure(2, weight=1)
            
            # Header section
            self._create_header_section()
            
            # Live status and controls
            self._create_live_controls()
            
            # Filters and content area
            self._create_content_area()
            
            # Notification area
            self._create_notification_area()
            
            # Start with some mock data
            self._load_mock_data()
            
            self.logger.info("Live view initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize live view: {e}", exc_info=True)
            raise
    
    def _create_header_section(self):
        """Create the main header section"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Main title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Live - Enhanced Reddit Experience",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Real-time Updates • Quick Actions • Multi-Account",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
    
    def _create_live_controls(self):
        """Create live monitoring controls"""
        controls_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['accent_green'],
            corner_radius=10,
            height=60
        )
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_propagate(False)
        
        # Live indicator
        live_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        live_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        live_dot = ctk.CTkLabel(
            live_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="white"
        )
        live_dot.pack(side="left")
        
        self.live_status_label = ctk.CTkLabel(
            live_frame,
            text="LIVE - Real-time updates enabled",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.live_status_label.pack(side="left", padx=(10, 0))
        
        # Account selector
        account_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        account_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        
        account_label = ctk.CTkLabel(
            account_frame,
            text="Account:",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        account_label.pack(side="left")
        
        self.account_menu = ctk.CTkOptionMenu(
            account_frame,
            values=["DrewR_Business", "Personal", "Add Account..."],
            font=ctk.CTkFont(size=12),
            fg_color="white",
            text_color=self.colors['text_primary'],
            button_color=self.colors['accent_green']
        )
        self.account_menu.pack(side="left", padx=(10, 0))
        self.account_menu.set("DrewR_Business ▼")
    
    def _create_content_area(self):
        """Create the main content area with filters and posts"""
        # Filter tabs
        self._create_filter_tabs()
        
        # Content container
        content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_container.grid(row=2, column=0, columnspan=2, sticky="nsew")
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_columnconfigure(1, weight=0)
        content_container.grid_rowconfigure(0, weight=1)
        
        # Posts area (left side)
        posts_frame = ctk.CTkFrame(
            content_container,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        posts_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        posts_frame.grid_columnconfigure(0, weight=1)
        posts_frame.grid_rowconfigure(0, weight=1)
        
        # Posts scrollable area
        self.posts_scrollable = ctk.CTkScrollableFrame(
            posts_frame,
            fg_color="transparent"
        )
        self.posts_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.posts_scrollable.grid_columnconfigure(0, weight=1)
        
        # AI Analysis sidebar (right side)
        self._create_ai_sidebar(content_container)
    
    def _create_filter_tabs(self):
        """Create filter tab buttons"""
        filters_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filters_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        filters_frame.grid_columnconfigure(5, weight=1)  # Spacer
        
        filter_tabs = [
            ("Hot", "hot", False),
            ("Rising", "rising", False),
            ("New", "new", False),
            ("Top", "top", False),
            ("Business", "business", True),
            ("Automation", "automation", False)
        ]
        
        self.filter_buttons = {}
        
        for i, (name, key, active) in enumerate(filter_tabs):
            # Skip the live controls row
            if i >= 5:  # Adjust positioning
                continue
                
            color = self.colors['accent_blue'] if active else self.colors['bg_tertiary']
            icon = "📈" if name == "Rising" else "🔥" if name == "Hot" else \
                  "🆕" if name == "New" else "⭐" if name == "Top" else \
                  "💼" if name == "Business" else "🤖"
            
            button = ctk.CTkButton(
                filters_frame,
                text=f"{icon} {name}",
                font=ctk.CTkFont(size=12),
                fg_color=color,
                hover_color=self.colors['accent_blue'],
                width=100,
                height=35,
                command=lambda k=key: self._filter_posts(k)
            )
            button.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            self.filter_buttons[key] = button
    
    def _create_ai_sidebar(self, parent):
        """Create AI analysis sidebar"""
        sidebar_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10,
            width=300
        )
        sidebar_frame.grid(row=0, column=1, sticky="nsew")
        sidebar_frame.grid_columnconfigure(0, weight=1)
        sidebar_frame.grid_propagate(False)
        
        # AI Analysis header
        ai_header = ctk.CTkLabel(
            sidebar_frame,
            text="🤖 AI Analysis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        ai_header.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Business Score section
        score_frame = ctk.CTkFrame(sidebar_frame, fg_color=self.colors['bg_tertiary'])
        score_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        score_frame.grid_columnconfigure(0, weight=1)
        
        score_title = ctk.CTkLabel(
            score_frame,
            text="Business Score: 9.2/10",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['accent_green']
        )
        score_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # Keywords Found section
        keywords_label = ctk.CTkLabel(
            score_frame,
            text="Keywords Found:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        keywords_label.grid(row=1, column=0, padx=15, pady=(10, 5), sticky="w")
        
        keywords_text = "• Manual tracking\n• 6 hours daily\n• Automation needed"
        keywords_content = ctk.CTkLabel(
            score_frame,
            text=keywords_text,
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        keywords_content.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(sidebar_frame, fg_color=self.colors['bg_tertiary'])
        actions_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        actions_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # Action buttons
        action_buttons = [
            ("💾 Save", self._save_post),
            ("🎯 Lead", self._create_lead),
            ("💬 Contact", self._contact_author),
            ("📤 Export", self._export_post)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            button = ctk.CTkButton(
                actions_frame,
                text=text,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors['accent_blue'],
                hover_color=self._get_hover_color(self.colors['accent_blue']),
                height=30,
                width=120,
                command=command
            )
            button.grid(row=i+1, column=0, padx=15, pady=2, sticky="w")
    
    def _create_notification_area(self):
        """Create bottom notification area"""
        self.notification_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['accent_blue'],
            corner_radius=10,
            height=50
        )
        self.notification_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        self.notification_frame.grid_columnconfigure(1, weight=1)
        self.notification_frame.grid_propagate(False)
        
        notification_icon = ctk.CTkLabel(
            self.notification_frame,
            text="🔔",
            font=ctk.CTkFont(size=18),
            text_color="white"
        )
        notification_icon.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="3 new high-priority leads detected",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.notification_label.grid(row=0, column=1, sticky="w", pady=15)
    
    def _load_mock_data(self):
        """Load mock post data for demonstration"""
        mock_posts = [
            {
                'id': '1',
                'title': 'Help! Spending 6 hours daily on manual inventory tracking',
                'author': 'smallbiz_owner',
                'subreddit': 'entrepreneur',
                'score': 47,
                'num_comments': 23,
                'time_ago': '5 minutes ago',
                'priority': 'high',
                'business_score': 9.2,
                'content_preview': 'Small retail business owner struggling with Excel-based inventory system. Currently updating stock levels manually across 3 locations. Looking for affordable automation solution...'
            },
            {
                'id': '2', 
                'title': 'Anyone know good tools for client follow-up automation?',
                'author': 'freelancer_pro',
                'subreddit': 'smallbusiness',
                'score': 23,
                'num_comments': 8,
                'time_ago': '23 minutes ago',
                'priority': 'medium',
                'business_score': 6.8,
                'content_preview': 'Running a service business and manually tracking client communications. Need something to automate follow-up emails and reminders...'
            }
        ]
        
        self.current_posts = mock_posts
        self._display_posts(mock_posts)
    
    def _display_posts(self, posts: List[Dict]):
        """Display posts in the scrollable area"""
        # Clear existing posts
        for widget in self.posts_scrollable.winfo_children():
            widget.destroy()
        
        for i, post in enumerate(posts):
            self._create_post_card(self.posts_scrollable, post, i)
    
    def _create_post_card(self, parent, post: Dict, row: int):
        """Create individual post card"""
        # Priority colors
        priority_colors = {
            'high': self.colors['accent_orange'],
            'medium': '#FFA726',
            'low': self.colors['text_secondary']
        }
        
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_primary'],
            corner_radius=10,
            border_width=2,
            border_color=priority_colors.get(post['priority'], self.colors['border'])
        )
        card.grid(row=row, column=0, sticky="ew", padx=5, pady=10)
        card.grid_columnconfigure(0, weight=1)
        
        # Priority badge
        priority_frame = ctk.CTkFrame(card, fg_color="transparent")
        priority_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        priority_badge = ctk.CTkLabel(
            priority_frame,
            text=f"{post['priority'].upper()} PRIORITY",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=priority_colors[post['priority']],
            text_color="white",
            corner_radius=10,
            width=100,
            height=20
        )
        priority_badge.pack(side="left")
        
        # Post info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        subreddit_label = ctk.CTkLabel(
            info_frame,
            text=f"r/{post['subreddit']} • Posted {post['time_ago']}",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        subreddit_label.pack(side="left")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=post['title'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary'],
            wraplength=600,
            justify="left"
        )
        title_label.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Content preview
        if post.get('content_preview'):
            content_text = ctk.CTkTextbox(
                card,
                height=60,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors['bg_tertiary'],
                text_color=self.colors['text_primary']
            )
            content_text.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 10))
            content_text.insert("0.0", post['content_preview'])
            content_text.configure(state="disabled")
        
        # Engagement metrics
        metrics_frame = ctk.CTkFrame(card, fg_color="transparent")
        metrics_frame.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        score_label = ctk.CTkLabel(
            metrics_frame,
            text=f"⬆ {post['score']}",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        score_label.pack(side="left")
        
        comments_label = ctk.CTkLabel(
            metrics_frame,
            text=f"💬 {post['num_comments']}",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        comments_label.pack(side="left", padx=(20, 0))
        
        # Quick action buttons
        actions_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        for action in ["Save", "Lead", "Contact"]:
            button = ctk.CTkButton(
                actions_frame,
                text=action,
                font=ctk.CTkFont(size=10),
                fg_color=self.colors['accent_blue'],
                hover_color=self._get_hover_color(self.colors['accent_blue']),
                width=50,
                height=25,
                command=lambda a=action, p=post: self._perform_quick_action(a, p)
            )
            button.pack(side="left", padx=2)
    
    def refresh_data(self):
        """Refresh live view data"""
        try:
            self.logger.info("Refreshing live view data")
            
            # In a real implementation, this would fetch fresh data from the live service
            live_service = self.get_service('live_reddit')
            if live_service:
                # Get recent posts
                posts = live_service.get_live_posts(20)
                if posts:
                    self.current_posts = posts
                    self._display_posts(posts)
                    self._update_notification(f"{len(posts)} posts updated")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh live data: {e}")
            self._show_error_message(f"Failed to refresh: {e}")
    
    def _filter_posts(self, filter_key: str):
        """Filter posts by category"""
        self.logger.info(f"Filtering posts by: {filter_key}")
        
        # Update button states
        for key, button in self.filter_buttons.items():
            if key == filter_key:
                button.configure(fg_color=self.colors['accent_blue'])
                self.selected_filters[key] = True
            else:
                button.configure(fg_color=self.colors['bg_tertiary'])
                self.selected_filters[key] = False
        
        # Apply filter (in real implementation, this would filter the posts)
        self._show_success_message(f"Filtered by: {filter_key}")
    
    def _update_notification(self, message: str):
        """Update the notification area"""
        self.notification_label.configure(text=message)
    
    def _get_hover_color(self, color: str) -> str:
        """Get hover color for buttons"""
        return '#3d7bd9' if color == self.colors['accent_blue'] else color
    
    # Quick action handlers
    def _save_post(self):
        """Save post action"""
        self._show_success_message("Post saved for later review")
    
    def _create_lead(self):
        """Create lead action"""
        self._show_success_message("Lead created from post")
    
    def _contact_author(self):
        """Contact author action"""
        self._show_success_message("Contact initiated with author")
    
    def _export_post(self):
        """Export post action"""
        if self.current_posts:
            self.export_data(self.current_posts, "live_posts", "csv")
    
    def _perform_quick_action(self, action: str, post: Dict):
        """Perform quick action on specific post"""
        self.logger.info(f"Performing {action} on post {post['id']}")
        
        if action == "Save":
            self._save_post()
        elif action == "Lead":
            self._create_lead()
        elif action == "Contact":
            self._contact_author()
    
    def show(self):
        """Show the live view and start monitoring"""
        super().show()
        if not self.is_monitoring:
            self._start_live_monitoring()
    
    def hide(self):
        """Hide the live view and stop monitoring"""
        super().hide()
        if self.is_monitoring:
            self._stop_live_monitoring()
    
    def _start_live_monitoring(self):
        """Start live monitoring"""
        self.is_monitoring = True
        live_service = self.get_service('live_reddit')
        if live_service:
            live_service.start_live_monitoring(self._handle_live_update)
        
        self.live_status_label.configure(text="LIVE - Real-time updates enabled")
    
    def _stop_live_monitoring(self):
        """Stop live monitoring"""
        self.is_monitoring = False
        live_service = self.get_service('live_reddit')
        if live_service:
            live_service.stop_live_monitoring()
    
    def _handle_live_update(self, new_posts: List[Dict]):
        """Handle live update callback"""
        if new_posts:
            # Update posts in UI thread
            self.after(0, lambda: self._process_live_posts(new_posts))
    
    def _process_live_posts(self, new_posts: List[Dict]):
        """Process new live posts"""
        high_priority_count = len([p for p in new_posts if p.get('priority') == 'high'])
        if high_priority_count > 0:
            self._update_notification(f"{high_priority_count} new high-priority leads detected")
        
        # Add new posts to current posts
        self.current_posts = new_posts + self.current_posts[:50]  # Keep last 50
        self._display_posts(self.current_posts)
    
    def cleanup(self):
        """Clean up live view resources"""
        self._stop_live_monitoring()
        super().cleanup()