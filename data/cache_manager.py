"""
Cache Manager for PersonalizedReddit
Handles in-memory caching for performance optimization
"""

import time
import json
import threading
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
from utils.logging_config import get_logger

class CacheManager:
    """
    Thread-safe cache manager with TTL support and LRU eviction
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.logger = get_logger(__name__)
        
        # Cache storage with thread safety
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        
        self.logger.info(f"Cache manager initialized with max_size={max_size}, default_ttl={default_ttl}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self.stats['misses'] += 1
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if expiry and datetime.now() > expiry:
                del self._cache[key]
                self.stats['misses'] += 1
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            self.stats['hits'] += 1
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        ttl = ttl if ttl is not None else self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        
        with self._lock:
            # Remove existing key if present
            if key in self._cache:
                del self._cache[key]
            
            # Add new entry
            self._cache[key] = (value, expiry)
            
            # Enforce size limit
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self.stats['evictions'] += 1
            
            self.stats['size'] = len(self._cache)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.stats['size'] = len(self._cache)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self.stats['size'] = 0
            self.logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = []
        
        with self._lock:
            for key, (value, expiry) in self._cache.items():
                if expiry and now > expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            self.stats['size'] = len(self._cache)
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate': round(hit_rate, 3),
                'total_requests': total_requests
            }

class ConfigManager:
    """
    Configuration manager for application settings and user preferences
    """
    
    def __init__(self, database_manager=None):
        self.database = database_manager
        self.cache = CacheManager(max_size=100, default_ttl=3600)  # 1 hour cache
        self.logger = get_logger(__name__)
        
        # Default configuration
        self.defaults = {
            'theme': 'dark',
            'auto_refresh_interval': 300,  # 5 minutes
            'max_posts_per_fetch': 100,
            'ai_analysis_enabled': True,
            'export_format': 'csv',
            'notification_enabled': True,
            'debug_mode': False
        }
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference with caching"""
        cache_key = f"pref_{key}"
        
        # Try cache first
        cached_value = self.cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        # Try database
        if self.database:
            try:
                value = self.database.get_setting(key, default or self.defaults.get(key))
                if value is not None:
                    self.cache.set(cache_key, value)
                    return value
            except Exception as e:
                self.logger.error(f"Failed to get preference {key}: {e}")
        
        # Return default
        return default or self.defaults.get(key)
    
    def set_user_preference(self, key: str, value: Any) -> None:
        """Set user preference"""
        cache_key = f"pref_{key}"
        
        # Update cache
        self.cache.set(cache_key, value)
        
        # Update database
        if self.database:
            try:
                self.database.set_setting(key, value)
                self.logger.debug(f"Set preference {key} = {value}")
            except Exception as e:
                self.logger.error(f"Failed to set preference {key}: {e}")
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        preferences = self.defaults.copy()
        
        if self.database:
            try:
                # This would need a method to get all settings
                # For now, return defaults
                pass
            except Exception as e:
                self.logger.error(f"Failed to get all preferences: {e}")
        
        return preferences
    
    def reset_preferences(self) -> None:
        """Reset preferences to defaults"""
        self.cache.clear()
        
        if self.database:
            try:
                for key, value in self.defaults.items():
                    self.database.set_setting(key, value)
                self.logger.info("Preferences reset to defaults")
            except Exception as e:
                self.logger.error(f"Failed to reset preferences: {e}")