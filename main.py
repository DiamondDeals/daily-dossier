#!/usr/bin/env python3
"""
PersonalizedReddit - Main Application Entry Point
Professional Reddit automation lead discovery tool with AI-powered analysis
"""

import sys
import os
import logging
import traceback
from pathlib import Path
import customtkinter as ctk
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import application components
try:
    from app.application import PersonalizedRedditApp
    from utils.logging_config import setup_logging
    from config.reddit_config import get_config
    from data.database_manager import DatabaseManager
except ImportError as e:
    print(f"Critical import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def setup_application_environment():
    """Set up the application environment and configuration"""
    # Set CustomTkinter appearance
    ctk.set_appearance_mode("dark")  # Dark theme as specified
    ctk.set_default_color_theme("blue")
    
    # Create necessary directories
    directories = [
        "Exports",
        "logs",
        "data",
        "cache",
        "assets"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Setup logging
    setup_logging()
    
    # Initialize database
    try:
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"Unhandled exception: {error_msg}")
    
    # Show error dialog to user if GUI is available
    try:
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "Critical Error", 
            f"A critical error occurred:\n{exc_type.__name__}: {exc_value}\n\nCheck logs for details."
        )
    except:
        pass

def main():
    """Main application entry point"""
    try:
        print("=" * 60)
        print("PersonalizedReddit - AI-Powered Reddit Business Automation")
        print("=" * 60)
        print(f"Starting application at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Set up exception handling
        sys.excepthook = handle_exception
        
        # Set up application environment
        setup_application_environment()
        
        # Load configuration
        config = get_config()
        logging.info("Configuration loaded successfully")
        
        # Create and run the main application
        app = PersonalizedRedditApp(config)
        
        print("Application initialized successfully")
        print("Starting GUI...")
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        logging.info("Application interrupted by user")
        
    except Exception as e:
        error_msg = f"Failed to start application: {e}"
        print(f"ERROR: {error_msg}")
        logging.critical(error_msg, exc_info=True)
        
        # Show error dialog
        try:
            import tkinter.messagebox as messagebox
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Startup Error", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)
    
    finally:
        print("Application shutdown complete")
        logging.info("Application shutdown complete")

if __name__ == "__main__":
    main()