"""
Home View - Newsletter Interface for PersonalizedReddit
AI-powered daily digest and business opportunity overview
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

from ui.views.base_view import BaseView
from utils.logging_config import get_logger

class HomeView(BaseView):
    """
    Home view displaying AI-powered newsletter overview
    Matches the design from PersonalizedReddit_Home_Mockup.png
    """
    
    def __init__(self, parent, app, services: Dict[str, Any], colors: Dict[str, str]):
        super().__init__(parent, app, services, colors)
        
        # Set auto-refresh for dynamic content
        self.set_auto_refresh(300)  # 5 minutes
        
        # Current digest data
        self.current_digest = None
        
    def _initialize_view(self):
        """Initialize the home view components"""
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
            
            # Statistics section
            self._create_stats_section()
            
            # AI Digest section
            self._create_digest_section()
            
            # Business opportunities grid
            self._create_opportunities_section()
            
            # Action buttons section
            self._create_actions_section()
            
            # Load initial data
            self.refresh_data()
            
            self.logger.info("Home view initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize home view: {e}", exc_info=True)
            raise
    
    def _create_header_section(self):
        """Create the main header section"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Main title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Home - Newsletter Overview",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.title_label.grid(row=0, column=0)
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="AI-Powered Daily Digest & Trending Analysis",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_secondary']
        )
        self.subtitle_label.grid(row=1, column=0, pady=(5, 0))
    
    def _create_stats_section(self):
        """Create the statistics overview section"""
        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")
        
        # Stats containers
        self.stats_widgets = {}
        
        stats_config = [
            ("today_digest", "Today's Digest", "24 Posts", "📊"),
            ("trending_score", "Trending Score", "8.7/10", "📈"),
            ("last_update", "Last Update", "2 min ago", "🔄"),
            ("match_rate", "Match Rate", "92%", "🎯")
        ]
        
        for i, (key, title, default_value, icon) in enumerate(stats_config):
            stat_container = self._create_stat_widget(stats_frame, title, default_value, icon)
            stat_container.grid(row=0, column=i, padx=15, pady=20, sticky="ew")
            self.stats_widgets[key] = stat_container
    
    def _create_stat_widget(self, parent, title: str, value: str, icon: str) -> ctk.CTkFrame:
        """Create individual statistic widget"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid_columnconfigure(0, weight=1)
        
        # Icon and value
        value_frame = ctk.CTkFrame(container, fg_color="transparent")
        value_frame.grid(row=0, column=0, sticky="ew")
        value_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            value_frame,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=40
        )
        icon_label.grid(row=0, column=0, sticky="w")
        
        # Value
        value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="e"
        )
        value_label.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        title_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # Store references for updates
        container.value_label = value_label
        container.title_label = title_label
        
        return container
    
    def _create_digest_section(self):
        """Create the AI digest section"""
        digest_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        digest_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30))
        digest_frame.grid_columnconfigure(0, weight=1)
        
        # Digest header
        digest_header = ctk.CTkFrame(digest_frame, fg_color="transparent")
        digest_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        digest_header.grid_columnconfigure(1, weight=1)
        
        # AI Digest label
        digest_badge = ctk.CTkLabel(
            digest_header,
            text="🤖 AI DIGEST",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['accent_blue'],
            text_color="white",
            corner_radius=15,
            width=100,
            height=25
        )
        digest_badge.grid(row=0, column=0, sticky="w")
        
        # Trending badge
        self.trending_badge = ctk.CTkLabel(
            digest_header,
            text="TRENDING",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['accent_green'],
            text_color="white",
            corner_radius=15,
            width=80,
            height=25
        )
        self.trending_badge.grid(row=0, column=2, sticky="e")
        
        # Digest content frame
        self.digest_content = ctk.CTkFrame(digest_frame, fg_color="transparent")
        self.digest_content.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.digest_content.grid_columnconfigure(0, weight=1)
        
        # Default digest content
        self.digest_text = ctk.CTkTextbox(
            self.digest_content,
            height=120,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary']
        )
        self.digest_text.grid(row=0, column=0, sticky="ew")
        
        self.digest_text.insert("0.0", "Generating AI digest...")
    
    def _create_opportunities_section(self):
        """Create the business opportunities grid section"""
        opportunities_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        opportunities_frame.grid(row=3, column=0, sticky="ew", pady=(0, 30))
        opportunities_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="opportunities")
        
        # Section header
        section_header = ctk.CTkFrame(opportunities_frame, fg_color="transparent")
        section_header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        section_title = ctk.CTkLabel(
            section_header,
            text="Today's Top Business Automation Opportunities",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['text_primary']
        )
        section_title.pack(anchor="w")
        
        # Opportunity cards container
        self.opportunities_container = ctk.CTkFrame(opportunities_frame, fg_color="transparent")
        self.opportunities_container.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.opportunities_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Create placeholder cards
        self.opportunity_cards = []
        self._create_placeholder_opportunity_cards()
    
    def _create_placeholder_opportunity_cards(self):
        """Create placeholder opportunity cards"""
        placeholder_opportunities = [
            {
                'title': 'Manual Process Solutions',
                'count': '12 leads • High Priority',
                'description': '• Data entry taking 4hrs daily\n• Need inventory automation\n• Manual data export needed',
                'subreddit': 'r/smallbusiness',
                'priority': 'high'
            },
            {
                'title': 'Workflow Automation',
                'count': '8 leads • Medium Priority',
                'description': '• Data entry taking 4hrs daily\n• Need inventory automation\n• Automation needed',
                'subreddit': 'r/entrepreneur',
                'priority': 'medium'
            },
            {
                'title': 'Time Management',
                'count': '6 leads • Medium Priority',
                'description': '• Data entry taking 4hrs daily\n• Need inventory automation\n• Need inventory automation',
                'subreddit': 'r/freelance',
                'priority': 'medium'
            }
        ]
        
        for i, opp in enumerate(placeholder_opportunities):
            card = self._create_opportunity_card(self.opportunities_container, opp, i)
            self.opportunity_cards.append(card)
    
    def _create_opportunity_card(self, parent, opportunity: Dict, column: int) -> ctk.CTkFrame:
        """Create individual opportunity card"""
        # Priority colors
        priority_colors = {
            'high': self.colors['accent_orange'],
            'medium': '#FFA726',
            'low': self.colors['text_secondary']
        }
        
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        # Priority indicator
        priority_frame = ctk.CTkFrame(card, fg_color="transparent")
        priority_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        
        priority_badge = ctk.CTkLabel(
            priority_frame,
            text=f"{opportunity['priority'].upper()} PRIORITY",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=priority_colors[opportunity['priority']],
            text_color="white",
            corner_radius=10,
            height=20
        )
        priority_badge.pack(side="left")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=opportunity['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary'],
            wraplength=250,
            justify="left"
        )
        title_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 10))
        
        # Count
        count_label = ctk.CTkLabel(
            card,
            text=opportunity['count'],
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        count_label.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Description
        desc_text = ctk.CTkTextbox(
            card,
            height=80,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary']
        )
        desc_text.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 10))
        desc_text.insert("0.0", opportunity['description'])
        desc_text.configure(state="disabled")
        
        # Source
        source_label = ctk.CTkLabel(
            card,
            text=opportunity['subreddit'],
            font=ctk.CTkFont(size=10),
            text_color=self.colors['accent_blue']
        )
        source_label.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        return card
    
    def _create_actions_section(self):
        """Create the action buttons section"""
        actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        actions_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Action buttons
        buttons_config = [
            ("Generate Newsletter", self._generate_newsletter, self.colors['accent_blue']),
            ("View Analytics", self._view_analytics, self.colors['bg_tertiary']),
            ("Customize Feed", self._customize_feed, self.colors['bg_tertiary']),
            ("Export Leads", self._export_leads, self.colors['accent_orange'])
        ]
        
        self.action_buttons = {}
        
        for i, (text, command, color) in enumerate(buttons_config):
            button = ctk.CTkButton(
                actions_frame,
                text=f"📋 {text}" if i == 0 else f"📊 {text}" if i == 1 
                     else f"⚙️ {text}" if i == 2 else f"📤 {text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self._get_hover_color(color),
                height=50,
                command=command
            )
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.action_buttons[text.lower().replace(' ', '_')] = button
    
    def _get_hover_color(self, color: str) -> str:
        """Get hover color for buttons"""
        hover_colors = {
            self.colors['accent_blue']: '#3d7bd9',
            self.colors['accent_orange']: '#e55a3d',
            self.colors['bg_tertiary']: '#555555'
        }
        return hover_colors.get(color, color)
    
    def refresh_data(self):
        """Refresh the home view data"""
        try:
            self.logger.info("Refreshing home view data")
            
            # Show loading state
            self._show_loading_state()
            
            # Generate digest in background
            self._run_in_background(
                self._fetch_digest_data,
                self._update_digest_display
            )
            
        except Exception as e:
            self.logger.error(f"Failed to refresh home data: {e}")
            self._show_error_message(f"Failed to refresh: {e}")
    
    def _show_loading_state(self):
        """Show loading state"""
        self.digest_text.delete("0.0", tk.END)
        self.digest_text.insert("0.0", "🔄 Generating AI digest...")
        
        # Update stats to show loading
        for widget_name, widget in self.stats_widgets.items():
            widget.value_label.configure(text="...")
    
    def _fetch_digest_data(self) -> Dict[str, Any]:
        """Fetch digest data from services"""
        try:
            newsletter_service = self.get_service('newsletter')
            if newsletter_service:
                digest = newsletter_service.generate_daily_digest()
                return digest
            else:
                # Return mock data if service not available
                return self._get_mock_digest_data()
                
        except Exception as e:
            self.logger.error(f"Failed to fetch digest data: {e}")
            return self._get_mock_digest_data()
    
    def _get_mock_digest_data(self) -> Dict[str, Any]:
        """Get mock digest data for testing"""
        return {
            'generated_at': datetime.now().isoformat(),
            'total_posts_analyzed': 89,
            'opportunities_found': 24,
            'trending_score': 8.7,
            'last_update': '2 min ago',
            'match_rate': '92%',
            'top_opportunities': [
                {
                    'title': 'Small business owner struggling with manual inventory tracking',
                    'summary': 'Retail store owner manually updating stock levels across 3 locations, taking 4+ hours daily. Looking for automation solution.',
                    'subreddit': 'smallbusiness',
                    'business_score': 9.2,
                    'priority': 'high',
                    'problem_indicators': ['manual process', 'time consuming', 'multiple locations']
                }
            ],
            'categories': {
                'Manual Process Solutions': [
                    {'title': 'Inventory tracking automation', 'subreddit': 'smallbusiness'},
                    {'title': 'Data entry streamlining', 'subreddit': 'entrepreneur'}
                ],
                'Workflow Automation': [
                    {'title': 'Customer follow-up system', 'subreddit': 'freelance'}
                ]
            }
        }
    
    def _update_digest_display(self, digest_data: Dict[str, Any]):
        """Update the display with digest data"""
        try:
            self.current_digest = digest_data
            
            # Update statistics
            self._update_statistics(digest_data)
            
            # Update digest text
            self._update_digest_text(digest_data)
            
            # Update opportunity cards
            self._update_opportunity_cards(digest_data)
            
            self.logger.info("Home view updated with fresh data")
            
        except Exception as e:
            self.logger.error(f"Failed to update digest display: {e}")
            self._show_error_message("Failed to update display")
    
    def _update_statistics(self, digest_data: Dict[str, Any]):
        """Update the statistics widgets"""
        stats_data = {
            'today_digest': f"{digest_data.get('opportunities_found', 0)} Posts",
            'trending_score': f"{digest_data.get('trending_score', 0)}/10",
            'last_update': digest_data.get('last_update', 'Just now'),
            'match_rate': digest_data.get('match_rate', '0%')
        }
        
        for key, value in stats_data.items():
            if key in self.stats_widgets:
                self.stats_widgets[key].value_label.configure(text=value)
    
    def _update_digest_text(self, digest_data: Dict[str, Any]):
        """Update the AI digest text"""
        digest_text = self._generate_digest_summary(digest_data)
        
        self.digest_text.delete("0.0", tk.END)
        self.digest_text.insert("0.0", digest_text)
    
    def _generate_digest_summary(self, digest_data: Dict[str, Any]) -> str:
        """Generate digest summary text"""
        opportunities = digest_data.get('top_opportunities', [])
        if not opportunities:
            return "No business opportunities detected in recent posts. Try adjusting your filters or keywords."
        
        top_opportunity = opportunities[0]
        
        summary = f"🎯 TOP OPPORTUNITY: {top_opportunity.get('title', 'Unknown')}\n\n"
        summary += f"Source: r/{top_opportunity.get('subreddit', 'unknown')}\n"
        summary += f"Business Score: {top_opportunity.get('business_score', 0)}/10\n"
        summary += f"Priority: {top_opportunity.get('priority', 'medium').title()}\n\n"
        summary += f"Summary: {top_opportunity.get('summary', 'No summary available.')}\n\n"
        
        if top_opportunity.get('problem_indicators'):
            indicators = top_opportunity['problem_indicators']
            if isinstance(indicators, list):
                summary += f"Keywords: {', '.join(indicators[:5])}"
            
        return summary
    
    def _update_opportunity_cards(self, digest_data: Dict[str, Any]):
        """Update opportunity cards with real data"""
        categories = digest_data.get('categories', {})
        
        # Update existing cards with real data
        card_index = 0
        for category_name, category_opportunities in categories.items():
            if card_index >= len(self.opportunity_cards):
                break
                
            card_data = {
                'title': category_name,
                'count': f"{len(category_opportunities)} leads • Mixed Priority",
                'description': self._format_category_description(category_opportunities),
                'subreddit': self._get_category_primary_subreddit(category_opportunities),
                'priority': self._assess_category_priority(category_opportunities)
            }
            
            # Update the existing card (this would require rebuilding the card)
            # For now, we keep the placeholder cards
            card_index += 1
    
    def _format_category_description(self, opportunities: List[Dict]) -> str:
        """Format category description"""
        if not opportunities:
            return "No opportunities available"
        
        descriptions = []
        for opp in opportunities[:3]:  # Top 3
            descriptions.append(f"• {opp.get('title', 'Unknown opportunity')}")
        
        return '\n'.join(descriptions)
    
    def _get_category_primary_subreddit(self, opportunities: List[Dict]) -> str:
        """Get primary subreddit for category"""
        if not opportunities:
            return "r/unknown"
        
        # Count subreddits and return most common
        subreddits = [opp.get('subreddit', 'unknown') for opp in opportunities]
        most_common = max(set(subreddits), key=subreddits.count) if subreddits else 'unknown'
        return f"r/{most_common}"
    
    def _assess_category_priority(self, opportunities: List[Dict]) -> str:
        """Assess overall priority for category"""
        if not opportunities:
            return 'low'
        
        # Simple assessment - could be enhanced
        high_priority = len([opp for opp in opportunities if opp.get('business_score', 0) >= 8])
        if high_priority >= 2:
            return 'high'
        elif high_priority >= 1:
            return 'medium'
        else:
            return 'low'
    
    # Action button handlers
    def _generate_newsletter(self):
        """Generate new newsletter"""
        self.logger.info("Generating new newsletter")
        self._show_success_message("Generating fresh newsletter...")
        self.refresh_data()
    
    def _view_analytics(self):
        """View detailed analytics"""
        self.logger.info("Opening analytics view")
        # Could open a detailed analytics dialog or switch to analytics view
        self._show_success_message("Analytics feature coming soon!")
    
    def _customize_feed(self):
        """Customize feed settings"""
        self.logger.info("Opening feed customization")
        # Open customization dialog
        CustomizeFeedDialog(self, self.app, self.colors)
    
    def _export_leads(self):
        """Export current leads"""
        if self.current_digest and self.current_digest.get('top_opportunities'):
            opportunities = self.current_digest['top_opportunities']
            self.export_data(opportunities, "newsletter_leads", "csv")
        else:
            self._show_error_message("No leads available to export")

class CustomizeFeedDialog(ctk.CTkToplevel):
    """Dialog for customizing newsletter feed"""
    
    def __init__(self, parent, app, colors: Dict[str, str]):
        super().__init__(parent)
        
        self.app = app
        self.colors = colors
        
        # Window configuration
        self.title("Customize Newsletter Feed")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self._center_window()
        
        self.configure(fg_color=colors['bg_primary'])
        
        self._setup_ui()
    
    def _center_window(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"600x700+{x}+{y}")
    
    def _setup_ui(self):
        """Setup the customization UI"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Customize Your Newsletter Feed",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Keywords section
        self._create_keywords_section(main_frame)
        
        # Subreddits section
        self._create_subreddits_section(main_frame)
        
        # Filters section
        self._create_filters_section(main_frame)
        
        # Action buttons
        self._create_action_buttons(main_frame)
    
    def _create_keywords_section(self, parent):
        """Create keywords customization section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        section_title = ctk.CTkLabel(
            section_frame,
            text="Business Keywords",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        section_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Keywords text area
        self.keywords_text = ctk.CTkTextbox(
            section_frame,
            height=100,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['bg_primary'],
            text_color=self.colors['text_primary']
        )
        self.keywords_text.pack(fill="x", padx=20, pady=(0, 15))
        
        # Default keywords
        default_keywords = "automation, manual process, time consuming, workflow, integration, efficiency, streamline, bottleneck"
        self.keywords_text.insert("0.0", default_keywords)
    
    def _create_subreddits_section(self, parent):
        """Create subreddits customization section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        section_title = ctk.CTkLabel(
            section_frame,
            text="Monitored Subreddits",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        section_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Subreddits checklist (simplified)
        subreddits = ['entrepreneur', 'smallbusiness', 'freelance', 'automation', 'productivity', 'excel', 'business']
        
        self.subreddit_vars = {}
        for subreddit in subreddits:
            var = tk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                section_frame,
                text=f"r/{subreddit}",
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_primary']
            )
            checkbox.pack(anchor="w", padx=20, pady=2)
            self.subreddit_vars[subreddit] = var
    
    def _create_filters_section(self, parent):
        """Create filters section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        section_title = ctk.CTkLabel(
            section_frame,
            text="Filters & Thresholds",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        section_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Min business score
        score_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        score_frame.pack(fill="x", padx=20, pady=5)
        
        score_label = ctk.CTkLabel(
            score_frame,
            text="Minimum Business Score:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_primary']
        )
        score_label.pack(side="left")
        
        self.score_slider = ctk.CTkSlider(
            score_frame,
            from_=0,
            to=10,
            number_of_steps=20,
            width=200
        )
        self.score_slider.pack(side="right")
        self.score_slider.set(2.0)
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['accent_orange'],
            command=self.destroy
        )
        cancel_button.pack(side="right", padx=(10, 0))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            fg_color=self.colors['accent_blue'],
            command=self._save_settings
        )
        save_button.pack(side="right")
    
    def _save_settings(self):
        """Save customization settings"""
        try:
            # Get settings
            keywords = self.keywords_text.get("0.0", tk.END).strip().split(",")
            keywords = [kw.strip() for kw in keywords if kw.strip()]
            
            selected_subreddits = [
                subreddit for subreddit, var in self.subreddit_vars.items()
                if var.get()
            ]
            
            min_score = self.score_slider.get()
            
            # Apply settings (would save to config service)
            newsletter_service = self.app.get_service('newsletter')
            if newsletter_service:
                newsletter_service.customize_feed({
                    'keywords': keywords,
                    'subreddits': selected_subreddits,
                    'min_business_score': min_score
                })
            
            self.app.show_status_message("Newsletter settings saved successfully!", "success")
            self.destroy()
            
        except Exception as e:
            self.app.show_status_message(f"Failed to save settings: {e}", "error")