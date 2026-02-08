"""
Navigation component for PersonalizedReddit application
Tab-based navigation matching the professional mockup design
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Callable, Optional
from utils.logging_config import get_logger

class NavigationFrame(ctk.CTkFrame):
    """Professional navigation frame with tab-based navigation"""
    
    def __init__(self, parent, app, colors: Dict[str, str]):
        super().__init__(parent, fg_color=colors['bg_secondary'], corner_radius=10)
        
        self.app = app
        self.colors = colors
        self.logger = get_logger(__name__)
        
        self.active_view = None
        self.tab_buttons = {}
        
        self._setup_navigation()
        
    def _setup_navigation(self):
        """Setup the navigation layout"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Center space
        
        # Left side - Navigation tabs
        self.tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tabs_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # Create navigation tabs
        self.tab_configs = [
            {"name": "home", "text": "Home", "description": "Newsletter Overview"},
            {"name": "live", "text": "Live", "description": "Enhanced Reddit"},
            {"name": "discover", "text": "Discover", "description": "AI Recommendations"}
        ]
        
        for i, tab_config in enumerate(self.tab_configs):
            self._create_tab_button(tab_config, i)
        
        # Center - App title and subtitle
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.grid(row=0, column=1, sticky="ew", pady=15)
        
        self.app_title = ctk.CTkLabel(
            self.title_frame,
            text="PersonalizedReddit",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.app_title.pack()
        
        # Right side - User info and settings
        self.user_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.user_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        
        # User avatar (placeholder)
        self.user_avatar = ctk.CTkLabel(
            self.user_frame,
            text="DL",
            width=40,
            height=40,
            fg_color=self.colors['accent_blue'],
            corner_radius=20,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.user_avatar.grid(row=0, column=0, padx=(0, 10))
        
        # User info
        self.user_info_frame = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        self.user_info_frame.grid(row=0, column=1, sticky="w")
        
        self.user_name = ctk.CTkLabel(
            self.user_info_frame,
            text="Drew Ruller",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.user_name.pack(anchor="w")
        
        # Settings button
        self.settings_button = ctk.CTkButton(
            self.user_frame,
            text="⚙",
            width=30,
            height=30,
            font=ctk.CTkFont(size=16),
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['accent_blue'],
            command=self._show_settings
        )
        self.settings_button.grid(row=0, column=2, padx=(10, 0))
    
    def _create_tab_button(self, config: Dict, index: int):
        """Create a navigation tab button"""
        button = ctk.CTkButton(
            self.tabs_frame,
            text=config['text'],
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['accent_blue'],
            command=lambda: self._on_tab_click(config['name'])
        )
        button.grid(row=0, column=index, padx=(0, 10))
        
        self.tab_buttons[config['name']] = button
    
    def _on_tab_click(self, view_name: str):
        """Handle tab button click"""
        self.app.navigate_to_view(view_name)
    
    def set_active_view(self, view_name: str):
        """Set the active view and update button states"""
        self.active_view = view_name
        
        # Update button appearances
        for name, button in self.tab_buttons.items():
            if name == view_name:
                button.configure(fg_color=self.colors['accent_blue'])
            else:
                button.configure(fg_color=self.colors['bg_tertiary'])
    
    def _show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self, self.app, self.colors)
    
    def show_status(self, message: str, status_type: str = "info", duration: int = 3000):
        """Show temporary status message"""
        # This could be implemented as a sliding notification
        # For now, just update the user info temporarily
        original_text = self.user_name.cget("text")
        
        color_map = {
            "info": self.colors['text_secondary'],
            "success": self.colors['accent_green'],
            "error": self.colors['accent_orange'],
            "warning": "#FFA726"
        }
        
        self.user_name.configure(text=message, text_color=color_map.get(status_type, self.colors['text_secondary']))
        
        # Restore original text after duration
        self.after(duration, lambda: self.user_name.configure(text=original_text, text_color=self.colors['text_primary']))

class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog window"""
    
    def __init__(self, parent, app, colors: Dict[str, str]):
        super().__init__(parent)
        
        self.app = app
        self.colors = colors
        
        # Window configuration
        self.title("PersonalizedReddit Settings")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        self.configure(fg_color=colors['bg_primary'])
        
        self._setup_settings_ui()
    
    def _setup_settings_ui(self):
        """Setup the settings dialog UI"""
        # Main container with scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=self.colors['bg_secondary'],
            corner_radius=10
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Settings sections
        self._create_appearance_section()
        self._create_reddit_section()
        self._create_ai_section()
        self._create_export_section()
        
        # Action buttons
        self._create_action_buttons()
    
    def _create_appearance_section(self):
        """Create appearance settings section"""
        section_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            section_frame,
            text="Appearance",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Theme selection
        theme_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_primary']
        )
        theme_label.pack(side="left")
        
        self.theme_var = tk.StringVar(value=self.app.theme_mode)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._on_theme_change
        )
        theme_menu.pack(side="right")
    
    def _create_reddit_section(self):
        """Create Reddit settings section"""
        section_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            section_frame,
            text="Reddit Integration",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Authentication status
        auth_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        auth_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        auth_label = ctk.CTkLabel(
            auth_frame,
            text="Authentication:",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_primary']
        )
        auth_label.pack(side="left")
        
        auth_button = ctk.CTkButton(
            auth_frame,
            text="Connect Reddit Account",
            fg_color=self.colors['accent_blue'],
            command=self._connect_reddit
        )
        auth_button.pack(side="right")
    
    def _create_ai_section(self):
        """Create AI settings section"""
        section_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            section_frame,
            text="AI Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # AI model settings
        model_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        model_label = ctk.CTkLabel(
            model_frame,
            text="Analysis Model:",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_primary']
        )
        model_label.pack(side="left")
        
        self.model_var = tk.StringVar(value="facebook/bart-large-cnn")
        model_menu = ctk.CTkOptionMenu(
            model_frame,
            values=["facebook/bart-large-cnn", "google/pegasus-xsum", "microsoft/DialoGPT-medium"],
            variable=self.model_var
        )
        model_menu.pack(side="right")
    
    def _create_export_section(self):
        """Create export settings section"""
        section_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['bg_tertiary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            section_frame,
            text="Export Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Default export format
        format_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Default Format:",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_primary']
        )
        format_label.pack(side="left")
        
        self.format_var = tk.StringVar(value="csv")
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=["csv", "markdown", "json", "excel"],
            variable=self.format_var
        )
        format_menu.pack(side="right")
    
    def _create_action_buttons(self):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['accent_orange'],
            command=self.destroy
        )
        cancel_button.pack(side="right", padx=(10, 0))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            fg_color=self.colors['accent_blue'],
            command=self._save_settings
        )
        save_button.pack(side="right")
    
    def _on_theme_change(self, theme: str):
        """Handle theme change"""
        self.app.set_theme(theme)
    
    def _connect_reddit(self):
        """Handle Reddit connection"""
        self.app.authenticate_reddit()
    
    def _save_settings(self):
        """Save all settings"""
        try:
            config_service = self.app.get_service('config')
            
            # Save preferences
            preferences = {
                'theme': self.theme_var.get(),
                'ai_model': self.model_var.get(),
                'default_export_format': self.format_var.get()
            }
            
            for key, value in preferences.items():
                config_service.set_user_preference(key, value)
            
            # Show success message
            self.app.show_status_message("Settings saved successfully!", "success")
            
            self.destroy()
            
        except Exception as e:
            self.app.show_status_message(f"Failed to save settings: {e}", "error")