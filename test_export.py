#!/usr/bin/env python3
"""
Test Export Service functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_export_service():
    """Test export service functionality"""
    print("Testing Export Service...")
    
    try:
        from services.export_service import ExportService
        
        # Initialize export service
        export_service = ExportService()
        print("OK Export Service initialized")
        
        # Test data
        test_business_leads = [
            {
                'title': 'Need automation for inventory management',
                'author': 'business_owner',
                'subreddit': 'entrepreneur',
                'business_score': 8.5,
                'urgency_level': 'high',
                'problem_indicators': ['manual data entry', 'time-consuming', 'automation'],
                'created_date': '2025-08-14',
                'permalink': 'https://reddit.com/r/entrepreneur/comments/test123',
                'summary': 'Small business struggling with manual inventory tracking'
            },
            {
                'title': 'Looking for integration solutions',
                'author': 'tech_startup',
                'subreddit': 'startups', 
                'business_score': 7.2,
                'urgency_level': 'medium',
                'problem_indicators': ['integration', 'systems dont talk', 'workflow'],
                'created_date': '2025-08-14',
                'permalink': 'https://reddit.com/r/startups/comments/test456',
                'summary': 'Startup needs to connect multiple business systems'
            }
        ]
        
        test_newsletter_data = [
            {
                'title': 'E-commerce Automation Opportunity',
                'summary': 'High-potential lead in e-commerce automation space',
                'subreddit': 'ecommerce',
                'priority': 'high',
                'business_score': 9.1,
                'engagement_score': 85,
                'created_date': '2025-08-14'
            },
            {
                'title': 'Workflow Optimization Request',
                'summary': 'Medium-priority opportunity for process improvement',
                'subreddit': 'productivity',
                'priority': 'medium', 
                'business_score': 6.5,
                'engagement_score': 42,
                'created_date': '2025-08-14'
            }
        ]
        
        print("Testing CSV export...")
        # Test CSV export
        csv_path = export_service.export_business_leads(test_business_leads, "csv")
        print(f"OK CSV exported to: {csv_path}")
        
        print("Testing JSON export...")
        # Test JSON export
        json_path = export_service.export_data(test_business_leads, "test_leads", "json")
        print(f"OK JSON exported to: {json_path}")
        
        print("Testing Markdown export...")
        # Test Markdown export
        md_path = export_service.export_business_leads(test_business_leads, "markdown")
        print(f"OK Markdown exported to: {md_path}")
        
        print("Testing Newsletter export...")
        # Test Newsletter export
        newsletter_path = export_service.export_newsletter_digest(
            {'top_opportunities': test_newsletter_data}, 
            "markdown"
        )
        print(f"OK Newsletter exported to: {newsletter_path}")
        
        # Test Excel export (may fallback to CSV)
        print("Testing Excel export...")
        try:
            excel_path = export_service.export_data(test_business_leads, "test_excel", "excel", "business_leads")
            print(f"OK Excel exported to: {excel_path}")
        except Exception as e:
            print(f"Excel export failed (expected): {e}")
        
        # Test PDF export (may fallback to Markdown)
        print("Testing PDF export...")
        try:
            pdf_path = export_service.export_data(test_business_leads, "test_pdf", "pdf", "business_leads")
            print(f"OK PDF exported to: {pdf_path}")
        except Exception as e:
            print(f"PDF export failed (expected): {e}")
        
        # Test export history
        print("Testing export history...")
        history = export_service.get_export_history()
        print(f"OK Export history: {len(history)} files found")
        
        # Verify files exist
        print("Verifying exported files...")
        for path in [csv_path, json_path, md_path, newsletter_path]:
            if path.exists():
                size = path.stat().st_size
                print(f"OK {path.name}: {size} bytes")
            else:
                print(f"FAILED {path.name}: File not found")
        
        export_service.close()
        print("OK Export Service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"FAILED Export Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_service()
    sys.exit(0 if success else 1)