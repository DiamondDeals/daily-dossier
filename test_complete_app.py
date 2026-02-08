#!/usr/bin/env python3
"""
Test script for PersonalizedReddit complete application
Tests core functionality without GUI
"""

import sys
import os
from datetime import datetime

def test_imports():
    """Test all critical imports"""
    print("=== Testing Imports ===")
    
    try:
        # Core modules
        from app.application import PersonalizedRedditApp
        print("✓ Main application imports successful")
        
        from services.ai_service import AIService
        from services.reddit_api_service import RedditAPIService
        from services.live_reddit_service import LiveRedditService
        from services.ai_recommendation_service import AIRecommendationService
        print("✓ All services imported successfully")
        
        from data.database_manager import DatabaseManager
        print("✓ Database manager imported successfully")
        
        from config.reddit_config import RedditConfig, get_config
        print("✓ Configuration system imported successfully")
        
        from ui.views.home_view import HomeView
        from ui.views.live_view import LiveView
        from ui.views.discover_view import DiscoverView
        print("✓ All UI views imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n=== Testing Database ===")
    
    try:
        from data.database_manager import DatabaseManager
        
        # Test database initialization
        db = DatabaseManager("test_personalized_reddit.db")
        print("✓ Database initialized successfully")
        
        # Test basic operations
        stats = db.get_database_stats()
        print(f"✓ Database stats: {stats}")
        
        # Test settings
        db.set_setting("test_key", "test_value")
        value = db.get_setting("test_key")
        assert value == "test_value", f"Expected 'test_value', got '{value}'"
        print("✓ Settings operations working")
        
        db.close()
        print("✓ Database operations successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_ai_service():
    """Test AI service functionality"""
    print("\n=== Testing AI Service ===")
    
    try:
        from services.ai_service import AIService
        
        ai_service = AIService()
        print("✓ AI Service initialized")
        
        # Test summarization
        test_text = """
        I'm struggling with manual data entry for my small business. Every day I spend 
        hours copying information from emails into our inventory system. This process 
        is so time-consuming and error-prone. I'm looking for a way to automate this 
        workflow. Does anyone know of a good solution?
        """
        
        summary = ai_service.summarize_text(test_text)
        print(f"✓ Summarization test: {summary.get('summary', 'No summary')[:100]}...")
        
        # Test sentiment analysis
        sentiment = ai_service.analyze_sentiment(test_text)
        print(f"✓ Sentiment analysis: {sentiment.get('label', 'unknown')} ({sentiment.get('confidence', 0):.2f})")
        
        # Test business opportunity detection
        opportunity = ai_service.detect_business_opportunities(test_text)
        print(f"✓ Business opportunity score: {opportunity.get('opportunity_score', 0):.2f}")
        
        ai_service.close()
        print("✓ AI Service test successful")
        
        return True
        
    except Exception as e:
        print(f"✗ AI Service test failed: {e}")
        return False

def test_reddit_config():
    """Test Reddit configuration"""
    print("\n=== Testing Reddit Configuration ===")
    
    try:
        from config.reddit_config import RedditConfig, get_config_status
        
        config = RedditConfig()
        print("✓ Reddit config initialized")
        
        status = get_config_status()
        print(f"✓ Config status: {status.get('is_configured', False)}")
        
        if not status.get('is_configured'):
            print("ℹ Reddit API not configured (expected for testing)")
        
        # Test validation
        validation = config.validate_config()
        print(f"✓ Config validation completed: {len(validation.get('errors', []))} errors")
        
        return True
        
    except Exception as e:
        print(f"✗ Reddit config test failed: {e}")
        return False

def test_recommendation_service():
    """Test AI recommendation service"""
    print("\n=== Testing Recommendation Service ===")
    
    try:
        from services.ai_recommendation_service import AIRecommendationService
        from data.database_manager import DatabaseManager
        
        # Create mock services for testing
        db = DatabaseManager("test_recommendations.db")
        
        class MockRedditService:
            pass
        
        class MockAIService:
            def detect_business_opportunities(self, text):
                return {'opportunity_score': 5.0, 'confidence': 0.8}
        
        reddit_service = MockRedditService()
        ai_service = MockAIService()
        
        rec_service = AIRecommendationService(reddit_service, ai_service, db)
        print("✓ Recommendation service initialized")
        
        # Test recommendations
        recommendations = rec_service.generate_subreddit_recommendations("test_user", 5)
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        if recommendations:
            print(f"  - Top recommendation: {recommendations[0].get('name', 'unknown')}")
        
        # Test analytics
        analytics = rec_service.get_recommendation_analytics("test_user")
        print(f"✓ Analytics generated: {analytics.get('algorithm_version', 'unknown')}")
        
        rec_service.close()
        db.close()
        print("✓ Recommendation service test successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Recommendation service test failed: {e}")
        return False

def test_ui_components():
    """Test UI components can be created"""
    print("\n=== Testing UI Components ===")
    
    try:
        import customtkinter as ctk
        
        # Test that CustomTkinter is available
        print("✓ CustomTkinter available")
        
        # Test creating a simple window (don't show it)
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        
        from ui.views.base_view import BaseView
        print("✓ Base view can be imported")
        
        root.destroy()
        print("✓ UI components test successful")
        
        return True
        
    except Exception as e:
        print(f"✗ UI components test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("PersonalizedReddit Application Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("AI Service", test_ai_service),
        ("Reddit Config", test_reddit_config),
        ("Recommendation Service", test_recommendation_service),
        ("UI Components", test_ui_components)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! PersonalizedReddit application is ready to use.")
    elif passed >= len(results) * 0.8:
        print("⚠️  Most tests passed. Application should work with minor limitations.")
    else:
        print("❌ Several tests failed. Application may have significant issues.")
    
    print(f"\nTest completed at: {datetime.now()}")
    
    # Clean up test files
    try:
        for test_file in ["test_personalized_reddit.db", "test_recommendations.db"]:
            if os.path.exists(test_file):
                os.remove(test_file)
        print("\n🧹 Test files cleaned up")
    except:
        pass

if __name__ == "__main__":
    main()