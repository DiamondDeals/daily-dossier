"""
PersonalizedReddit - Main Application Controller
Manages the overall application lifecycle, navigation, and component coordination
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import sys
from pathlib import Path

# Import services
from services.reddit_api_service import RedditAPIService
from services.ai_service import AIService
from services.newsletter_service import NewsletterService
from services.live_reddit_service import LiveRedditService
from services.ai_recommendation_service import AIRecommendationService
from services.export_service import ExportService

# Import data managers
from data.database_manager import DatabaseManager
from data.cache_manager import CacheManager
from data.config_manager import ConfigManager

# Import UI components
from ui.views.home_view import HomeView
from ui.views.live_view import LiveView
from ui.views.discover_view import DiscoverView
from ui.components.navigation import NavigationFrame

# Import utilities
from utils.logging_config import get_logger

class PersonalizedRedditApp:
    """Main application controller and window manager"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize core services
        self.services = {}
        self.views = {}
        
        # Application state
        self.current_view = None
        self.is_closing = False
        self.theme_mode = "dark"
        
        # Initialize the main window
        self._setup_window()
        
        # Initialize all services
        self._initialize_services()
        
        # Setup UI components
        self._setup_navigation()
        self._setup_views()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Load initial state
        self._load_initial_state()
        
        self.logger.info("PersonalizedReddit application initialized successfully")
    
    def _setup_window(self):
        """Initialize the main application window"""
        self.root = ctk.CTk()
        self.root.title("PersonalizedReddit - AI-Powered Business Automation")
        
        # Set window properties matching mockups
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Set window icon if available
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Set professional dark theme colors
        self.colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d', 
            'bg_tertiary': '#404040',
            'accent_blue': '#4a9eff',
            'accent_orange': '#ff6b47',
            'accent_green': '#4caf50',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#555555'
        }
        
        # Apply theme
        self.root.configure(fg_color=self.colors['bg_primary'])
    
    def _initialize_services(self):
        """Initialize all application services"""
        try:
            self.logger.info("Initializing application services...")
            
            # Initialize data managers first
            self.services['database'] = DatabaseManager()
            self.services['cache'] = CacheManager()
            self.services['config'] = ConfigManager()
            
            # Initialize core Reddit API service
            self.services['reddit_api'] = RedditAPIService(self.config)
            
            # Initialize AI service
            self.services['ai'] = AIService()
            
            # Initialize business logic services
            self.services['newsletter'] = NewsletterService(
                reddit_service=self.services['reddit_api'],
                ai_service=self.services['ai'],
                database=self.services['database']
            )
            
            self.services['live_reddit'] = LiveRedditService(
                reddit_service=self.services['reddit_api'],
                ai_service=self.services['ai'],
                database=self.services['database']
            )
            
            self.services['ai_recommendations'] = AIRecommendationService(
                reddit_service=self.services['reddit_api'],
                ai_service=self.services['ai'],
                database=self.services['database']
            )
            
            self.services['export'] = ExportService(
                database=self.services['database']
            )
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Service initialization failed: {e}", exc_info=True)
            messagebox.showerror("Service Error", f"Failed to initialize services: {e}")
            raise
    
    def _setup_navigation(self):
        """Setup the main navigation component"""
        self.navigation = NavigationFrame(
            parent=self.root,
            app=self,
            colors=self.colors
        )
        self.navigation.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
    
    def _setup_views(self):
        """Initialize all application views"""
        try:
            self.logger.info("Setting up application views...")
            
            # Create main content frame
            self.content_frame = ctk.CTkFrame(self.root, fg_color=self.colors['bg_primary'])
            self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_rowconfigure(0, weight=1)
            
            # Initialize views
            self.views['home'] = HomeView(
                parent=self.content_frame,
                app=self,
                services=self.services,
                colors=self.colors
            )
            
            self.views['live'] = LiveView(
                parent=self.content_frame,
                app=self,
                services=self.services,
                colors=self.colors
            )
            
            self.views['discover'] = DiscoverView(
                parent=self.content_frame,
                app=self,
                services=self.services,
                colors=self.colors
            )
            
            # Show home view by default
            self.navigate_to_view('home')
            
            self.logger.info("All views initialized successfully")
            
        except Exception as e:
            self.logger.error(f"View setup failed: {e}", exc_info=True)
            raise
    
    def _setup_event_handlers(self):
        """Setup application event handlers"""
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-n>', lambda e: self.navigate_to_view('home'))
        self.root.bind('<Control-l>', lambda e: self.navigate_to_view('live'))
        self.root.bind('<Control-d>', lambda e: self.navigate_to_view('discover'))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F5>', lambda e: self.refresh_current_view())
    
    def _load_initial_state(self):
        """Load initial application state and preferences"""
        try:
            # Load user preferences
            preferences = self.services['config'].get_user_preferences()
            
            # Apply theme preference
            if preferences.get('theme'):
                self.set_theme(preferences['theme'])
            
            # Load last view preference
            last_view = preferences.get('last_view', 'home')
            if last_view in self.views:
                self.navigate_to_view(last_view)
            
            self.logger.info("Initial state loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load initial state: {e}")
    
    def navigate_to_view(self, view_name: str):
        """Navigate to a specific view"""
        if view_name not in self.views:
            self.logger.error(f"Unknown view: {view_name}")
            return
        
        try:
            # Hide current view
            if self.current_view:
                self.views[self.current_view].hide()
            
            # Show new view
            self.views[view_name].show()
            self.current_view = view_name
            
            # Update navigation
            self.navigation.set_active_view(view_name)
            
            # Save preference
            self.services['config'].set_user_preference('last_view', view_name)
            
            self.logger.info(f"Navigated to view: {view_name}")
            
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}", exc_info=True)
            messagebox.showerror("Navigation Error", f"Failed to navigate to {view_name}")
    
    def set_theme(self, theme: str):
        """Set application theme"""
        if theme in ['dark', 'light']:
            self.theme_mode = theme
            ctk.set_appearance_mode(theme)
            
            # Update colors based on theme
            if theme == 'light':
                self.colors.update({
                    'bg_primary': '#f0f0f0',
                    'bg_secondary': '#ffffff', 
                    'bg_tertiary': '#e0e0e0',
                    'text_primary': '#000000',
                    'text_secondary': '#666666',
                    'border': '#cccccc'
                })
            else:
                # Dark theme colors (already set)
                pass
            
            # Refresh all views to apply new theme
            for view in self.views.values():
                if hasattr(view, 'apply_theme'):
                    view.apply_theme(self.colors)
            
            self.services['config'].set_user_preference('theme', theme)
            self.logger.info(f"Theme changed to: {theme}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
    
    def refresh_current_view(self):
        """Refresh the current view"""
        if self.current_view and hasattr(self.views[self.current_view], 'refresh'):
            self.views[self.current_view].refresh()
            self.logger.info("Current view refreshed")
    
    def show_status_message(self, message: str, status_type: str = "info", duration: int = 3000):
        """Show a temporary status message"""
        # This could be implemented as a status bar or toast notification
        self.logger.info(f"Status: {message}")
        
        # For now, just log it - could be enhanced with a visual status bar
        if hasattr(self.navigation, 'show_status'):
            self.navigation.show_status(message, status_type, duration)
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service by name"""
        return self.services.get(service_name)
    
    def get_current_view(self) -> Optional[Any]:
        """Get the currently active view"""
        if self.current_view:
            return self.views.get(self.current_view)
        return None
    
    def authenticate_reddit(self, callback: Optional[Callable] = None):
        """Trigger Reddit authentication process"""
        def auth_thread():
            try:
                success = self.services['reddit_api'].authenticate_user()
                if callback:
                    self.root.after(0, lambda: callback(success))
                
                if success:
                    self.show_status_message("Reddit authentication successful!", "success")
                else:
                    self.show_status_message("Reddit authentication failed", "error")
                    
            except Exception as e:
                self.logger.error(f"Authentication error: {e}", exc_info=True)
                if callback:
                    self.root.after(0, lambda: callback(False))
                self.show_status_message(f"Authentication error: {e}", "error")
        
        # Run authentication in background thread
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def export_data(self, data_type: str, data: Any, format: str = "csv"):
        """Export data using the export service"""
        try:
            filename = f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.services['export'].export_data(data, filename, format)
            self.show_status_message(f"Data exported to: {filepath}", "success")
            return filepath
        except Exception as e:
            self.logger.error(f"Export failed: {e}", exc_info=True)
            self.show_status_message(f"Export failed: {e}", "error")
            return None
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_closing:
            return
        
        self.is_closing = True
        
        try:
            self.logger.info("Application closing initiated")
            
            # Save current state
            if self.current_view:
                self.services['config'].set_user_preference('last_view', self.current_view)
            
            # Close services gracefully
            for service_name, service in self.services.items():
                if hasattr(service, 'close'):
                    try:
                        service.close()
                        self.logger.info(f"Service {service_name} closed successfully")
                    except Exception as e:
                        self.logger.error(f"Error closing service {service_name}: {e}")
            
            # Destroy the window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
            # Force exit if normal shutdown fails
            sys.exit(0)
    
    def run(self):
        """Start the main application loop"""
        try:
            self.logger.info("Starting main application loop")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted")
            self.on_closing()
        except Exception as e:
            self.logger.error(f"Application loop error: {e}", exc_info=True)
            raise