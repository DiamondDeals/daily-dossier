#!/usr/bin/env python3
"""
Test GUI Components - Basic CustomTkinter functionality test
"""

import sys
import os
from pathlib import Path
import threading
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_components():
    """Test basic GUI components without full application"""
    print("Testing GUI Components...")
    
    try:
        import customtkinter as ctk
        print("OK CustomTkinter available")
        
        # Test basic window creation
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create test window
        root = ctk.CTk()
        root.title("PersonalizedReddit - GUI Test")
        root.geometry("800x600")
        
        # Define colors like the app
        colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#404040',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent_blue': '#4A90E2',
            'accent_green': '#7ED321',
            'accent_orange': '#F5A623'
        }
        
        root.configure(fg_color=colors['bg_primary'])
        
        # Test navigation-like header
        header_frame = ctk.CTkFrame(root, fg_color=colors['bg_secondary'], corner_radius=10, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Test title
        title_label = ctk.CTkLabel(
            header_frame,
            text="PersonalizedReddit - GUI Test",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors['text_primary']
        )
        title_label.pack(pady=20)
        
        # Test tab buttons
        tab_frame = ctk.CTkFrame(root, fg_color=colors['bg_secondary'], corner_radius=10)
        tab_frame.pack(fill="x", padx=20, pady=10)
        
        tab_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="tabs")
        
        tabs = ["Home", "Live", "Discover"]
        tab_buttons = []
        
        for i, tab_name in enumerate(tabs):
            button = ctk.CTkButton(
                tab_frame,
                text=f"📊 {tab_name}" if i == 0 else f"🔍 {tab_name}" if i == 1 else f"🤖 {tab_name}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=colors['accent_blue'] if i == 0 else colors['bg_tertiary'],
                hover_color=colors['accent_blue'],
                height=40,
                command=lambda name=tab_name: print(f"Clicked {name} tab")
            )
            button.grid(row=0, column=i, padx=10, pady=15, sticky="ew")
            tab_buttons.append(button)
        
        # Test content area with cards
        content_frame = ctk.CTkScrollableFrame(root, fg_color=colors['bg_primary'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Test statistics cards
        stats_frame = ctk.CTkFrame(content_frame, fg_color=colors['bg_secondary'], corner_radius=10)
        stats_frame.pack(fill="x", pady=10)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")
        
        stats_data = [
            ("📊", "24 Posts", "Today's Digest"),
            ("📈", "8.7/10", "Trending Score"),
            ("🔄", "2 min ago", "Last Update"),
            ("🎯", "92%", "Match Rate")
        ]
        
        for i, (icon, value, title) in enumerate(stats_data):
            stat_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_container.grid(row=0, column=i, padx=15, pady=20, sticky="ew")
            
            # Icon and value
            value_frame = ctk.CTkFrame(stat_container, fg_color="transparent")
            value_frame.pack(fill="x")
            
            icon_label = ctk.CTkLabel(value_frame, text=icon, font=ctk.CTkFont(size=20))
            icon_label.pack(side="left")
            
            value_label = ctk.CTkLabel(
                value_frame,
                text=value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=colors['text_primary']
            )
            value_label.pack(side="right")
            
            # Title
            title_label = ctk.CTkLabel(
                stat_container,
                text=title,
                font=ctk.CTkFont(size=12),
                text_color=colors['text_secondary']
            )
            title_label.pack(pady=(5, 0))
        
        # Test business opportunity cards
        opportunities_frame = ctk.CTkFrame(content_frame, fg_color=colors['bg_secondary'], corner_radius=10)
        opportunities_frame.pack(fill="x", pady=10)
        opportunities_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="opportunities")
        
        # Section title
        opp_title = ctk.CTkLabel(
            opportunities_frame,
            text="Test Business Opportunities",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors['text_primary']
        )
        opp_title.pack(pady=(15, 10))
        
        # Opportunity cards container
        cards_container = ctk.CTkFrame(opportunities_frame, fg_color="transparent")
        cards_container.pack(fill="x", padx=20, pady=(0, 20))
        cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        opportunities = [
            {
                'title': 'Manual Process Solutions',
                'count': '12 leads • High Priority',
                'description': '• Data entry automation needs\\n• Inventory tracking solutions\\n• Process streamlining requests',
                'subreddit': 'r/smallbusiness',
                'priority': 'high'
            },
            {
                'title': 'Workflow Automation',
                'count': '8 leads • Medium Priority',
                'description': '• Customer follow-up systems\\n• Order processing automation\\n• Report generation tools',
                'subreddit': 'r/entrepreneur',
                'priority': 'medium'
            },
            {
                'title': 'Integration Projects',
                'count': '6 leads • Medium Priority',
                'description': '• System connectivity issues\\n• API integration needs\\n• Data synchronization projects',
                'subreddit': 'r/freelance',
                'priority': 'low'
            }
        ]
        
        priority_colors = {
            'high': colors['accent_orange'],
            'medium': '#FFA726',
            'low': colors['text_secondary']
        }
        
        for i, opp in enumerate(opportunities):
            card = ctk.CTkFrame(cards_container, fg_color=colors['bg_tertiary'], corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
            # Priority badge
            priority_badge = ctk.CTkLabel(
                card,
                text=f"{opp['priority'].upper()} PRIORITY",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=priority_colors[opp['priority']],
                text_color="white",
                corner_radius=10,
                height=20
            )
            priority_badge.pack(pady=(15, 5))
            
            # Title
            title_label = ctk.CTkLabel(
                card,
                text=opp['title'],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=colors['text_primary'],
                wraplength=200
            )
            title_label.pack(pady=5)
            
            # Count
            count_label = ctk.CTkLabel(
                card,
                text=opp['count'],
                font=ctk.CTkFont(size=11),
                text_color=colors['text_secondary']
            )
            count_label.pack(pady=5)
            
            # Description
            desc_text = ctk.CTkTextbox(
                card,
                height=80,
                font=ctk.CTkFont(size=10),
                fg_color=colors['bg_primary'],
                text_color=colors['text_primary']
            )
            desc_text.pack(fill="x", padx=10, pady=5)
            desc_text.insert("0.0", opp['description'])
            desc_text.configure(state="disabled")
            
            # Source
            source_label = ctk.CTkLabel(
                card,
                text=opp['subreddit'],
                font=ctk.CTkFont(size=10),
                text_color=colors['accent_blue']
            )
            source_label.pack(pady=(5, 15))
        
        # Test action buttons
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=10)
        actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        action_buttons = [
            ("📋 Generate Newsletter", colors['accent_blue']),
            ("📊 View Analytics", colors['bg_tertiary']),
            ("⚙️ Customize Feed", colors['bg_tertiary']),
            ("📤 Export Leads", colors['accent_orange'])
        ]
        
        for i, (text, color) in enumerate(action_buttons):
            button = ctk.CTkButton(
                actions_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=color,
                height=40,
                command=lambda t=text: print(f"Clicked: {t}")
            )
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        print("OK GUI components created successfully")
        
        def close_test():
            """Close test after showing it works"""
            time.sleep(0.1)  # Brief pause to show it works
            print("OK GUI test completed - closing window")
            root.quit()
            root.destroy()
        
        # Show window briefly then close
        root.after(100, close_test)  # Close after 100ms
        
        print("OK Starting GUI test window...")
        root.mainloop()
        
        print("OK GUI test completed successfully!")
        return True
        
    except Exception as e:
        print(f"FAILED GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_components()
    sys.exit(0 if success else 1)