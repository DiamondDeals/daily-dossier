"""
Base View class for PersonalizedReddit UI views
Provides common functionality and structure for all views
"""

import customtkinter as ctk
import threading
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod

from utils.logging_config import get_logger

class BaseView(ctk.CTkFrame, ABC):
    """
    Abstract base class for all application views
    Provides common functionality and interface
    """
    
    def __init__(self, parent, app, services: Dict[str, Any], colors: Dict[str, str]):
        super().__init__(parent, fg_color=colors['bg_primary'])
        
        self.app = app
        self.services = services
        self.colors = colors
        self.logger = get_logger(self.__class__.__name__)
        
        # View state
        self.is_visible = False
        self.is_initialized = False
        self.refresh_interval = None
        self.auto_refresh_job = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize the view
        self._initialize_view()
        
    @abstractmethod
    def _initialize_view(self):
        """Initialize the view components - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def refresh_data(self):
        """Refresh view data - must be implemented by subclasses"""
        pass
    
    def show(self):
        """Show the view"""
        if not self.is_visible:
            self.grid(row=0, column=0, sticky="nsew")
            self.is_visible = True
            
            # Start auto-refresh if configured
            if self.refresh_interval:
                self._start_auto_refresh()
            
            self.logger.debug(f"{self.__class__.__name__} view shown")
    
    def hide(self):
        """Hide the view"""
        if self.is_visible:
            self.grid_remove()
            self.is_visible = False
            
            # Stop auto-refresh
            self._stop_auto_refresh()
            
            self.logger.debug(f"{self.__class__.__name__} view hidden")
    
    def refresh(self):
        """Refresh the view"""
        try:
            self.refresh_data()
            self.logger.debug(f"{self.__class__.__name__} view refreshed")
        except Exception as e:
            self.logger.error(f"View refresh failed: {e}", exc_info=True)
            self._show_error_message(f"Failed to refresh view: {e}")
    
    def apply_theme(self, colors: Dict[str, str]):
        """Apply theme colors to the view"""
        self.colors = colors
        self.configure(fg_color=colors['bg_primary'])
        
        # Subclasses should override to apply theme to their components
        if hasattr(self, '_apply_theme_to_components'):
            self._apply_theme_to_components()
    
    def set_auto_refresh(self, interval_seconds: int):
        """Set auto-refresh interval"""
        self.refresh_interval = interval_seconds
        if self.is_visible:
            self._start_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        if self.refresh_interval and not self.auto_refresh_job:
            self.auto_refresh_job = self.after(
                self.refresh_interval * 1000, 
                self._auto_refresh_callback
            )
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self.auto_refresh_job:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None
    
    def _auto_refresh_callback(self):
        """Auto-refresh callback"""
        try:
            self.refresh_data()
        except Exception as e:
            self.logger.error(f"Auto-refresh failed: {e}")
        
        # Schedule next refresh
        if self.is_visible and self.refresh_interval:
            self.auto_refresh_job = self.after(
                self.refresh_interval * 1000,
                self._auto_refresh_callback
            )
    
    def _show_loading(self, message: str = "Loading..."):
        """Show loading indicator"""
        # Subclasses can implement custom loading indicators
        pass
    
    def _hide_loading(self):
        """Hide loading indicator"""
        # Subclasses can implement custom loading indicators
        pass
    
    def _show_error_message(self, message: str):
        """Show error message to user"""
        # This could be enhanced with custom error dialogs
        self.app.show_status_message(message, "error")
    
    def _show_success_message(self, message: str):
        """Show success message to user"""
        self.app.show_status_message(message, "success")
    
    def _run_in_background(self, func: Callable, callback: Optional[Callable] = None):
        """Run function in background thread"""
        def background_task():
            try:
                result = func()
                if callback:
                    self.after(0, lambda: callback(result))
            except Exception as e:
                self.logger.error(f"Background task failed: {e}")
                self.after(0, lambda: self._show_error_message(str(e)))
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service by name"""
        return self.services.get(service_name)
    
    def export_data(self, data: Any, filename: str, format: str = "csv"):
        """Export data using the export service"""
        try:
            export_service = self.get_service('export')
            if export_service:
                filepath = export_service.export_data(data, filename, format)
                self._show_success_message(f"Data exported to: {filepath.name}")
                return filepath
            else:
                raise Exception("Export service not available")
        except Exception as e:
            self._show_error_message(f"Export failed: {e}")
            return None
    
    def cleanup(self):
        """Cleanup view resources"""
        self._stop_auto_refresh()
        self.logger.debug(f"{self.__class__.__name__} view cleaned up")