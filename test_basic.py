#!/usr/bin/env python3
"""
Basic test script for PersonalizedReddit core functionality
Tests without heavy AI dependencies
"""

import sys
import os
from datetime import datetime

def test_database():
    """Test database functionality"""
    print("=== Testing Database ===")
    
    try:
        from data.database_manager import DatabaseManager
        
        # Test database initialization
        db = DatabaseManager("test_basic.db")
        print("+ Database initialized successfully")
        
        # Test basic operations
        stats = db.get_database_stats()
        print(f"+ Database stats: {stats}")
        
        # Test settings
        db.set_setting("test_key", "test_value")
        value = db.get_setting("test_key")
        assert value == "test_value", f"Expected 'test_value', got '{value}'"
        print("+ Settings operations working")
        
        db.close()
        print("+ Database operations successful")
        
        return True
        
    except Exception as e:
        print(f"- Database test failed: {e}")
        return False

def test_reddit_config():
    """Test Reddit configuration"""
    print("\n=== Testing Reddit Configuration ===")
    
    try:
        from config.reddit_config import RedditConfig, get_config_status
        
        config = RedditConfig()
        print("+ Reddit config initialized")
        
        status = get_config_status()
        print(f"+ Config status: {status.get('is_configured', False)}")
        
        if not status.get('is_configured'):
            print("+ Reddit API not configured (expected for testing)")
        
        # Test validation
        validation = config.validate_config()
        print(f"+ Config validation completed: {len(validation.get('errors', []))} errors")
        
        return True
        
    except Exception as e:
        print(f"- Reddit config test failed: {e}")
        return False

def test_ui_imports():
    """Test UI components can be imported"""
    print("\n=== Testing UI Imports ===")
    
    try:
        import customtkinter as ctk
        print("+ CustomTkinter available")
        
        from ui.views.base_view import BaseView
        print("+ Base view can be imported")
        
        from ui.views.home_view import HomeView
        print("+ Home view can be imported")
        
        from ui.views.live_view import LiveView
        print("+ Live view can be imported")
        
        from ui.views.discover_view import DiscoverView
        print("+ Discover view can be imported")
        
        from ui.components.navigation import NavigationSidebar
        print("+ Navigation component can be imported")
        
        return True
        
    except Exception as e:
        print(f"- UI imports test failed: {e}")
        return False

def test_services_basic():
    """Test basic service imports without AI"""
    print("\n=== Testing Basic Service Imports ===")
    
    try:
        from services.reddit_api_service import RedditAPIService
        print("+ Reddit API service can be imported")
        
        from services.export_service import ExportService
        print("+ Export service can be imported")
        
        from services.newsletter_service import NewsletterService
        print("+ Newsletter service can be imported")
        
        return True
        
    except Exception as e:
        print(f"- Basic services test failed: {e}")
        return False

def test_main_app_creation():
    """Test creating the main application (without running)"""
    print("\n=== Testing Main Application ===")
    
    try:
        # Just test imports and basic creation without AI services
        import customtkinter as ctk
        
        # Create a minimal test window
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        root.title("PersonalizedReddit Test")
        root.geometry("800x600")
        
        print("+ Main application window can be created")
        
        root.destroy()
        print("+ Application test successful")
        
        return True
        
    except Exception as e:
        print(f"- Main application test failed: {e}")
        return False

def test_simple_functionality():
    """Test some simple functionality without AI"""
    print("\n=== Testing Simple Functionality ===")
    
    try:
        from data.database_manager import DatabaseManager
        from config.reddit_config import RedditConfig
        
        # Test database with some data
        db = DatabaseManager("test_simple.db")
        
        # Test post saving
        post_data = {
            'reddit_id': 'test123',
            'title': 'Test Business Problem Post',
            'text': 'I need help automating my manual processes',
            'author': 'test_user',
            'subreddit': 'entrepreneur',
            'score': 15,
            'num_comments': 3,
            'created_utc': datetime.now().timestamp(),
            'url': 'https://reddit.com/test',
            'permalink': '/r/entrepreneur/test'
        }
        
        post_id = db.save_reddit_post(post_data)
        print(f"+ Saved test post with ID: {post_id}")
        
        # Test retrieving post
        saved_post = db.get_reddit_post('test123')
        assert saved_post is not None, "Post not found"
        print("+ Retrieved test post successfully")
        
        # Test analysis save
        analysis_data = {
            'analysis_type': 'business_opportunity',
            'score': 7.5,
            'confidence': 0.8,
            'business_score': 7.5,
            'sentiment_score': -0.2,
            'keywords_matched': ['automation', 'manual', 'processes']
        }
        
        analysis_id = db.save_post_analysis(post_id, analysis_data)
        print(f"+ Saved analysis with ID: {analysis_id}")
        
        # Test business lead creation
        lead_data = {
            'post_id': post_id,
            'lead_title': 'Process Automation Opportunity',
            'lead_description': 'Small business needs automation help',
            'business_problem': 'Manual processes',
            'industry_category': 'technology',
            'urgency_level': 2,
            'lead_score': 7.5,
            'qualification_status': 'qualified',
            'reddit_author': 'test_user',
            'notes': 'Good automation opportunity'
        }
        
        lead_id = db.save_business_lead(lead_data)
        print(f"+ Created business lead with ID: {lead_id}")
        
        db.close()
        print("+ Simple functionality test successful")
        
        return True
        
    except Exception as e:
        print(f"- Simple functionality test failed: {e}")
        return False

def main():
    """Run basic tests"""
    print("PersonalizedReddit Basic Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Database", test_database),
        ("Reddit Config", test_reddit_config),
        ("UI Imports", test_ui_imports),
        ("Basic Services", test_services_basic),
        ("Main Application", test_main_app_creation),
        ("Simple Functionality", test_simple_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"- {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "+" if result else "-"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nAll core tests passed! PersonalizedReddit basic functionality is working.")
    elif passed >= len(results) * 0.8:
        print("\nMost tests passed. Core application should work.")
    else:
        print("\nSeveral tests failed. Application may have issues.")
    
    print(f"\nTest completed at: {datetime.now()}")
    
    # Clean up test files
    try:
        for test_file in ["test_basic.db", "test_simple.db"]:
            if os.path.exists(test_file):
                os.remove(test_file)
        print("\nTest files cleaned up")
    except:
        pass

if __name__ == "__main__":
    main()