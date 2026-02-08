#!/usr/bin/env python3
"""
Reddit Scraper GUI Launcher
Simple launcher script to ensure proper environment setup and launch the main application.
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'customtkinter',
        'requests', 
        'beautifulsoup4',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstalling missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                return False
        
        print("\nAll dependencies installed successfully!")
    
    return True

def setup_directories():
    """Ensure required directories exist."""
    directories = [
        "Exports",
        "Archive"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main launcher function."""
    print("Reddit Subreddit Description Scraper v2.0")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"Python version: {sys.version}")
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("Failed to install required dependencies.")
        return False
    
    # Setup directories
    print("\nSetting up directories...")
    setup_directories()
    
    # Launch main application
    print("\nLaunching Reddit Scraper GUI...")
    try:
        from reddit_scraper_gui import main as run_scraper
        run_scraper()
    except ImportError as e:
        print(f"Error importing main application: {e}")
        return False
    except Exception as e:
        print(f"Error running application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)