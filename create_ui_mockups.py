#!/usr/bin/env python3
"""
Professional UI Mockup Generator for Personalized Reddit App
Creates three detailed mockups: Home (Newsletter), Live (Enhanced Reddit), Discover (AI Recommendations)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
from datetime import datetime
import os

# Set up dark theme colors to match CustomTkinter
class Colors:
    # CustomTkinter Dark Theme Colors
    BACKGROUND = '#212121'
    SURFACE = '#2B2B2B'
    SURFACE_LIGHT = '#3B3B3B'
    PRIMARY = '#1F538D'
    PRIMARY_LIGHT = '#4A90E2'
    ACCENT = '#FF6B35'
    TEXT_PRIMARY = '#FFFFFF'
    TEXT_SECONDARY = '#B0B0B0'
    TEXT_HINT = '#808080'
    BORDER = '#404040'
    SUCCESS = '#4CAF50'
    WARNING = '#FF9800'
    ERROR = '#F44336'
    CARD_BG = '#2E2E2E'

def create_base_window(title, subtitle=""):
    """Create base window layout with navigation"""
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(Colors.BACKGROUND)
    ax.set_facecolor(Colors.BACKGROUND)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title bar
    title_bar = FancyBboxPatch((0, 95), 100, 5, boxstyle="round,pad=0", 
                              facecolor=Colors.SURFACE, edgecolor=Colors.BORDER)
    ax.add_patch(title_bar)
    
    # App title
    ax.text(2, 97.5, "PersonalizedReddit", fontsize=14, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='center')
    
    # Window controls (minimize, maximize, close)
    for i, color in enumerate([Colors.SUCCESS, Colors.WARNING, Colors.ERROR]):
        circle = plt.Circle((96 + i * 1.5, 97.5), 0.3, color=color)
        ax.add_patch(circle)
    
    # Navigation bar
    nav_bar = FancyBboxPatch((0, 88), 100, 7, boxstyle="round,pad=0", 
                            facecolor=Colors.SURFACE, edgecolor=Colors.BORDER)
    ax.add_patch(nav_bar)
    
    # Navigation tabs
    nav_items = [
        ("Home", 15, Colors.PRIMARY if title == "Home - Newsletter Overview" else Colors.SURFACE_LIGHT),
        ("Live", 35, Colors.PRIMARY if title == "Live - Enhanced Reddit" else Colors.SURFACE_LIGHT),
        ("Discover", 55, Colors.PRIMARY if title == "Discover - AI Recommendations" else Colors.SURFACE_LIGHT)
    ]
    
    for nav_text, x_pos, bg_color in nav_items:
        nav_tab = FancyBboxPatch((x_pos-5, 89), 10, 5, boxstyle="round,pad=0.2", 
                                facecolor=bg_color, edgecolor=Colors.BORDER)
        ax.add_patch(nav_tab)
        ax.text(x_pos, 91.5, nav_text, fontsize=12, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
    
    # User profile section
    profile_bg = FancyBboxPatch((75, 89), 23, 5, boxstyle="round,pad=0.2", 
                               facecolor=Colors.SURFACE_LIGHT, edgecolor=Colors.BORDER)
    ax.add_patch(profile_bg)
    
    # Profile avatar (circle)
    avatar = plt.Circle((78, 91.5), 1.5, color=Colors.PRIMARY_LIGHT)
    ax.add_patch(avatar)
    ax.text(78, 91.5, "DL", fontsize=10, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Username
    ax.text(82, 91.5, "Drew Ruller", fontsize=10, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='center')
    
    # Settings icon
    settings_bg = plt.Circle((95, 91.5), 1, color=Colors.SURFACE_LIGHT)
    ax.add_patch(settings_bg)
    ax.text(95, 91.5, "⚙", fontsize=14, color=Colors.TEXT_SECONDARY, ha='center', va='center')
    
    # Main title
    ax.text(50, 82, title, fontsize=20, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    if subtitle:
        ax.text(50, 78, subtitle, fontsize=14, color=Colors.TEXT_SECONDARY, 
                ha='center', va='center')
    
    return fig, ax

def create_home_mockup():
    """Create Home - Newsletter Overview mockup"""
    fig, ax = create_base_window("Home - Newsletter Overview", 
                                "AI-Powered Daily Digest & Trending Analysis")
    
    # Stats bar
    stats_bg = FancyBboxPatch((5, 72), 90, 4, boxstyle="round,pad=0.2", 
                             facecolor=Colors.SURFACE, edgecolor=Colors.BORDER)
    ax.add_patch(stats_bg)
    
    # Daily stats
    stats = [
        ("📊 Today's Digest", "24 Posts", 15),
        ("🔥 Trending Score", "8.7/10", 35),
        ("⏱ Last Update", "2 min ago", 55),
        ("🎯 Match Rate", "92%", 75)
    ]
    
    for stat_title, stat_value, x_pos in stats:
        ax.text(x_pos, 75, stat_title, fontsize=10, color=Colors.TEXT_SECONDARY, 
                ha='center', va='center')
        ax.text(x_pos, 73, stat_value, fontsize=12, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
    
    # Main content area - Newsletter cards
    content_y = 68
    
    # AI Summary Card (Featured)
    featured_card = FancyBboxPatch((5, content_y-15), 90, 13, boxstyle="round,pad=0.3", 
                                  facecolor=Colors.CARD_BG, edgecolor=Colors.PRIMARY)
    ax.add_patch(featured_card)
    
    # AI badge
    ai_badge = FancyBboxPatch((7, content_y-3), 12, 2.5, boxstyle="round,pad=0.1", 
                             facecolor=Colors.PRIMARY, edgecolor=None)
    ax.add_patch(ai_badge)
    ax.text(13, content_y-1.7, "🤖 AI DIGEST", fontsize=9, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Featured content
    ax.text(7, content_y-6, "Today's Top Business Automation Opportunities", 
            fontsize=16, color=Colors.TEXT_PRIMARY, weight='bold', va='top')
    ax.text(7, content_y-8.5, "AI Summary: Found 15 posts about manual data entry problems in r/entrepreneur.", 
            fontsize=11, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, content_y-10, "• Small business owner struggling with inventory tracking (47 upvotes)", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, content_y-11.5, "• Freelancer spending 3hrs daily on client invoicing (31 upvotes)", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, content_y-13, "• Real estate agent needs lead management automation (28 upvotes)", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    
    # Trending score
    score_bg = FancyBboxPatch((82, content_y-8), 10, 4, boxstyle="round,pad=0.2", 
                             facecolor=Colors.SUCCESS, edgecolor=None)
    ax.add_patch(score_bg)
    ax.text(87, content_y-6, "TRENDING", fontsize=8, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    ax.text(87, content_y-7.5, "9.2/10", fontsize=12, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Newsletter cards grid
    cards_y = content_y - 18
    card_data = [
        ("r/entrepreneur", "Manual Process Solutions", "12 leads • High Priority", Colors.ACCENT),
        ("r/smallbusiness", "Workflow Automation", "8 leads • Medium Priority", Colors.PRIMARY_LIGHT),
        ("r/freelance", "Time Management", "6 leads • Medium Priority", Colors.WARNING)
    ]
    
    for i, (subreddit, title, stats, color) in enumerate(card_data):
        x_pos = 5 + (i * 30)
        card = FancyBboxPatch((x_pos, cards_y), 28, 12, boxstyle="round,pad=0.3", 
                             facecolor=Colors.CARD_BG, edgecolor=Colors.BORDER)
        ax.add_patch(card)
        
        # Subreddit header
        header_bg = FancyBboxPatch((x_pos+1, cards_y+9), 26, 2.5, boxstyle="round,pad=0.1", 
                                  facecolor=color, edgecolor=None)
        ax.add_patch(header_bg)
        ax.text(x_pos+14, cards_y+10.2, subreddit, fontsize=11, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
        
        # Card content
        ax.text(x_pos+2, cards_y+7, title, fontsize=12, color=Colors.TEXT_PRIMARY, 
                weight='bold', va='top')
        ax.text(x_pos+2, cards_y+5, stats, fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
        
        # Sample posts
        ax.text(x_pos+2, cards_y+3, "• Data entry taking 4hrs daily", fontsize=9, 
                color=Colors.TEXT_SECONDARY, va='top')
        ax.text(x_pos+2, cards_y+1.5, "• Need inventory automation", fontsize=9, 
                color=Colors.TEXT_SECONDARY, va='top')
    
    # Action buttons
    button_y = cards_y - 8
    buttons = [
        ("📧 Generate Newsletter", 15, Colors.PRIMARY),
        ("📊 View Analytics", 35, Colors.SURFACE_LIGHT),
        ("⚙ Customize Feed", 55, Colors.SURFACE_LIGHT),
        ("📤 Export Leads", 75, Colors.ACCENT)
    ]
    
    for button_text, x_pos, bg_color in buttons:
        button = FancyBboxPatch((x_pos-8, button_y), 16, 4, boxstyle="round,pad=0.2", 
                               facecolor=bg_color, edgecolor=Colors.BORDER)
        ax.add_patch(button)
        ax.text(x_pos, button_y+2, button_text, fontsize=10, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
    
    plt.tight_layout()
    return fig

def create_live_mockup():
    """Create Live - Enhanced Reddit Experience mockup"""
    fig, ax = create_base_window("Live - Enhanced Reddit Experience", 
                                "Real-time Updates • Quick Actions • Multi-Account")
    
    # Live status bar
    status_bg = FancyBboxPatch((5, 72), 90, 4, boxstyle="round,pad=0.2", 
                              facecolor=Colors.SUCCESS, edgecolor=None)
    ax.add_patch(status_bg)
    
    # Live indicator
    live_dot = plt.Circle((8, 74), 0.5, color=Colors.TEXT_PRIMARY)
    ax.add_patch(live_dot)
    ax.text(12, 74, "🔴 LIVE - Real-time updates enabled", fontsize=12, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='center')
    
    # Account switcher
    ax.text(80, 74, "Account: DrewR_Business ▼", fontsize=10, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='center')
    
    # Filters bar
    filter_bg = FancyBboxPatch((5, 66), 90, 5, boxstyle="round,pad=0.2", 
                              facecolor=Colors.SURFACE, edgecolor=Colors.BORDER)
    ax.add_patch(filter_bg)
    
    # Filter buttons
    filters = ["🔥 Hot", "⬆ Rising", "🆕 New", "💎 Top", "🎯 Business", "⚡ Automation"]
    for i, filter_name in enumerate(filters):
        x_pos = 8 + (i * 14)
        filter_color = Colors.PRIMARY if i == 4 else Colors.SURFACE_LIGHT  # Business filter active
        filter_btn = FancyBboxPatch((x_pos, 67), 12, 3, boxstyle="round,pad=0.1", 
                                   facecolor=filter_color, edgecolor=Colors.BORDER)
        ax.add_patch(filter_btn)
        ax.text(x_pos+6, 68.5, filter_name, fontsize=9, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
    
    # Main feed area
    feed_y = 63
    
    # Post 1 - High priority lead
    post1_bg = FancyBboxPatch((5, feed_y-12), 90, 11, boxstyle="round,pad=0.3", 
                             facecolor=Colors.CARD_BG, edgecolor=Colors.ACCENT)
    ax.add_patch(post1_bg)
    
    # Priority indicator
    priority_badge = FancyBboxPatch((7, feed_y-2), 15, 2, boxstyle="round,pad=0.1", 
                                   facecolor=Colors.ACCENT, edgecolor=None)
    ax.add_patch(priority_badge)
    ax.text(14.5, feed_y-1, "🚨 HIGH PRIORITY", fontsize=8, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Post content
    ax.text(7, feed_y-5, "r/entrepreneur • Posted 5 minutes ago", fontsize=10, 
            color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, feed_y-6.5, "Help! Spending 6 hours daily on manual inventory tracking", 
            fontsize=14, color=Colors.TEXT_PRIMARY, weight='bold', va='top')
    ax.text(7, feed_y-8.5, "Small retail business owner struggling with Excel-based inventory system. Currently updating", 
            fontsize=11, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, feed_y-10, "stock levels manually across 3 locations. Looking for affordable automation solution...", 
            fontsize=11, color=Colors.TEXT_SECONDARY, va='top')
    
    # Quick actions
    actions = ["👍 47", "👎", "💬 12", "🔖 Save", "💼 Lead", "📧 Contact"]
    for i, action in enumerate(actions):
        x_pos = 65 + (i * 5)
        action_bg = FancyBboxPatch((x_pos, feed_y-10), 4, 2.5, boxstyle="round,pad=0.1", 
                                  facecolor=Colors.SURFACE_LIGHT, edgecolor=Colors.BORDER)
        ax.add_patch(action_bg)
        ax.text(x_pos+2, feed_y-8.7, action, fontsize=8, color=Colors.TEXT_PRIMARY, 
                ha='center', va='center')
    
    # AI Analysis sidebar
    ai_analysis_bg = FancyBboxPatch((72, feed_y-12), 23, 11, boxstyle="round,pad=0.2", 
                                   facecolor=Colors.SURFACE, edgecolor=Colors.PRIMARY)
    ax.add_patch(ai_analysis_bg)
    
    ax.text(73, feed_y-3, "🤖 AI Analysis", fontsize=10, color=Colors.PRIMARY_LIGHT, 
            weight='bold', va='top')
    ax.text(73, feed_y-5, "Business Score: 9.2/10", fontsize=9, color=Colors.SUCCESS, 
            weight='bold', va='top')
    ax.text(73, feed_y-6.5, "Keywords Found:", fontsize=9, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(73, feed_y-7.8, "• Manual tracking", fontsize=8, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(73, feed_y-9, "• 6 hours daily", fontsize=8, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(73, feed_y-10.2, "• Automation needed", fontsize=8, color=Colors.TEXT_SECONDARY, va='top')
    
    # Post 2 - Medium priority
    post2_y = feed_y - 15
    post2_bg = FancyBboxPatch((5, post2_y-10), 90, 9, boxstyle="round,pad=0.3", 
                             facecolor=Colors.CARD_BG, edgecolor=Colors.BORDER)
    ax.add_patch(post2_bg)
    
    # Medium priority
    med_badge = FancyBboxPatch((7, post2_y-2), 12, 1.5, boxstyle="round,pad=0.1", 
                              facecolor=Colors.WARNING, edgecolor=None)
    ax.add_patch(med_badge)
    ax.text(13, post2_y-1.2, "MEDIUM", fontsize=8, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    ax.text(7, post2_y-4, "r/smallbusiness • Posted 23 minutes ago", fontsize=10, 
            color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, post2_y-5.5, "Anyone know good tools for client follow-up automation?", 
            fontsize=14, color=Colors.TEXT_PRIMARY, weight='bold', va='top')
    ax.text(7, post2_y-7, "Running a service business and manually tracking client communications...", 
            fontsize=11, color=Colors.TEXT_SECONDARY, va='top')
    
    # Quick actions for post 2
    for i, action in enumerate(["👍 23", "💬 8", "🔖", "💼"]):
        x_pos = 75 + (i * 4.5)
        action_bg = FancyBboxPatch((x_pos, post2_y-8), 4, 2, boxstyle="round,pad=0.1", 
                                  facecolor=Colors.SURFACE_LIGHT, edgecolor=Colors.BORDER)
        ax.add_patch(action_bg)
        ax.text(x_pos+2, post2_y-7, action, fontsize=8, color=Colors.TEXT_PRIMARY, 
                ha='center', va='center')
    
    # Real-time update notification
    notification_bg = FancyBboxPatch((5, 5), 40, 4, boxstyle="round,pad=0.2", 
                                    facecolor=Colors.PRIMARY, edgecolor=None)
    ax.add_patch(notification_bg)
    ax.text(25, 7, "🔔 3 new high-priority leads detected", fontsize=10, 
            color=Colors.TEXT_PRIMARY, weight='bold', ha='center', va='center')
    
    plt.tight_layout()
    return fig

def create_discover_mockup():
    """Create Discover - AI-Powered Recommendations mockup"""
    fig, ax = create_base_window("Discover - AI-Powered Recommendations", 
                                "AI-Curated Content • Subreddit Discovery • Personalized Feed")
    
    # AI status bar
    ai_status_bg = FancyBboxPatch((5, 72), 90, 4, boxstyle="round,pad=0.2", 
                                 facecolor=Colors.PRIMARY, edgecolor=None)
    ax.add_patch(ai_status_bg)
    
    ax.text(8, 74, "🧠 AI Engine Active • Analyzing 2.3M posts • Confidence: 94%", 
            fontsize=12, color=Colors.TEXT_PRIMARY, weight='bold', va='center')
    
    # Recommendation score
    ax.text(85, 74, "Today's Score: A+", fontsize=11, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='center')
    
    # Discovery categories
    categories_bg = FancyBboxPatch((5, 66), 90, 5, boxstyle="round,pad=0.2", 
                                  facecolor=Colors.SURFACE, edgecolor=Colors.BORDER)
    ax.add_patch(categories_bg)
    
    categories = [
        ("🎯 For You", Colors.ACCENT, True),
        ("🚀 Trending", Colors.SURFACE_LIGHT, False),
        ("💡 New Subreddits", Colors.SURFACE_LIGHT, False),
        ("🔍 Similar Interests", Colors.SURFACE_LIGHT, False),
        ("📈 Opportunities", Colors.PRIMARY, False)
    ]
    
    for i, (cat_name, bg_color, active) in enumerate(categories):
        x_pos = 7 + (i * 17)
        cat_btn = FancyBboxPatch((x_pos, 67), 15, 3, boxstyle="round,pad=0.1", 
                                facecolor=bg_color, edgecolor=Colors.BORDER)
        ax.add_patch(cat_btn)
        ax.text(x_pos+7.5, 68.5, cat_name, fontsize=9, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
    
    # Main discovery feed
    discovery_y = 63
    
    # Recommended subreddit 1
    rec1_bg = FancyBboxPatch((5, discovery_y-15), 42, 14, boxstyle="round,pad=0.3", 
                            facecolor=Colors.CARD_BG, edgecolor=Colors.ACCENT)
    ax.add_patch(rec1_bg)
    
    # AI recommendation badge
    ai_badge1 = FancyBboxPatch((7, discovery_y-2), 18, 2, boxstyle="round,pad=0.1", 
                              facecolor=Colors.ACCENT, edgecolor=None)
    ax.add_patch(ai_badge1)
    ax.text(16, discovery_y-1, "🤖 AI RECOMMENDED", fontsize=8, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Match score
    match_bg = FancyBboxPatch((35, discovery_y-2), 10, 2, boxstyle="round,pad=0.1", 
                             facecolor=Colors.SUCCESS, edgecolor=None)
    ax.add_patch(match_bg)
    ax.text(40, discovery_y-1, "96% MATCH", fontsize=8, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Subreddit info
    ax.text(7, discovery_y-5, "r/ProcessAutomation", fontsize=16, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='top')
    ax.text(7, discovery_y-7, "47K members • Very Active", fontsize=10, 
            color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, discovery_y-8.5, "Community focused on business process automation,", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(7, discovery_y-10, "workflow optimization, and efficiency solutions.", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    
    # Why recommended
    ax.text(7, discovery_y-12, "🎯 Why recommended: High business problem density", 
            fontsize=9, color=Colors.PRIMARY_LIGHT, weight='bold', va='top')
    ax.text(7, discovery_y-13.5, "• 89% automation-related posts • 12 leads/day avg", 
            fontsize=9, color=Colors.TEXT_SECONDARY, va='top')
    
    # Action buttons
    join_btn = FancyBboxPatch((35, discovery_y-10), 10, 3, boxstyle="round,pad=0.1", 
                             facecolor=Colors.PRIMARY, edgecolor=None)
    ax.add_patch(join_btn)
    ax.text(40, discovery_y-8.5, "🔔 JOIN", fontsize=10, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # Recommended subreddit 2
    rec2_bg = FancyBboxPatch((50, discovery_y-15), 42, 14, boxstyle="round,pad=0.3", 
                            facecolor=Colors.CARD_BG, edgecolor=Colors.BORDER)
    ax.add_patch(rec2_bg)
    
    # New discovery badge
    new_badge = FancyBboxPatch((52, discovery_y-2), 12, 2, boxstyle="round,pad=0.1", 
                              facecolor=Colors.WARNING, edgecolor=None)
    ax.add_patch(new_badge)
    ax.text(58, discovery_y-1, "🆕 NEW", fontsize=8, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    ax.text(52, discovery_y-5, "r/SaaSFounders", fontsize=16, color=Colors.TEXT_PRIMARY, 
            weight='bold', va='top')
    ax.text(52, discovery_y-7, "23K members • Growing Fast", fontsize=10, 
            color=Colors.TEXT_SECONDARY, va='top')
    ax.text(52, discovery_y-8.5, "Software founders sharing automation challenges", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    ax.text(52, discovery_y-10, "and solutions for scaling their businesses.", 
            fontsize=10, color=Colors.TEXT_SECONDARY, va='top')
    
    ax.text(52, discovery_y-12, "🎯 Similar to your interests in r/entrepreneur", 
            fontsize=9, color=Colors.PRIMARY_LIGHT, weight='bold', va='top')
    
    # Preview button
    preview_btn = FancyBboxPatch((80, discovery_y-10), 10, 3, boxstyle="round,pad=0.1", 
                                facecolor=Colors.SURFACE_LIGHT, edgecolor=Colors.BORDER)
    ax.add_patch(preview_btn)
    ax.text(85, discovery_y-8.5, "👁 PREVIEW", fontsize=9, color=Colors.TEXT_PRIMARY, 
            weight='bold', ha='center', va='center')
    
    # AI Insights section
    insights_y = discovery_y - 18
    insights_bg = FancyBboxPatch((5, insights_y-12), 90, 11, boxstyle="round,pad=0.3", 
                                facecolor=Colors.SURFACE, edgecolor=Colors.PRIMARY)
    ax.add_patch(insights_bg)
    
    ax.text(7, insights_y-2, "🧠 AI Insights & Trends", fontsize=14, color=Colors.PRIMARY_LIGHT, 
            weight='bold', va='top')
    
    # Insight cards
    insight_cards = [
        ("📈 Trending Topics", "API Integration\nWorkflow Tools\nData Migration", 28),
        ("🎯 Best Times", "Peak Activity:\n2-4 PM EST\n7-9 PM EST", 58),
        ("💡 Opportunities", "12 new leads\nidentified today\n+47% vs yesterday", 88)
    ]
    
    for title, content, x_pos in insight_cards:
        card_bg = FancyBboxPatch((x_pos-12, insights_y-11), 22, 8, boxstyle="round,pad=0.2", 
                                facecolor=Colors.CARD_BG, edgecolor=Colors.BORDER)
        ax.add_patch(card_bg)
        ax.text(x_pos-1, insights_y-4, title, fontsize=11, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            ax.text(x_pos-1, insights_y-6.5-(i*1.2), line, fontsize=9, 
                   color=Colors.TEXT_SECONDARY, ha='center', va='center')
    
    # Bottom action bar
    action_bar_bg = FancyBboxPatch((5, 5), 90, 5, boxstyle="round,pad=0.2", 
                                  facecolor=Colors.SURFACE, edgecolor=Colors.BORDER)
    ax.add_patch(action_bar_bg)
    
    # Action buttons
    actions = [
        ("🔍 Explore More", Colors.PRIMARY),
        ("⚙ Customize AI", Colors.SURFACE_LIGHT),
        ("📊 View Analytics", Colors.SURFACE_LIGHT),
        ("📤 Share Findings", Colors.ACCENT)
    ]
    
    for i, (action_text, bg_color) in enumerate(actions):
        x_pos = 10 + (i * 20)
        action_btn = FancyBboxPatch((x_pos, 6), 18, 3, boxstyle="round,pad=0.1", 
                                   facecolor=bg_color, edgecolor=Colors.BORDER)
        ax.add_patch(action_btn)
        ax.text(x_pos+9, 7.5, action_text, fontsize=10, color=Colors.TEXT_PRIMARY, 
                weight='bold', ha='center', va='center')
    
    plt.tight_layout()
    return fig

def save_mockups():
    """Generate and save all three mockups"""
    output_dir = r"C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Images\Working"
    
    # Create Home mockup
    print("Creating Home - Newsletter Overview mockup...")
    home_fig = create_home_mockup()
    home_path = os.path.join(output_dir, "PersonalizedReddit_Home_Mockup.png")
    home_fig.savefig(home_path, dpi=300, bbox_inches='tight', facecolor=Colors.BACKGROUND)
    plt.close(home_fig)
    
    # Create Live mockup
    print("Creating Live - Enhanced Reddit mockup...")
    live_fig = create_live_mockup()
    live_path = os.path.join(output_dir, "PersonalizedReddit_Live_Mockup.png")
    live_fig.savefig(live_path, dpi=300, bbox_inches='tight', facecolor=Colors.BACKGROUND)
    plt.close(live_fig)
    
    # Create Discover mockup
    print("Creating Discover - AI Recommendations mockup...")
    discover_fig = create_discover_mockup()
    discover_path = os.path.join(output_dir, "PersonalizedReddit_Discover_Mockup.png")
    discover_fig.savefig(discover_path, dpi=300, bbox_inches='tight', facecolor=Colors.BACKGROUND)
    plt.close(discover_fig)
    
    print(f"\n✅ All mockups saved successfully!")
    print(f"📁 Location: {output_dir}")
    print(f"📄 Files created:")
    print(f"   • PersonalizedReddit_Home_Mockup.png")
    print(f"   • PersonalizedReddit_Live_Mockup.png")
    print(f"   • PersonalizedReddit_Discover_Mockup.png")
    
    return [home_path, live_path, discover_path]

if __name__ == "__main__":
    # Generate all mockups
    mockup_paths = save_mockups()
    
    # Create a summary PDF combining all mockups (optional)
    print("\n🎨 Professional UI Mockups Complete!")
    print("Ready for development implementation with CustomTkinter!")