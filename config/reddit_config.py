"""
Reddit Configuration Management for PersonalizedReddit
Handles Reddit API credentials, settings, and configuration
"""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logging_config import get_logger
from dataclasses import dataclass
from typing import Optional

@dataclass
class RedditCredentials:
    """Reddit API credentials data class"""
    client_id: str
    client_secret: str
    user_agent: str
    redirect_uri: str = "http://localhost:8080/reddit/callback"
    username: Optional[str] = None
    password: Optional[str] = None

class RedditConfig:
    """
    Reddit API configuration management
    """
    
    def __init__(self, config_file: str = "config/reddit_settings.ini"):
        self.logger = get_logger(__name__)
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config_data = {}
        
        # Ensure config directory exists
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        try:
            # Load from config file if it exists
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
                self.logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self._create_default_config()
            
            # Override with environment variables if available
            self._load_from_environment()
            
            # Build final config dictionary
            self._build_config_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._create_fallback_config()
    
    def _create_default_config(self):
        """Create default configuration file"""
        try:
            self.config['REDDIT_API'] = {
                'client_id': '',
                'client_secret': '',
                'user_agent': 'PersonalizedReddit/1.0 by YourUsername',
                'redirect_uri': 'http://localhost:8080/reddit/callback',
                'username': '',
                'password': ''
            }
            
            self.config['API_SETTINGS'] = {
                'rate_limit_requests': '60',
                'rate_limit_period': '60',
                'timeout': '30',
                'max_retries': '3',
                'backoff_factor': '2.0'
            }
            
            self.config['SCRAPING'] = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'delay_between_requests': '1.0',
                'max_concurrent_requests': '5',
                'enable_fallback_scraping': 'true'
            }
            
            self.config['SEARCH'] = {
                'default_subreddits': 'entrepreneur,smallbusiness,freelance,automation,productivity',
                'default_limit': '100',
                'default_sort': 'relevance',
                'time_filter': 'month'
            }
            
            # Save the default config
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            self.logger.info(f"Created default configuration at {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default config: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'REDDIT_CLIENT_ID': ('REDDIT_API', 'client_id'),
            'REDDIT_CLIENT_SECRET': ('REDDIT_API', 'client_secret'),
            'REDDIT_USER_AGENT': ('REDDIT_API', 'user_agent'),
            'REDDIT_USERNAME': ('REDDIT_API', 'username'),
            'REDDIT_PASSWORD': ('REDDIT_API', 'password'),
            'REDDIT_REDIRECT_URI': ('REDDIT_API', 'redirect_uri')
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if not self.config.has_section(section):
                    self.config.add_section(section)
                self.config.set(section, key, value)
                self.logger.debug(f"Loaded {env_var} from environment")
    
    def _build_config_dict(self):
        """Build configuration dictionary from ConfigParser"""
        self.config_data = {
            'reddit_api': {
                'client_id': self.config.get('REDDIT_API', 'client_id', fallback=''),
                'client_secret': self.config.get('REDDIT_API', 'client_secret', fallback=''),
                'user_agent': self.config.get('REDDIT_API', 'user_agent', fallback='PersonalizedReddit/1.0'),
                'redirect_uri': self.config.get('REDDIT_API', 'redirect_uri', fallback='http://localhost:8080/reddit/callback'),
                'username': self.config.get('REDDIT_API', 'username', fallback=''),
                'password': self.config.get('REDDIT_API', 'password', fallback='')
            },
            'api_settings': {
                'rate_limit_requests': self.config.getint('API_SETTINGS', 'rate_limit_requests', fallback=60),
                'rate_limit_period': self.config.getint('API_SETTINGS', 'rate_limit_period', fallback=60),
                'timeout': self.config.getint('API_SETTINGS', 'timeout', fallback=30),
                'max_retries': self.config.getint('API_SETTINGS', 'max_retries', fallback=3),
                'backoff_factor': self.config.getfloat('API_SETTINGS', 'backoff_factor', fallback=2.0)
            },
            'scraping': {
                'user_agent': self.config.get('SCRAPING', 'user_agent', fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
                'delay_between_requests': self.config.getfloat('SCRAPING', 'delay_between_requests', fallback=1.0),
                'max_concurrent_requests': self.config.getint('SCRAPING', 'max_concurrent_requests', fallback=5),
                'enable_fallback_scraping': self.config.getboolean('SCRAPING', 'enable_fallback_scraping', fallback=True)
            },
            'search': {
                'default_subreddits': self.config.get('SEARCH', 'default_subreddits', fallback='entrepreneur,smallbusiness,freelance').split(','),
                'default_limit': self.config.getint('SEARCH', 'default_limit', fallback=100),
                'default_sort': self.config.get('SEARCH', 'default_sort', fallback='relevance'),
                'time_filter': self.config.get('SEARCH', 'time_filter', fallback='month')
            }
        }
    
    def _create_fallback_config(self):
        """Create minimal fallback configuration"""
        self.config_data = {
            'reddit_api': {
                'client_id': '',
                'client_secret': '',
                'user_agent': 'PersonalizedReddit/1.0',
                'redirect_uri': 'http://localhost:8080/reddit/callback',
                'username': '',
                'password': ''
            },
            'api_settings': {
                'rate_limit_requests': 60,
                'rate_limit_period': 60,
                'timeout': 30,
                'max_retries': 3,
                'backoff_factor': 2.0
            },
            'scraping': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'delay_between_requests': 1.0,
                'max_concurrent_requests': 5,
                'enable_fallback_scraping': True
            },
            'search': {
                'default_subreddits': ['entrepreneur', 'smallbusiness', 'freelance'],
                'default_limit': 100,
                'default_sort': 'relevance',
                'time_filter': 'month'
            }
        }
        self.logger.warning("Using fallback configuration")
    
    def get_reddit_credentials(self) -> Dict[str, str]:
        """Get Reddit API credentials"""
        return self.config_data.get('reddit_api', {})
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API rate limiting and connection settings"""
        return self.config_data.get('api_settings', {})
    
    def get_scraping_settings(self) -> Dict[str, Any]:
        """Get web scraping settings"""
        return self.config_data.get('scraping', {})
    
    def get_search_settings(self) -> Dict[str, Any]:
        """Get search configuration"""
        return self.config_data.get('search', {})
    
    def is_configured(self) -> bool:
        """Check if Reddit API is properly configured"""
        credentials = self.get_reddit_credentials()
        required_fields = ['client_id', 'client_secret']
        
        return all(credentials.get(field) for field in required_fields)
    
    def update_credentials(self, credentials: Dict[str, str]):
        """Update Reddit API credentials"""
        try:
            reddit_section = 'REDDIT_API'
            if not self.config.has_section(reddit_section):
                self.config.add_section(reddit_section)
            
            for key, value in credentials.items():
                if key in ['client_id', 'client_secret', 'user_agent', 'username', 'password', 'redirect_uri']:
                    self.config.set(reddit_section, key, value)
            
            # Save updated config
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            # Rebuild config dict
            self._build_config_dict()
            
            self.logger.info("Updated Reddit credentials")
            
        except Exception as e:
            self.logger.error(f"Failed to update credentials: {e}")
            raise
    
    def update_setting(self, section: str, key: str, value: Any):
        """Update a specific configuration setting"""
        try:
            section_map = {
                'reddit_api': 'REDDIT_API',
                'api_settings': 'API_SETTINGS',
                'scraping': 'SCRAPING',
                'search': 'SEARCH'
            }
            
            config_section = section_map.get(section)
            if not config_section:
                raise ValueError(f"Unknown section: {section}")
            
            if not self.config.has_section(config_section):
                self.config.add_section(config_section)
            
            self.config.set(config_section, key, str(value))
            
            # Save updated config
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            # Rebuild config dict
            self._build_config_dict()
            
            self.logger.info(f"Updated {section}.{key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to update setting {section}.{key}: {e}")
            raise
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get configuration status and validation"""
        credentials = self.get_reddit_credentials()
        
        status = {
            'config_file_exists': os.path.exists(self.config_file),
            'is_configured': self.is_configured(),
            'has_client_id': bool(credentials.get('client_id')),
            'has_client_secret': bool(credentials.get('client_secret')),
            'has_user_agent': bool(credentials.get('user_agent')),
            'has_username': bool(credentials.get('username')),
            'has_password': bool(credentials.get('password')),
            'config_file_path': os.path.abspath(self.config_file)
        }
        
        # Add validation messages
        messages = []
        if not status['is_configured']:
            messages.append("Reddit API credentials not configured")
        if not status['has_client_id']:
            messages.append("Missing client_id")
        if not status['has_client_secret']:
            messages.append("Missing client_secret")
        
        status['messages'] = messages
        status['is_valid'] = len(messages) == 0
        
        return status
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for Reddit API"""
        return """
Reddit API Setup Instructions:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill out the form:
   - Name: PersonalizedReddit
   - App type: Choose "script"
   - Description: (optional)
   - About URL: (optional)
   - Redirect URI: http://localhost:8080/reddit/callback

4. After creating the app, you'll see:
   - Client ID: (string under the app name)
   - Client Secret: (secret key)

5. Add these to your configuration:
   - Set REDDIT_CLIENT_ID environment variable OR
   - Edit config/reddit_settings.ini file OR
   - Use the app settings dialog

6. Optionally add your Reddit username/password for enhanced features

Environment Variables:
- REDDIT_CLIENT_ID=your_client_id
- REDDIT_CLIENT_SECRET=your_client_secret
- REDDIT_USER_AGENT=PersonalizedReddit/1.0 by YourUsername
- REDDIT_USERNAME=your_reddit_username (optional)
- REDDIT_PASSWORD=your_reddit_password (optional)
"""
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration for backup or sharing"""
        config_export = self.config_data.copy()
        
        if not include_secrets:
            # Remove sensitive information
            if 'reddit_api' in config_export:
                sensitive_keys = ['client_secret', 'password']
                for key in sensitive_keys:
                    if key in config_export['reddit_api']:
                        config_export['reddit_api'][key] = '***HIDDEN***'
        
        return config_export
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        credentials = self.get_reddit_credentials()
        
        # Required field validation
        if not credentials.get('client_id'):
            validation_result['errors'].append("Missing Reddit client_id")
            validation_result['is_valid'] = False
        
        if not credentials.get('client_secret'):
            validation_result['errors'].append("Missing Reddit client_secret")
            validation_result['is_valid'] = False
        
        # User agent validation
        user_agent = credentials.get('user_agent', '')
        if not user_agent:
            validation_result['errors'].append("Missing user_agent")
            validation_result['is_valid'] = False
        elif 'PersonalizedReddit' not in user_agent:
            validation_result['warnings'].append("User agent should include 'PersonalizedReddit'")
        
        # Optional but recommended fields
        if not credentials.get('username'):
            validation_result['recommendations'].append("Consider adding Reddit username for enhanced features")
        
        if not credentials.get('password'):
            validation_result['recommendations'].append("Consider adding Reddit password for full API access")
        
        # API settings validation
        api_settings = self.get_api_settings()
        if api_settings.get('rate_limit_requests', 0) > 100:
            validation_result['warnings'].append("Rate limit may be too high (Reddit allows 60 requests/minute)")
        
        return validation_result


def get_config() -> Dict[str, Any]:
    """
    Get Reddit configuration - main entry point for the application
    """
    config_manager = RedditConfig()
    return config_manager.config_data


def is_reddit_configured() -> bool:
    """
    Check if Reddit API is configured
    """
    config_manager = RedditConfig()
    return config_manager.is_configured()


def get_reddit_credentials() -> Dict[str, str]:
    """
    Get Reddit API credentials
    """
    config_manager = RedditConfig()
    return config_manager.get_reddit_credentials()


def update_reddit_credentials(credentials: Dict[str, str]):
    """
    Update Reddit API credentials
    """
    config_manager = RedditConfig()
    config_manager.update_credentials(credentials)


def get_config_status() -> Dict[str, Any]:
    """
    Get configuration status for UI display
    """
    config_manager = RedditConfig()
    return config_manager.get_config_status()


def get_setup_instructions() -> str:
    """
    Get setup instructions for Reddit API
    """
    config_manager = RedditConfig()
    return config_manager.get_setup_instructions()


# Example usage and testing
if __name__ == "__main__":
    print("=== Reddit Configuration Test ===")
    
    config_manager = RedditConfig()
    
    print("Configuration Status:")
    status = config_manager.get_config_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\nValidation:")
    validation = config_manager.validate_config()
    print(f"  Valid: {validation['is_valid']}")
    if validation['errors']:
        print("  Errors:")
        for error in validation['errors']:
            print(f"    - {error}")
    
    if validation['warnings']:
        print("  Warnings:")
        for warning in validation['warnings']:
            print(f"    - {warning}")
    
    if not config_manager.is_configured():
        print("\nSetup Instructions:")
        print(config_manager.get_setup_instructions())