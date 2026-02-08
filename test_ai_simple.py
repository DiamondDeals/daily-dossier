#!/usr/bin/env python3
"""
Simple AI Service test without heavy model downloads
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_service_lightweight():
    """Test AI service with lightweight configuration"""
    print("Testing AI Service in lightweight mode...")
    
    try:
        # Import with fallback configuration
        from services.ai_service import AIService
        
        # Create offline config for testing
        offline_config = {
            'ai_max_workers': 1,
            'skip_model_loading': True,  # Skip downloading models
            'load_summarization': False,
            'load_sentiment': False,
            'load_embeddings': False
        }
        
        # Initialize service
        ai_service = AIService(config=offline_config)
        print("OK AI Service initialized")
        
        # Get model info
        model_info = ai_service.get_model_info()
        print(f"OK Model info: {model_info}")
        
        # Test text
        test_text = """I am struggling with manual data entry for my small business. 
        Every day I spend hours copying information from emails into our inventory system. 
        This process is time-consuming and error-prone. I need automation help."""
        
        print("\nTesting AI analysis functions...")
        
        # Test business opportunity detection (keyword-based)
        opportunity = ai_service.detect_business_opportunities(test_text)
        print(f"OK Business opportunity score: {opportunity.get('opportunity_score', 0)}")
        print(f"OK Categories found: {opportunity.get('categories', [])}")
        print(f"OK Keywords found: {list(opportunity.get('keywords_found', {}).keys())}")
        print(f"OK Urgency level: {opportunity.get('urgency_level', 'unknown')}")
        
        # Test sentiment analysis (fallback mode)
        sentiment = ai_service.analyze_sentiment(test_text)
        print(f"OK Sentiment: {sentiment.get('label', 'unknown')} (method: {sentiment.get('method', 'unknown')})")
        
        # Test summarization (fallback mode)
        summary = ai_service.summarize_text(test_text)
        print(f"OK Summary method: {summary.get('method', 'unknown')}")
        print(f"OK Summary confidence: {summary.get('confidence', 0)}")
        
        # Test similarity calculation
        text1 = "automation software"
        text2 = "manual process improvement"
        similarity = ai_service.calculate_similarity(text1, text2)
        print(f"OK Text similarity: {similarity:.2f}")
        
        # Test embeddings (fallback mode)
        test_texts = [test_text, "Different text about something else"]
        embeddings = ai_service.generate_content_embeddings(test_texts)
        print(f"OK Embeddings shape: {embeddings.shape}")
        
        ai_service.close()
        print("\nOK AI Service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"FAILED AI Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_service_lightweight()
    sys.exit(0 if success else 1)