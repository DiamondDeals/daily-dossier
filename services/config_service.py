"""
Configuration Service for PersonalizedReddit
Manages application configuration and user preferences
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from utils.logging_config import get_logger

class ConfigService:
    """Simple configuration service"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = get_logger(__name__)
        
        # Default settings
        self.settings = {
            'theme': 'dark',
            'default_export_format': 'csv',
            'ai_processing_enabled': True,
            'max_posts_per_fetch': 100
        }
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        config_file = self.config_dir / "app_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                self.settings.update(loaded_config)
                self.logger.info("Configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        self.settings[key] = value
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        config_file = self.config_dir / "app_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            self.logger.debug("Configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference (alias for set_setting)"""
        self.set_setting(key, value)