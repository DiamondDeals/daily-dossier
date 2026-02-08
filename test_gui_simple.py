#!/usr/bin/env python3
"""
Simple GUI Components Test - Import and basic functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_imports():
    """Test GUI component imports"""
    print("Testing GUI Component Imports...")
    
    try:
        # Test CustomTkinter
        import customtkinter as ctk
        print("OK CustomTkinter imported")
        
        # Test our UI components
        from ui.components.navigation import NavigationFrame, SettingsDialog
        print("OK Navigation components imported")
        
        from ui.views.base_view import BaseView
        print("OK Base view imported")
        
        from ui.views.home_view import HomeView, CustomizeFeedDialog
        print("OK Home view imported")
        
        # Test if we can create basic CTk objects without mainloop
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        print("OK CustomTkinter configuration set")
        
        # Test basic widget creation (without showing)
        test_frame = ctk.CTkFrame(None, width=200, height=100)
        test_label = ctk.CTkLabel(test_frame, text="Test Label")
        test_button = ctk.CTkButton(test_frame, text="Test Button")
        print("OK Basic widgets created")
        
        # Test color definitions
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
        print("OK Color scheme defined")
        
        # Test fonts
        test_font = ctk.CTkFont(size=14, weight="bold")
        print("OK Custom fonts work")
        
        print("OK All GUI component imports successful!")
        return True
        
    except Exception as e:
        print(f"FAILED GUI imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_services():
    """Test app service imports"""
    print("Testing Application Service Imports...")
    
    try:
        from services.newsletter_service import NewsletterService
        print("OK Newsletter service imported")
        
        from services.config_service import ConfigService
        print("OK Config service imported")
        
        from utils.logging_config import get_logger, log_performance
        print("OK Logging utilities imported")
        
        print("OK All service imports successful!")
        return True
        
    except Exception as e:
        print(f"FAILED Service imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_app_import():
    """Test main application import"""
    print("Testing Main Application Import...")
    
    try:
        # Test main app import
        from app.application import PersonalizedRedditApp
        print("OK Main application imported")
        
        # Test that we can access the class
        app_class = PersonalizedRedditApp
        print(f"OK Application class available: {app_class.__name__}")
        
        print("OK Main application import successful!")
        return True
        
    except Exception as e:
        print(f"FAILED Main app import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== PersonalizedReddit GUI Component Tests ===")
    
    success = True
    
    success &= test_gui_imports()
    print()
    
    success &= test_app_services()
    print()
    
    success &= test_main_app_import()
    print()
    
    if success:
        print("=== ALL TESTS PASSED ===")
        print("GUI components are ready for full application testing!")
    else:
        print("=== SOME TESTS FAILED ===")
        print("Check the errors above for issues to resolve.")
    
    sys.exit(0 if success else 1)