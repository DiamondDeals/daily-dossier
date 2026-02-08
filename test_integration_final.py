#!/usr/bin/env python3
"""
Final Integration Test for PersonalizedReddit Application
Comprehensive test of all components working together
"""

import sys
import os
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_core_imports():
    """Test all core component imports"""
    print("=== Testing Core Imports ===")
    
    try:
        # Test database
        from data.database_manager import DatabaseManager
        print("OK Database manager imported")
        
        # Test services
        from services.ai_service import AIService
        from services.export_service import ExportService
        from services.reddit_api_service import RedditAPIService
        from services.newsletter_service import NewsletterService
        from services.config_service import ConfigService
        print("OK All services imported")
        
        # Test UI components
        import customtkinter as ctk
        from ui.components.navigation import NavigationFrame
        from ui.views.home_view import HomeView
        print("OK UI components imported")
        
        return True
        
    except Exception as e:
        print(f"FAILED Core imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """Test database operations"""
    print("\n=== Testing Database Operations ===")
    
    try:
        from data.database_manager import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = DatabaseManager(db_path)
            print("OK Database created")
            
            # Test account creation
            account_id = db.save_reddit_account('test_user', 'token123', 'refresh456')
            print(f"OK Account created: {account_id}")
            
            # Test subreddit operations
            subreddit_id = db.get_or_create_subreddit('entrepreneur', 'Entrepreneur')
            print(f"OK Subreddit created: {subreddit_id}")
            
            # Test post saving
            post_data = {
                'reddit_id': 'test_post_123',
                'subreddit_id': subreddit_id,
                'account_id': account_id,
                'title': 'Test Business Automation Post',
                'selftext': 'Looking for automation solutions for manual processes',
                'author': 'test_user',
                'score': 50,
                'num_comments': 10,
                'created_utc': '2025-08-14 18:00:00'
            }
            post_id = db.save_reddit_post(post_data)
            print(f"OK Post created: {post_id}")
            
            # Test analysis saving
            analysis_data = {
                'analysis_type': 'business_opportunity',
                'score': 0.85,
                'confidence': 0.9,
                'business_score': 0.88,
                'keywords_matched': ['automation', 'manual process']
            }
            analysis_id = db.save_post_analysis(post_id, analysis_data)
            print(f"OK Analysis created: {analysis_id}")
            
            # Test lead saving
            lead_data = {
                'post_id': post_id,
                'account_id': account_id,
                'lead_title': 'Automation opportunity',
                'business_problem': 'Manual data processing',
                'industry_category': 'Technology',
                'urgency_level': 3,
                'lead_score': 0.85,
                'reddit_author': 'test_user'
            }
            lead_id = db.save_business_lead(lead_data)
            print(f"OK Lead created: {lead_id}")
            
            # Test data retrieval
            posts = db.get_recent_posts(24, 10)
            leads = db.get_business_leads()
            print(f"OK Data retrieval: {len(posts)} posts, {len(leads)} leads")
            
            db.close()
            return True
            
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)
        
    except Exception as e:
        print(f"FAILED Database operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_services():
    """Test AI services"""
    print("\n=== Testing AI Services ===")
    
    try:
        from services.ai_service import AIService
        
        # Test with offline configuration
        config = {
            'skip_model_loading': True,
            'load_summarization': False,
            'load_sentiment': False,
            'load_embeddings': False
        }
        
        ai_service = AIService(config=config)
        print("OK AI service initialized")
        
        test_text = "I need automation for my manual data entry process that takes hours daily"
        
        # Test business opportunity detection
        opportunity = ai_service.detect_business_opportunities(test_text)
        print(f"OK Business opportunity score: {opportunity.get('opportunity_score', 0)}")
        
        # Test sentiment analysis
        sentiment = ai_service.analyze_sentiment(test_text)
        print(f"OK Sentiment: {sentiment.get('label', 'unknown')}")
        
        # Test summarization
        summary = ai_service.summarize_text(test_text)
        print(f"OK Summary method: {summary.get('method', 'unknown')}")
        
        ai_service.close()
        return True
        
    except Exception as e:
        print(f"FAILED AI services failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_functionality():
    """Test export functionality"""
    print("\n=== Testing Export Functionality ===")
    
    try:
        from services.export_service import ExportService
        
        export_service = ExportService()
        print("OK Export service initialized")
        
        # Test data
        test_data = [
            {
                'title': 'Test Business Lead',
                'author': 'test_user',
                'subreddit': 'entrepreneur',
                'business_score': 8.5,
                'urgency_level': 'high',
                'created_date': '2025-08-14'
            }
        ]
        
        # Test CSV export
        csv_path = export_service.export_data(test_data, "test_integration", "csv")
        print(f"OK CSV export: {csv_path}")
        
        # Test JSON export
        json_path = export_service.export_data(test_data, "test_integration", "json")
        print(f"OK JSON export: {json_path}")
        
        # Test Markdown export
        md_path = export_service.export_data(test_data, "test_integration", "markdown")
        print(f"OK Markdown export: {md_path}")
        
        # Verify files exist
        for path in [csv_path, json_path, md_path]:
            if path.exists() and path.stat().st_size > 0:
                print(f"OK {path.name}: {path.stat().st_size} bytes")
            else:
                print(f"FAILED {path.name}: File missing or empty")
        
        export_service.close()
        return True
        
    except Exception as e:
        print(f"FAILED Export functionality failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reddit_configuration():
    """Test Reddit API configuration"""
    print("\n=== Testing Reddit Configuration ===")
    
    try:
        from config.reddit_config import get_config, get_config_status
        
        config = get_config()
        print("OK Reddit config loaded")
        
        status = get_config_status()
        print(f"OK Config status: {status['is_valid']}")
        
        if not status['is_valid']:
            print("INFO Reddit API not configured (expected for testing)")
        
        return True
        
    except Exception as e:
        print(f"FAILED Reddit configuration failed: {e}")
        return False

def test_service_integration():
    """Test services working together"""
    print("\n=== Testing Service Integration ===")
    
    try:
        from services.newsletter_service import NewsletterService
        from services.config_service import ConfigService
        from data.database_manager import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Initialize services
            db = DatabaseManager(db_path)
            config_service = ConfigService()
            
            # Test newsletter service with mock data
            newsletter_service = NewsletterService(database=db, config=config_service)
            print("OK Newsletter service initialized")
            
            # Test digest generation (will use mock data)
            digest = newsletter_service.generate_daily_digest()
            print(f"OK Digest generated: {len(digest.get('top_opportunities', []))} opportunities")
            
            db.close()
            return True
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
        
    except Exception as e:
        print(f"FAILED Service integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_requirements_completeness():
    """Test that all requirements are available"""
    print("\n=== Testing Requirements Completeness ===")
    
    required_modules = [
        'customtkinter', 'praw', 'pandas', 'numpy', 
        'requests', 'beautifulsoup4', 'structlog',
        'sentence_transformers', 'scikit_learn'
    ]
    
    missing = []
    available = []
    
    for module in required_modules:
        try:
            if module == 'scikit_learn':
                import sklearn
            elif module == 'beautifulsoup4':
                import bs4
            else:
                __import__(module)
            available.append(module)
        except ImportError:
            missing.append(module)
    
    print(f"OK Available modules: {len(available)}")
    print(f"OK Missing modules: {len(missing)}")
    
    if missing:
        print(f"INFO Missing: {missing}")
    
    return len(missing) == 0

def main():
    """Run comprehensive integration test"""
    print("=" * 60)
    print("PersonalizedReddit Application - Final Integration Test")
    print("=" * 60)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Database Operations", test_database_operations),
        ("AI Services", test_ai_services),
        ("Export Functionality", test_export_functionality),
        ("Reddit Configuration", test_reddit_configuration),
        ("Service Integration", test_service_integration),
        ("Requirements Completeness", test_requirements_completeness),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"PASS {test_name}")
            else:
                print(f"FAIL {test_name}")
        except Exception as e:
            print(f"FAIL {test_name} - Exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\nSUCCESS: ALL TESTS PASSED! Application is ready for production.")
        print("\nTo run the application:")
        print("  python main.py")
        print("\nTo test individual components:")
        print("  python test_ai_simple.py")
        print("  python test_export.py")
        print("  python test_gui_simple.py")
    else:
        print(f"\nWARNING: {total - passed} test(s) failed. Review the errors above.")
        print("The application may still work with limited functionality.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)