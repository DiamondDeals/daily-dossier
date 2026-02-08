"""
AI Service for PersonalizedReddit
Integrates Hugging Face transformers for content analysis, summarization, and recommendations
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import numpy as np

# AI/ML imports - all optional with compatibility checks
try:
    # Fix numpy compatibility issue
    import numpy as np
    if not hasattr(np, 'complex'):
        # Add backward compatibility for older transformers
        np.complex = complex
        np.int = int
        np.float = float
        np.bool = bool
    
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        AutoModelForSeq2SeqLM, pipeline,
        BartForConditionalGeneration, BartTokenizer
    )
    TRANSFORMERS_AVAILABLE = True
except (ImportError, RuntimeError, AttributeError) as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"Transformers not available: {e}")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Set overall availability
ai_available = all([TRANSFORMERS_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE, TORCH_AVAILABLE, SKLEARN_AVAILABLE])

from utils.logging_config import get_logger, log_performance

class AIService:
    """
    Comprehensive AI service for Reddit content analysis
    Provides summarization, sentiment analysis, business opportunity detection,
    and recommendation capabilities using Hugging Face models
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.logger = get_logger(__name__)
        self.config = config or {}
        
        # Model configuration
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        
        # Performance settings
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.max_workers = self.config.get('ai_max_workers', 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Cache for embeddings and model outputs
        self.embeddings_cache = {}
        self.analysis_cache = {}
        
        # Business keyword patterns
        self.business_keywords = self._load_business_keywords()
        
        # Initialize models
        self._initialize_models()
        
        self.logger.info(f"AI Service initialized with device: {self.device}")
    
    def _load_business_keywords(self) -> Dict[str, List[str]]:
        """Load business opportunity keywords from JSON file"""
        try:
            keywords_file = "keywords.json"
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r') as f:
                    loaded_keywords = json.load(f)
                    
                    # Handle both list and dict formats
                    if isinstance(loaded_keywords, list):
                        # Convert list to categorized dict
                        return self._categorize_keywords(loaded_keywords)
                    elif isinstance(loaded_keywords, dict):
                        return loaded_keywords
        except Exception as e:
            self.logger.warning(f"Failed to load keywords: {e}")
        
        # Default business keywords
        return {
            "automation": [
                "automate", "automation", "manual process", "repetitive task",
                "streamline", "workflow", "efficiency", "time-consuming"
            ],
            "integration": [
                "integrate", "integration", "connect systems", "API",
                "data sync", "workflow", "process improvement"
            ],
            "scaling": [
                "scale", "scaling", "bottleneck", "capacity", "growth",
                "volume", "performance", "optimization"
            ],
            "pain_points": [
                "struggle", "difficult", "problem", "issue", "challenge",
                "frustrating", "time waste", "inefficient", "manual"
            ],
            "budget": [
                "budget", "cost", "price", "expensive", "cheap", "ROI",
                "investment", "worth", "value", "money"
            ]
        }
    
    def _categorize_keywords(self, keywords_list: List[str]) -> Dict[str, List[str]]:
        """Categorize a flat list of keywords"""
        categorized = {
            "automation": [],
            "integration": [],
            "scaling": [],
            "pain_points": [],
            "budget": [],
            "general": []
        }
        
        automation_terms = ["automate", "automation", "manual", "repetitive", "streamline", "workflow"]
        integration_terms = ["sync", "integration", "transfer", "export", "import", "connect", "systems"]
        scaling_terms = ["scale", "bottleneck", "hundreds", "thousands", "bulk", "mass", "optimize"]
        pain_terms = ["nightmare", "crazy", "struggle", "time-consuming", "tedious", "wasting"]
        budget_terms = ["cost", "expensive", "budget", "price", "investment"]
        
        for keyword in keywords_list:
            keyword_lower = keyword.lower()
            categorized_flag = False
            
            for term in automation_terms:
                if term in keyword_lower:
                    categorized["automation"].append(keyword)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                for term in integration_terms:
                    if term in keyword_lower:
                        categorized["integration"].append(keyword)
                        categorized_flag = True
                        break
            
            if not categorized_flag:
                for term in scaling_terms:
                    if term in keyword_lower:
                        categorized["scaling"].append(keyword)
                        categorized_flag = True
                        break
            
            if not categorized_flag:
                for term in pain_terms:
                    if term in keyword_lower:
                        categorized["pain_points"].append(keyword)
                        categorized_flag = True
                        break
            
            if not categorized_flag:
                for term in budget_terms:
                    if term in keyword_lower:
                        categorized["budget"].append(keyword)
                        categorized_flag = True
                        break
            
            if not categorized_flag:
                categorized["general"].append(keyword)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def _initialize_models(self):
        """Initialize all AI models"""
        # Check if we should skip model loading (for testing)
        if self.config.get('skip_model_loading', False):
            self.logger.info("Skipping model loading (test mode)")
            self._setup_business_classifier()
            return
            
        if not ai_available:
            self.logger.warning("AI dependencies not available. AI features will be limited.")
            return
        
        try:
            self.logger.info("Loading AI models...")
            
            # Only load models if explicitly requested and available
            if self.config.get('load_summarization', True):
                self._load_summarization_model()
            
            if self.config.get('load_sentiment', True):
                self._load_sentiment_model()
            
            if self.config.get('load_embeddings', True):
                self._load_sentence_transformer()
            
            # Business classification model (custom pipeline)
            self._setup_business_classifier()
            
            self.logger.info("AI models initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}", exc_info=True)
            # Don't raise - continue with fallback methods
            self.logger.warning("Continuing with fallback AI methods")
    
    def _load_summarization_model(self):
        """Load summarization model"""
        model_name = self.config.get('summarization_model', 'facebook/bart-large-cnn')
        
        try:
            self.tokenizers['summarization'] = BartTokenizer.from_pretrained(model_name)
            self.models['summarization'] = BartForConditionalGeneration.from_pretrained(model_name)
            self.models['summarization'].to(self.device)
            
            # Create pipeline for easier use
            self.pipelines['summarization'] = pipeline(
                "summarization",
                model=self.models['summarization'],
                tokenizer=self.tokenizers['summarization'],
                device=0 if self.device == "cuda" else -1
            )
            
            self.logger.info(f"Summarization model loaded: {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load summarization model: {e}")
            # Fallback to a simpler extraction-based summarization
            self.pipelines['summarization'] = None
    
    def _load_sentiment_model(self):
        """Load sentiment analysis model"""
        model_name = self.config.get('sentiment_model', 'cardiffnlp/twitter-roberta-base-sentiment-latest')
        
        try:
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=0 if self.device == "cuda" else -1
            )
            
            self.logger.info(f"Sentiment model loaded: {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load sentiment model: {e}")
            self.pipelines['sentiment'] = None
    
    def _load_sentence_transformer(self):
        """Load sentence transformer for embeddings"""
        model_name = self.config.get('embedding_model', 'all-MiniLM-L6-v2')
        
        try:
            self.models['embeddings'] = SentenceTransformer(model_name)
            self.logger.info(f"Sentence transformer loaded: {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load sentence transformer: {e}")
            self.models['embeddings'] = None
    
    def _setup_business_classifier(self):
        """Setup custom business opportunity classifier"""
        # This could be a custom model trained on business data
        # For now, we'll use keyword-based classification
        self.business_classifier = {
            'keywords': self.business_keywords,
            'weights': {
                'automation': 2.0,
                'integration': 1.8,
                'scaling': 1.6,
                'pain_points': 1.4,
                'budget': 1.2
            }
        }
    
    @log_performance
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 50) -> Dict[str, Any]:
        """
        Generate a summary of the given text
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Dictionary containing summary and metadata
        """
        if not text or len(text.strip()) < 50:
            return {
                'summary': text[:100] + "..." if len(text) > 100 else text,
                'confidence': 0.1,
                'method': 'truncation',
                'word_count': len(text.split())
            }
        
        # Check cache first
        cache_key = f"summary_{hash(text)}_{max_length}_{min_length}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        try:
            if self.pipelines.get('summarization'):
                # Use AI summarization
                result = self.pipelines['summarization'](
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                
                summary_result = {
                    'summary': result[0]['summary_text'],
                    'confidence': 0.9,
                    'method': 'ai_bart',
                    'word_count': len(result[0]['summary_text'].split()),
                    'original_length': len(text.split()),
                    'compression_ratio': len(result[0]['summary_text'].split()) / len(text.split())
                }
            else:
                # Fallback to extractive summarization
                summary_result = self._extractive_summarization(text, max_length)
            
            # Cache the result
            self.analysis_cache[cache_key] = summary_result
            return summary_result
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            # Fallback to simple truncation
            return {
                'summary': text[:max_length * 4] + "..." if len(text) > max_length * 4 else text,
                'confidence': 0.2,
                'method': 'truncation_fallback',
                'word_count': len(text.split()[:max_length]),
                'error': str(e)
            }
    
    def _extractive_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Simple extractive summarization fallback"""
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return {
                'summary': text,
                'confidence': 0.6,
                'method': 'full_text',
                'word_count': len(text.split())
            }
        
        # Take first sentence, middle sentences, and last sentence
        summary_sentences = []
        summary_sentences.append(sentences[0])
        
        if len(sentences) > 4:
            mid_point = len(sentences) // 2
            summary_sentences.append(sentences[mid_point])
        
        if len(sentences) > 2:
            summary_sentences.append(sentences[-1])
        
        summary = '. '.join(summary_sentences)
        if not summary.endswith('.'):
            summary += '.'
        
        return {
            'summary': summary,
            'confidence': 0.6,
            'method': 'extractive',
            'word_count': len(summary.split()),
            'sentences_selected': len(summary_sentences)
        }
    
    @log_performance
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        if not text or len(text.strip()) < 10:
            return {
                'label': 'NEUTRAL',
                'score': 0.5,
                'confidence': 0.1,
                'method': 'default'
            }
        
        cache_key = f"sentiment_{hash(text)}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        try:
            if self.pipelines.get('sentiment'):
                result = self.pipelines['sentiment'](text[:512])  # Limit length for model
                
                sentiment_result = {
                    'label': result[0]['label'],
                    'score': result[0]['score'],
                    'confidence': result[0]['score'],
                    'method': 'ai_roberta'
                }
            else:
                # Simple keyword-based sentiment analysis
                sentiment_result = self._keyword_sentiment_analysis(text)
            
            self.analysis_cache[cache_key] = sentiment_result
            return sentiment_result
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {
                'label': 'NEUTRAL',
                'score': 0.5,
                'confidence': 0.2,
                'method': 'fallback',
                'error': str(e)
            }
    
    def _keyword_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based sentiment analysis fallback"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'horrible', 'hate', 'worst', 'awful', 'disappointing', 'frustrating']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {'label': 'NEUTRAL', 'score': 0.5, 'confidence': 0.3, 'method': 'keyword_fallback'}
        
        sentiment_score = positive_count / total_sentiment_words
        
        if sentiment_score > 0.6:
            label = 'POSITIVE'
        elif sentiment_score < 0.4:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        return {
            'label': label,
            'score': sentiment_score,
            'confidence': min(0.7, total_sentiment_words / 10),
            'method': 'keyword_fallback',
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    @log_performance
    def detect_business_opportunities(self, text: str) -> Dict[str, Any]:
        """
        Detect business opportunities in text using keyword analysis and AI
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing business opportunity analysis
        """
        cache_key = f"business_{hash(text)}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        try:
            # Keyword-based analysis
            keyword_analysis = self._analyze_business_keywords(text)
            
            # Sentiment analysis for urgency detection
            sentiment = self.analyze_sentiment(text)
            
            # Calculate opportunity score
            opportunity_score = self._calculate_opportunity_score(keyword_analysis, sentiment)
            
            # Detect specific business categories
            categories = self._detect_business_categories(text, keyword_analysis)
            
            result = {
                'opportunity_score': opportunity_score,
                'categories': categories,
                'keywords_found': keyword_analysis['matched_keywords'],
                'keyword_count': keyword_analysis['total_matches'],
                'sentiment': sentiment,
                'urgency_level': self._assess_urgency(text, sentiment),
                'confidence': min(1.0, keyword_analysis['total_matches'] * 0.2 + sentiment['confidence'] * 0.3),
                'recommendations': self._generate_opportunity_recommendations(keyword_analysis, categories)
            }
            
            self.analysis_cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Business opportunity detection failed: {e}")
            return {
                'opportunity_score': 0.0,
                'categories': [],
                'keywords_found': {},
                'keyword_count': 0,
                'sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                'urgency_level': 'low',
                'confidence': 0.1,
                'error': str(e)
            }
    
    def _analyze_business_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze text for business-related keywords"""
        text_lower = text.lower()
        matched_keywords = {}
        total_score = 0.0
        
        for category, keywords in self.business_keywords.items():
            category_matches = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    category_matches.append(keyword)
            
            if category_matches:
                matched_keywords[category] = category_matches
                # Apply category weight
                weight = self.business_classifier['weights'].get(category, 1.0)
                total_score += len(category_matches) * weight
        
        return {
            'matched_keywords': matched_keywords,
            'total_matches': sum(len(matches) for matches in matched_keywords.values()),
            'weighted_score': total_score,
            'categories_matched': len(matched_keywords)
        }
    
    def _calculate_opportunity_score(self, keyword_analysis: Dict, sentiment: Dict) -> float:
        """Calculate business opportunity score"""
        # Base score from keywords
        keyword_score = min(10.0, keyword_analysis['weighted_score'])
        
        # Sentiment modifier
        sentiment_modifier = 1.0
        if sentiment['label'] == 'NEGATIVE':
            sentiment_modifier = 1.5  # Negative sentiment might indicate pain points
        elif sentiment['label'] == 'POSITIVE':
            sentiment_modifier = 0.8  # Positive might mean they already have solutions
        
        # Final score (0-10 scale)
        final_score = (keyword_score * sentiment_modifier) / 2.0
        return round(min(10.0, max(0.0, final_score)), 2)
    
    def _detect_business_categories(self, text: str, keyword_analysis: Dict) -> List[str]:
        """Detect specific business categories"""
        categories = []
        
        # Map keywords to business categories
        category_mapping = {
            'Process Automation': ['automation', 'pain_points'],
            'System Integration': ['integration'],
            'Business Scaling': ['scaling'],
            'Cost Optimization': ['budget'],
            'Workflow Improvement': ['automation', 'pain_points']
        }
        
        for category, required_types in category_mapping.items():
            if any(kw_type in keyword_analysis['matched_keywords'] for kw_type in required_types):
                categories.append(category)
        
        return categories
    
    def _assess_urgency(self, text: str, sentiment: Dict) -> str:
        """Assess urgency level of the business need"""
        urgency_keywords = {
            'high': ['urgent', 'asap', 'immediately', 'crisis', 'emergency', 'breaking', 'critical'],
            'medium': ['soon', 'quickly', 'fast', 'deadline', 'rushing', 'hurry'],
            'low': ['eventually', 'someday', 'thinking about', 'considering', 'maybe']
        }
        
        text_lower = text.lower()
        
        for level, keywords in urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        # Use sentiment as additional indicator
        if sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.7:
            return 'medium'
        
        return 'low'
    
    def _generate_opportunity_recommendations(self, keyword_analysis: Dict, categories: List[str]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if 'automation' in keyword_analysis['matched_keywords']:
            recommendations.append("Consider offering process automation consulting")
        
        if 'integration' in keyword_analysis['matched_keywords']:
            recommendations.append("API integration services could be valuable")
        
        if 'scaling' in keyword_analysis['matched_keywords']:
            recommendations.append("Scalability solutions might be needed")
        
        if 'pain_points' in keyword_analysis['matched_keywords']:
            recommendations.append("Pain point analysis could reveal opportunities")
        
        if len(categories) > 2:
            recommendations.append("Multiple business areas identified - comprehensive solution needed")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    @log_performance
    def generate_content_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for content similarity analysis"""
        if not self.models.get('embeddings'):
            # Fallback to simple TF-IDF if sentence transformer not available
            return self._simple_text_embeddings(texts)
        
        try:
            embeddings = self.models['embeddings'].encode(texts)
            return embeddings
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            return self._simple_text_embeddings(texts)
    
    def _simple_text_embeddings(self, texts: List[str]) -> np.ndarray:
        """Simple TF-IDF based embeddings fallback"""
        if SKLEARN_AVAILABLE:
            try:
                vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
                embeddings = vectorizer.fit_transform(texts).toarray()
                return embeddings
            except Exception as e:
                self.logger.error(f"TF-IDF embedding failed: {e}")
        
        # Ultra simple word-based embeddings if sklearn not available
        try:
            import numpy as np
            # Create simple word frequency vectors
            all_words = set()
            for text in texts:
                all_words.update(text.lower().split())
            
            word_list = list(all_words)[:100]  # Limit to 100 most common words
            embeddings = []
            
            for text in texts:
                words = text.lower().split()
                vector = [words.count(word) for word in word_list]
                embeddings.append(vector)
            
            return np.array(embeddings)
        except Exception as e:
            self.logger.error(f"Simple embedding failed: {e}")
            # Return zero embeddings as last resort
            return np.zeros((len(texts), 100))
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            embeddings = self.generate_content_embeddings([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            # Fallback to simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            return len(words1.intersection(words2)) / len(words1.union(words2))
    
    def cluster_content(self, texts: List[str], n_clusters: int = 5) -> Dict[str, Any]:
        """Cluster content using embeddings"""
        if len(texts) < n_clusters:
            return {
                'clusters': list(range(len(texts))),
                'cluster_centers': [],
                'method': 'no_clustering'
            }
        
        try:
            embeddings = self.generate_content_embeddings(texts)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            return {
                'clusters': cluster_labels.tolist(),
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'inertia': kmeans.inertia_,
                'method': 'kmeans'
            }
        except Exception as e:
            self.logger.error(f"Clustering failed: {e}")
            # Random assignment fallback
            return {
                'clusters': [i % n_clusters for i in range(len(texts))],
                'cluster_centers': [],
                'method': 'random_fallback',
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'device': self.device,
            'models_loaded': list(self.models.keys()),
            'pipelines_loaded': list(self.pipelines.keys()),
            'cache_size': {
                'embeddings': len(self.embeddings_cache),
                'analysis': len(self.analysis_cache)
            },
            'business_categories': list(self.business_keywords.keys()),
            'ai_available': ai_available
        }
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Clear AI service caches"""
        if cache_type == 'embeddings' or cache_type is None:
            self.embeddings_cache.clear()
        
        if cache_type == 'analysis' or cache_type is None:
            self.analysis_cache.clear()
        
        self.logger.info(f"Cleared {cache_type or 'all'} caches")
    
    def close(self):
        """Clean up resources"""
        try:
            self.thread_pool.shutdown(wait=True)
            self.clear_cache()
            
            # Clear models from memory if using CUDA
            if self.device == "cuda" and TORCH_AVAILABLE:
                for model in self.models.values():
                    if hasattr(model, 'to'):
                        model.to('cpu')
                torch.cuda.empty_cache()
            
            self.logger.info("AI Service closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing AI Service: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Test the AI service
    ai_service = AIService()
    
    test_text = """
    I'm struggling with manual data entry for my small business. Every day I spend 
    hours copying information from emails into our inventory system. This process 
    is so time-consuming and error-prone. I'm looking for a way to automate this 
    workflow. Does anyone know of a good solution for integrating email data with 
    inventory management systems?
    """
    
    print("=== AI Service Test ===")
    print(f"Model Info: {ai_service.get_model_info()}")
    print()
    
    # Test summarization
    summary = ai_service.summarize_text(test_text)
    print(f"Summary: {summary}")
    print()
    
    # Test sentiment analysis
    sentiment = ai_service.analyze_sentiment(test_text)
    print(f"Sentiment: {sentiment}")
    print()
    
    # Test business opportunity detection
    opportunity = ai_service.detect_business_opportunities(test_text)
    print(f"Business Opportunity: {opportunity}")
    print()
    
    ai_service.close()