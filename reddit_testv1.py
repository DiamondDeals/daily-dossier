import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import json
import csv
import re
import threading
import time
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse, quote
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import markdown
import html2text

class RedditHelperHelper:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Reddit Helper Helper")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Theme settings
        self.dark_mode = True
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Data storage
        self.keywords = []
        self.search_results = []
        self.current_view = "table"  # table, list, card
        self.is_searching = False
        
        # Debug window reference
        self.debug_window = None
        self.debug_text = None
        
        # Create directories
        self.create_directories()
        
        # Load keywords
        self.load_keywords()
        
        # Setup GUI
        self.setup_gui()
        
        # Variables for search control
        self.search_thread = None
        self.stop_search = False
        
        # Log initial status
        self.debug_log("=== Reddit Helper Helper Started ===")
        self.debug_log(f"Program folder: {self.program_folder}")
        self.debug_log(f"Keywords loaded: {len(self.keywords)}")
        
    def debug_log(self, message):
        """Add message to debug log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)  # Also print to console
        
        # If debug window exists, update it
        if self.debug_text:
            try:
                self.debug_text.insert(tk.END, log_message + "\n")
                self.debug_text.see(tk.END)
            except:
                pass
                
    def show_debug_window(self):
        """Show or create the debug console window"""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            self.debug_window = ctk.CTkToplevel(self.root)
            self.debug_window.title("Debug Console")
            self.debug_window.geometry("800x600")
            self.debug_window.transient(self.root)
            
            # Debug text area
            self.debug_text = tk.Text(self.debug_window, bg="#1a1a1a", fg="#00ff00", 
                                     font=("Consolas", 10), wrap=tk.WORD)
            debug_scrollbar = ttk.Scrollbar(self.debug_window, orient="vertical", command=self.debug_text.yview)
            self.debug_text.configure(yscrollcommand=debug_scrollbar.set)
            
            self.debug_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            debug_scrollbar.pack(side="right", fill="y", pady=5)
            
            # Control buttons frame
            button_frame = ctk.CTkFrame(self.debug_window)
            button_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkButton(button_frame, text="Clear Log", command=self.clear_debug_log).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Test Connection", command=self.test_reddit_connection).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Show Keywords", command=self.show_loaded_keywords).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Test Search", command=self.test_search_simple).pack(side="left", padx=5)
            
            # Add existing log messages
            self.debug_text.insert("1.0", "=== Debug Console Opened ===\n")
            
        else:
            self.debug_window.lift()
            self.debug_window.focus()
            
    def clear_debug_log(self):
        """Clear the debug log"""
        if self.debug_text:
            self.debug_text.delete("1.0", tk.END)
            
    def test_reddit_connection(self):
        """Test basic connection to Reddit"""
        self.debug_log("=== Testing Reddit Connection ===")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get("https://www.reddit.com", headers=headers, timeout=10)
            self.debug_log(f"Status Code: {response.status_code}")
            self.debug_log(f"Response headers: {dict(response.headers)}")
            self.debug_log(f"Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                self.debug_log("✓ Successfully connected to Reddit")
                
                # Check if we can access a specific subreddit
                test_url = "https://www.reddit.com/r/python/hot.json?limit=5"
                api_response = requests.get(test_url, headers=headers, timeout=10)
                self.debug_log(f"API test status: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    self.debug_log("✓ Reddit JSON API accessible")
                else:
                    self.debug_log("✗ Reddit JSON API not accessible, will use HTML scraping")
                    
            else:
                self.debug_log(f"✗ Failed to connect to Reddit: {response.status_code}")
                
        except Exception as e:
            self.debug_log(f"✗ Connection error: {str(e)}")
            
    def show_loaded_keywords(self):
        """Show the currently loaded keywords"""
        self.debug_log("=== Loaded Keywords ===")
        self.debug_log(f"Total keywords: {len(self.keywords)}")
        
        keywords_file = os.path.join(self.program_folder, "keywords.json")
        self.debug_log(f"Keywords file path: {keywords_file}")
        self.debug_log(f"Keywords file exists: {os.path.exists(keywords_file)}")
        
        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r') as f:
                    file_keywords = json.load(f)
                self.debug_log(f"Keywords in file: {len(file_keywords)}")
                
                # Show first 10 keywords
                self.debug_log("First 10 keywords:")
                for i, keyword in enumerate(self.keywords[:10]):
                    self.debug_log(f"  {i+1}. {keyword}")
                    
                if len(self.keywords) > 10:
                    self.debug_log(f"  ... and {len(self.keywords) - 10} more")
                    
            except Exception as e:
                self.debug_log(f"Error reading keywords file: {str(e)}")
        else:
            self.debug_log("Keywords file not found - using defaults")
            
    def test_search_simple(self):
        """Test a simple search to see what happens"""
        self.debug_log("=== Testing Simple Search ===")
        try:
            # Test search for "python"
            test_keywords = ["python", "programming"]
            self.debug_log(f"Testing with keywords: {test_keywords}")
            
            # Try Reddit's search API first
            self.test_reddit_search_api(test_keywords)
            
            # Try HTML scraping
            self.test_reddit_html_scraping(test_keywords)
            
        except Exception as e:
            self.debug_log(f"Test search error: {str(e)}")
            
    def test_reddit_search_api(self, keywords):
        """Test Reddit's search API"""
        self.debug_log("--- Testing Reddit Search API ---")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            search_query = " OR ".join(keywords[:3])  # Use first 3 keywords
            search_url = f"https://www.reddit.com/search.json?q={quote(search_query)}&sort=new&limit=10"
            
            self.debug_log(f"Search URL: {search_url}")
            
            response = requests.get(search_url, headers=headers, timeout=15)
            self.debug_log(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    posts = data['data']['children']
                    self.debug_log(f"Found {len(posts)} posts via API")
                    
                    for i, post in enumerate(posts[:3]):
                        post_data = post['data']
                        title = post_data.get('title', 'No title')
                        subreddit = post_data.get('subreddit', 'Unknown')
                        self.debug_log(f"  Post {i+1}: r/{subreddit} - {title[:100]}")
                        
                except json.JSONDecodeError as e:
                    self.debug_log(f"Failed to parse API response: {str(e)}")
                    self.debug_log(f"Response content preview: {response.text[:500]}")
                    
            else:
                self.debug_log(f"API request failed: {response.status_code}")
                self.debug_log(f"Response: {response.text[:500]}")
                
        except Exception as e:
            self.debug_log(f"API test error: {str(e)}")
            
    def test_reddit_html_scraping(self, keywords):
        """Test HTML scraping"""
        self.debug_log("--- Testing HTML Scraping ---")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Test with r/programming
            test_url = "https://www.reddit.com/r/programming/hot/"
            self.debug_log(f"Testing HTML scraping: {test_url}")
            
            response = requests.get(test_url, headers=headers, timeout=15)
            self.debug_log(f"HTML Response status: {response.status_code}")
            self.debug_log(f"Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for various post selectors
                selectors = [
                    'div[data-testid="post-container"]',
                    'article',
                    'div.Post',
                    'div[class*="thing"]',
                    'h3',
                    'a[data-click-id="body"]'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    self.debug_log(f"Selector '{selector}': found {len(elements)} elements")
                    
                    if elements:
                        for i, elem in enumerate(elements[:3]):
                            text = elem.get_text(strip=True)[:100]
                            self.debug_log(f"  Element {i+1}: {text}")
                            
                # Look for titles specifically
                titles = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(r'.+'))
                self.debug_log(f"Found {len(titles)} title elements")
                
                for i, title in enumerate(titles[:5]):
                    self.debug_log(f"  Title {i+1}: {title.get_text(strip=True)[:100]}")
                    
            else:
                self.debug_log(f"HTML scraping failed: {response.status_code}")
                
        except Exception as e:
            self.debug_log(f"HTML scraping error: {str(e)}")
        
    def create_directories(self):
        """Create necessary directories"""
        self.documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        self.program_folder = os.path.join(self.documents_path, "Reddit Helper Helper")
        self.exports_folder = os.path.join(self.program_folder, "Exports")
        
        os.makedirs(self.program_folder, exist_ok=True)
        os.makedirs(self.exports_folder, exist_ok=True)
        
    def load_keywords(self):
        """Load keywords from JSON file or create from default list"""
        keywords_file = os.path.join(self.program_folder, "keywords.json")
        self.debug_log(f"Loading keywords from: {keywords_file}")
        
        default_keywords = [
            "manual data entry", "copy and paste", "one by one", "individually processing",
            "manually updating", "doing this manually", "repetitive workflow", "same process over and over",
            "tedious task", "manual process", "time-consuming", "repetitive task", "doing this by hand",
            "takes hours to", "streamline", "workflow", "eating up my time", "consuming hours",
            "spending all day", "full-time job just to", "can't scale", "bottleneck", "slowing us down",
            "wasting so much time", "can't keep up", "organize files", "sort through",
            "file management nightmare", "data scattered", "inconsistent formats", "duplicate entries",
            "merge data", "clean up data", "keep track of", "monitor changes", "get notifications when",
            "alert me if", "check regularly", "status updates", "progress tracking", "losing track",
            "transfer data between", "export from X import to Y", "systems don't talk", "manual sync",
            "update multiple places", "cross-platform", "between systems", "different platforms",
            "migration", "consolidate", "synchronize", "notify team when", "distribute updates",
            "collect responses", "coordinate schedules", "manage requests", "inventory tracking",
            "customer follow-up", "order processing", "appointment scheduling", "invoice generation",
            "report compilation", "lead management", "project status", "manage inventory",
            "track customers", "reporting", "analytics", "wish there was a way",
            "there has to be a better way", "driving me crazy", "hundreds of", "thousands of",
            "bulk", "mass", "optimize", "integration"
        ]
        
        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r') as f:
                    self.keywords = json.load(f)
                self.debug_log(f"✓ Loaded {len(self.keywords)} keywords from JSON file")
                
                # Verify keywords loaded correctly
                if len(self.keywords) > 0:
                    self.debug_log(f"First keyword: '{self.keywords[0]}'")
                    self.debug_log(f"Last keyword: '{self.keywords[-1]}'")
                else:
                    self.debug_log("Warning: No keywords found in JSON file")
                    
            except Exception as e:
                self.debug_log(f"Error loading keywords from JSON: {str(e)}")
                self.keywords = default_keywords
                self.save_keywords()
                self.debug_log("Using default keywords instead")
        else:
            self.debug_log("Keywords file not found, creating with defaults")
            self.keywords = default_keywords
            self.save_keywords()
            
    def save_keywords(self):
        """Save keywords to JSON file"""
        keywords_file = os.path.join(self.program_folder, "keywords.json")
        try:
            with open(keywords_file, 'w') as f:
                json.dump(self.keywords, f, indent=2)
            self.debug_log(f"✓ Saved {len(self.keywords)} keywords to {keywords_file}")
        except Exception as e:
            self.debug_log(f"Error saving keywords: {str(e)}")
            
    def setup_gui(self):
        """Setup the main GUI"""
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        self.menu_frame = ctk.CTkFrame(self.root, height=40)
        self.menu_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.menu_frame.grid_columnconfigure(7, weight=1)
        
        # Menu buttons
        ctk.CTkButton(self.menu_frame, text="File", width=60, command=self.file_menu).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Search", width=60, command=self.search_menu).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Export", width=60, command=self.export_menu).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Keywords", width=80, command=self.keywords_menu).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Debug", width=60, command=self.show_debug_window).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Help", width=60, command=self.help_menu).grid(row=0, column=5, padx=5, pady=5)
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(self.menu_frame, text="🌙 Dark", width=80, command=self.toggle_theme)
        self.theme_button.grid(row=0, column=6, padx=5, pady=5)
        
    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar_frame = ctk.CTkFrame(self.root, height=60)
        self.toolbar_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 5))
        self.toolbar_frame.grid_columnconfigure(4, weight=1)
        
        # Search controls
        ctk.CTkLabel(self.toolbar_frame, text="Search Terms:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ctk.CTkEntry(self.toolbar_frame, width=200, placeholder_text="Enter additional keywords...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(self.toolbar_frame, text="Subreddit (optional):").grid(row=0, column=2, padx=5, pady=5)
        self.subreddit_entry = ctk.CTkEntry(self.toolbar_frame, width=150, placeholder_text="e.g., python, programming")
        self.subreddit_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Search button
        self.search_button = ctk.CTkButton(self.toolbar_frame, text="🔍 Search Reddit", command=self.start_search)
        self.search_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Stop button
        self.stop_button = ctk.CTkButton(self.toolbar_frame, text="⏹ Stop", command=self.stop_search_func, state="disabled")
        self.stop_button.grid(row=0, column=6, padx=5, pady=5)
        
        # Clear button
        ctk.CTkButton(self.toolbar_frame, text="🗑 Clear Results", command=self.clear_results).grid(row=0, column=7, padx=5, pady=5)
        
    def create_main_content(self):
        """Create the main content area"""
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=(0, 5))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # View toggle buttons
        self.view_frame = ctk.CTkFrame(self.main_frame, height=40)
        self.view_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.table_button = ctk.CTkButton(self.view_frame, text="📊 Table View", command=lambda: self.switch_view("table"))
        self.table_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.list_button = ctk.CTkButton(self.view_frame, text="📋 List View", command=lambda: self.switch_view("list"))
        self.list_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.card_button = ctk.CTkButton(self.view_frame, text="🃏 Card View", command=lambda: self.switch_view("card"))
        self.card_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Results display area
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Create different view containers
        self.create_table_view()
        self.create_list_view()
        self.create_card_view()
        
        # Show table view by default
        self.switch_view("table")
        
    def create_table_view(self):
        """Create the table view"""
        self.table_frame = ctk.CTkFrame(self.results_frame)
        
        # Create treeview for table
        self.tree = ttk.Treeview(self.table_frame, columns=("Score", "Subreddit", "Title", "Author", "Upvotes", "Comments"), show="headings")
        
        # Define column headings
        self.tree.heading("Score", text="Score")
        self.tree.heading("Subreddit", text="Subreddit")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Upvotes", text="Upvotes")
        self.tree.heading("Comments", text="Comments")
        
        # Configure column widths
        self.tree.column("Score", width=60)
        self.tree.column("Subreddit", width=100)
        self.tree.column("Title", width=400)
        self.tree.column("Author", width=100)
        self.tree.column("Upvotes", width=80)
        self.tree.column("Comments", width=80)
        
        # Add scrollbars
        table_v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        table_h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=table_v_scrollbar.set, xscrollcommand=table_h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        table_v_scrollbar.grid(row=0, column=1, sticky="ns")
        table_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
    def create_list_view(self):
        """Create the list view"""
        self.list_frame = ctk.CTkFrame(self.results_frame)
        
        # Create scrollable text widget
        self.list_text = tk.Text(self.list_frame, wrap=tk.WORD, bg="#2b2b2b", fg="white", font=("Arial", 10))
        list_scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.list_text.yview)
        self.list_text.configure(yscrollcommand=list_scrollbar.set)
        
        self.list_text.grid(row=0, column=0, sticky="nsew")
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
    def create_card_view(self):
        """Create the card view"""
        self.card_frame = ctk.CTkFrame(self.results_frame)
        
        # Create scrollable frame
        self.card_scroll = ctk.CTkScrollableFrame(self.card_frame, width=600, height=400)
        self.card_scroll.grid(row=0, column=0, sticky="nsew")
        
        self.card_frame.grid_rowconfigure(0, weight=1)
        self.card_frame.grid_columnconfigure(0, weight=1)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_frame = ctk.CTkFrame(self.root, height=40)
        self.status_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready to search Reddit...")
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.grid(row=0, column=1, padx=5, pady=5)
        self.progress_bar.set(0)
        
        # Results count
        self.results_count_label = ctk.CTkLabel(self.status_frame, text="Results: 0")
        self.results_count_label.grid(row=0, column=2, padx=5, pady=5)
        
    def switch_view(self, view_type):
        """Switch between different view types"""
        # Hide all views
        self.table_frame.grid_remove()
        self.list_frame.grid_remove()
        self.card_frame.grid_remove()
        
        # Show selected view
        if view_type == "table":
            self.table_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = "table"
        elif view_type == "list":
            self.list_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = "list"
        elif view_type == "card":
            self.card_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = "card"
            
        # Update view with current results
        self.update_display()
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.dark_mode:
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="☀️ Light")
            self.dark_mode = False
        else:
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙 Dark")
            self.dark_mode = True
            
    def start_search(self):
        """Start the Reddit search in a separate thread"""
        if not self.is_searching:
            self.is_searching = True
            self.stop_search = False
            self.search_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # Clear previous results
            self.search_results = []
            self.update_display()
            
            self.debug_log("=== Starting New Search ===")
            
            # Start search thread
            self.search_thread = threading.Thread(target=self.search_reddit)
            self.search_thread.daemon = True
            self.search_thread.start()
            
    def stop_search_func(self):
        """Stop the current search"""
        self.stop_search = True
        self.debug_log("Search stop requested by user")
        self.status_label.configure(text="Stopping search...")
        
    def search_reddit(self):
        """Main search function"""
        try:
            # Get search parameters
            additional_keywords = self.search_entry.get().strip()
            subreddit_filter = self.subreddit_entry.get().strip()
            
            self.debug_log(f"Additional keywords: '{additional_keywords}'")
            self.debug_log(f"Subreddit filter: '{subreddit_filter}'")
            
            # Combine keywords
            search_keywords = self.keywords.copy()
            if additional_keywords:
                new_keywords = [k.strip() for k in additional_keywords.split(',')]
                search_keywords.extend(new_keywords)
                self.debug_log(f"Added {len(new_keywords)} additional keywords")
            
            self.debug_log(f"Total keywords to search: {len(search_keywords)}")
            
            # Try API search first
            self.debug_log("Attempting Reddit API search...")
            api_posts = self.search_reddit_api(search_keywords, subreddit_filter)
            
            if api_posts:
                self.debug_log(f"API search found {len(api_posts)} posts")
                for post in api_posts:
                    if self.stop_search:
                        break
                    score = self.calculate_post_score(post, search_keywords)
                    if score > 0:
                        post['score'] = score
                        self.search_results.append(post)
                        self.root.after(0, self.update_display)
            else:
                self.debug_log("API search failed, trying HTML scraping...")
                
                # Fallback to HTML scraping
                sort_methods = ['new', 'hot', 'rising', 'top']
                total_posts_found = 0
                
                for sort_method in sort_methods:
                    if self.stop_search:
                        break
                        
                    self.debug_log(f"Scraping {sort_method} posts...")
                    self.update_status(f"Searching {sort_method} posts...")
                    
                    posts = self.scrape_reddit_html(search_keywords, subreddit_filter, sort_method)
                    
                    for post in posts:
                        if self.stop_search:
                            break
                            
                        score = self.calculate_post_score(post, search_keywords)
                        if score > 0:
                            post['score'] = score
                            self.search_results.append(post)
                            total_posts_found += 1
                            
                            # Update display every 5 posts
                            if total_posts_found % 5 == 0:
                                self.root.after(0, self.update_display)
                                
                    # Update progress
                    progress = (sort_methods.index(sort_method) + 1) / len(sort_methods)
                    self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                    
            # Sort results by score
            self.search_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Update final display
            self.root.after(0, self.update_display)
            final_count = len(self.search_results)
            self.debug_log(f"Search complete! Found {final_count} relevant posts.")
            self.root.after(0, lambda: self.update_status(f"Search complete! Found {final_count} relevant posts."))
            
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            self.debug_log(error_msg)
            self.root.after(0, lambda: self.update_status(error_msg))
            
        finally:
            self.is_searching = False
            self.root.after(0, lambda: self.search_button.configure(state="normal"))
            self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
            self.root.after(0, lambda: self.progress_bar.set(0))
            
    def search_reddit_api(self, keywords, subreddit_filter):
        """Search Reddit using JSON API"""
        posts = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Build search query - use top keywords only to avoid too long URLs
            search_terms = keywords[:10]  # Use first 10 keywords
            search_query = " OR ".join([f'"{term}"' for term in search_terms])
            
            if subreddit_filter:
                search_url = f"https://www.reddit.com/r/{subreddit_filter}/search.json?q={quote(search_query)}&sort=new&restrict_sr=1&limit=50"
            else:
                search_url = f"https://www.reddit.com/search.json?q={quote(search_query)}&sort=new&limit=50"
                
            self.debug_log(f"API URL: {search_url[:100]}...")
            
            response = requests.get(search_url, headers=headers, timeout=15)
            self.debug_log(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    reddit_posts = data['data']['children']
                    self.debug_log(f"API returned {len(reddit_posts)} posts")
                    
                    for post_data in reddit_posts:
                        if self.stop_search:
                            break
                            
                        post = post_data['data']
                        
                        # Extract post information
                        post_info = {
                            'title': post.get('title', ''),
                            'content': post.get('selftext', ''),
                            'author': post.get('author', ''),
                            'subreddit': post.get('subreddit', ''),
                            'upvotes': post.get('ups', 0),
                            'comments': post.get('num_comments', 0),
                            'url': f"https://www.reddit.com{post.get('permalink', '')}",
                            'score': 0
                        }
                        
                        # Only add posts with content
                        if post_info['title']:
                            posts.append(post_info)
                            self.debug_log(f"Added post: {post_info['title'][:50]}...")
                            
                except json.JSONDecodeError as e:
                    self.debug_log(f"Failed to parse API response: {str(e)}")
                    return []
                    
            else:
                self.debug_log(f"API request failed: {response.status_code}")
                if response.status_code == 429:
                    self.debug_log("Rate limited by Reddit API")
                return []
                
        except Exception as e:
            self.debug_log(f"API search error: {str(e)}")
            return []
            
        return posts
            
    def scrape_reddit_html(self, keywords, subreddit_filter, sort_method):
        """Scrape Reddit posts using HTML parsing"""
        posts = []
        
        try:
            # Build URL
            if subreddit_filter:
                base_url = f"https://www.reddit.com/r/{subreddit_filter}/{sort_method}/"
            else:
                base_url = f"https://www.reddit.com/{sort_method}/"
                
            self.debug_log(f"HTML scraping URL: {base_url}")
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(base_url, headers=headers, timeout=15)
            self.debug_log(f"HTML response status: {response.status_code}")
            self.debug_log(f"Content length: {len(response.content)} bytes")
            
            if response.status_code != 200:
                self.debug_log(f"Failed to fetch page: {response.status_code}")
                return posts
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for finding posts
            post_selectors = [
                'div[data-testid="post-container"]',
                'article',
                'div.Post',
                'div[class*="thing"]',
                'div[data-type="link"]',
                'shreddit-post'
            ]
            
            post_elements = []
            for selector in post_selectors:
                elements = soup.select(selector)
                self.debug_log(f"Selector '{selector}': found {len(elements)} elements")
                if elements:
                    post_elements = elements
                    break
                    
            if not post_elements:
                # Fallback: look for any divs with post-like content
                all_divs = soup.find_all('div')
                self.debug_log(f"Total divs found: {len(all_divs)}")
                
                # Look for divs containing links to reddit posts
                for div in all_divs[:100]:  # Check first 100 divs
                    links = div.find_all('a', href=re.compile(r'/r/.*/comments/'))
                    if links:
                        post_elements.append(div)
                        
                self.debug_log(f"Fallback method found {len(post_elements)} potential posts")
            
            # Extract data from found elements
            for i, post_elem in enumerate(post_elements[:50]):  # Limit to 50 posts
                if self.stop_search:
                    break
                    
                try:
                    post_data = self.extract_post_data_improved(post_elem)
                    if post_data and post_data['title']:
                        posts.append(post_data)
                        self.debug_log(f"Extracted post {i+1}: {post_data['title'][:50]}...")
                        
                except Exception as e:
                    self.debug_log(f"Error extracting post {i+1}: {str(e)}")
                    continue
                    
            self.debug_log(f"Successfully extracted {len(posts)} posts from HTML")
                    
        except Exception as e:
            self.debug_log(f"HTML scraping error: {str(e)}")
            
        return posts
        
    def extract_post_data_improved(self, post_elem):
        """Extract post data from HTML element with improved methods"""
        try:
            post_data = {
                'title': '',
                'content': '',
                'author': '',
                'subreddit': '',
                'upvotes': 0,
                'comments': 0,
                'url': '',
                'score': 0
            }
            
            # Extract title - try multiple methods
            title_selectors = [
                'h3',
                'a[data-testid="post-title"]',
                'a[data-click-id="body"]',
                'h2',
                'h1',
                '[class*="title"]',
                'a[href*="/comments/"]'
            ]
            
            for selector in title_selectors:
                title_elem = post_elem.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    if title_text and len(title_text) > 10:  # Valid title
                        post_data['title'] = title_text
                        break
                        
            # Extract content
            content_selectors = [
                'div[data-testid="post-content"]',
                'div[class*="usertext"]',
                'div[class*="content"]',
                'p'
            ]
            
            for selector in content_selectors:
                content_elem = post_elem.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text(strip=True)
                    if content_text and len(content_text) > 20:  # Valid content
                        post_data['content'] = content_text[:1000]  # Limit content length
                        break
                        
            # Extract author
            author_selectors = [
                'a[href*="/user/"]',
                'a[href*="/u/"]',
                '[class*="author"]'
            ]
            
            for selector in author_selectors:
                author_elem = post_elem.select_one(selector)
                if author_elem:
                    author_text = author_elem.get_text(strip=True)
                    if author_text and not author_text.startswith('r/'):
                        post_data['author'] = author_text.replace('u/', '').replace('/u/', '')
                        break
                        
            # Extract subreddit
            subreddit_selectors = [
                'a[href*="/r/"]',
                '[class*="subreddit"]'
            ]
            
            for selector in subreddit_selectors:
                subreddit_elem = post_elem.select_one(selector)
                if subreddit_elem:
                    subreddit_text = subreddit_elem.get_text(strip=True)
                    if subreddit_text and subreddit_text.startswith('r/'):
                        post_data['subreddit'] = subreddit_text.replace('r/', '')
                        break
                        
            # Extract URL
            url_selectors = [
                'a[href*="/comments/"]',
                'a[data-click-id="body"]'
            ]
            
            for selector in url_selectors:
                url_elem = post_elem.select_one(selector)
                if url_elem:
                    href = url_elem.get('href', '')
                    if '/comments/' in href:
                        if href.startswith('/'):
                            post_data['url'] = f"https://www.reddit.com{href}"
                        else:
                            post_data['url'] = href
                        break
                        
            # Extract engagement metrics
            # Look for vote counts
            vote_elements = post_elem.find_all(string=re.compile(r'\d+'))
            numbers = []
            for elem in vote_elements:
                try:
                    num = int(re.search(r'\d+', elem).group())
                    numbers.append(num)
                except:
                    continue
                    
            if numbers:
                # Assume first number might be upvotes, second might be comments
                post_data['upvotes'] = numbers[0] if len(numbers) > 0 else 0
                post_data['comments'] = numbers[1] if len(numbers) > 1 else 0
                
            return post_data if post_data['title'] else None
            
        except Exception as e:
            self.debug_log(f"Error in extract_post_data_improved: {str(e)}")
            return None
            
    def calculate_post_score(self, post, keywords):
        """Calculate relevance score for a post"""
        score = 0
        text_content = f"{post['title']} {post['content']}".lower()
        
        matched_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in text_content:
                score += 1
                matched_keywords.append(keyword)
                
        # Bonus scoring
        if post['upvotes'] > 10:
            score += 1
        if post['upvotes'] > 50:
            score += 1
        if post['comments'] > 5:
            score += 1
        if post['comments'] > 20:
            score += 1
            
        # Bonus for multiple keyword matches
        if len(matched_keywords) > 2:
            score += 2
            
        if score > 0:
            self.debug_log(f"Post scored {score}: '{post['title'][:50]}...' (matched: {matched_keywords[:3]})")
            
        return score
        
    def update_display(self):
        """Update the display with current results"""
        if self.current_view == "table":
            self.update_table_view()
        elif self.current_view == "list":
            self.update_list_view()
        elif self.current_view == "card":
            self.update_card_view()
            
        # Update results count (only if the label exists)
        if hasattr(self, 'results_count_label'):
            self.results_count_label.configure(text=f"Results: {len(self.search_results)}")
        
    def update_table_view(self):
        """Update the table view"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items
        for post in self.search_results:
            self.tree.insert("", "end", values=(
                post['score'],
                post['subreddit'],
                post['title'][:100] + "..." if len(post['title']) > 100 else post['title'],
                post['author'],
                post['upvotes'],
                post['comments']
            ))
            
    def update_list_view(self):
        """Update the list view"""
        self.list_text.delete(1.0, tk.END)
        
        for i, post in enumerate(self.search_results, 1):
            self.list_text.insert(tk.END, f"{i}. [{post['score']}] {post['title']}\n")
            self.list_text.insert(tk.END, f"   r/{post['subreddit']} | u/{post['author']} | {post['upvotes']} upvotes | {post['comments']} comments\n")
            self.list_text.insert(tk.END, f"   {post['url']}\n")
            if post['content']:
                self.list_text.insert(tk.END, f"   {post['content'][:200]}...\n")
            self.list_text.insert(tk.END, "\n" + "-"*80 + "\n\n")
            
    def update_card_view(self):
        """Update the card view"""
        # Clear existing cards
        for widget in self.card_scroll.winfo_children():
            widget.destroy()
            
        # Add new cards
        for post in self.search_results:
            card = ctk.CTkFrame(self.card_scroll)
            card.pack(fill="x", padx=10, pady=5)
            
            # Title and score
            title_frame = ctk.CTkFrame(card)
            title_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(title_frame, text=f"[{post['score']}] {post['title']}", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=2)
            
            # Metadata
            meta_text = f"r/{post['subreddit']} | u/{post['author']} | {post['upvotes']} upvotes | {post['comments']} comments"
            ctk.CTkLabel(card, text=meta_text, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5, pady=2)
            
            # Content preview
            if post['content']:
                content_preview = post['content'][:300] + "..." if len(post['content']) > 300 else post['content']
                ctk.CTkLabel(card, text=content_preview, wraplength=600, justify="left").pack(anchor="w", padx=5, pady=2)
            
            # URL button
            ctk.CTkButton(card, text="Open Post", width=100, 
                         command=lambda url=post['url']: webbrowser.open(url)).pack(anchor="w", padx=5, pady=2)
            
    def update_status(self, message):
        """Update the status label"""
        self.status_label.configure(text=message)
        
    def clear_results(self):
        """Clear all search results"""
        self.search_results = []
        self.update_display()
        self.update_status("Results cleared.")
        self.debug_log("Search results cleared by user")
        
    def on_item_double_click(self, event):
        """Handle double-click on table item"""
        try:
            item = self.tree.selection()[0]
            item_index = self.tree.index(item)
            
            if item_index < len(self.search_results):
                post = self.search_results[item_index]
                self.debug_log(f"Opening post: {post['url']}")
                webbrowser.open(post['url'])
        except:
            pass  # Ignore errors if no item selected
            
    # Menu functions
    def file_menu(self):
        """File menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Clear Cache", command=self.clear_cache)
        menu.add_command(label="Show Debug Console", command=self.show_debug_window)
        menu.add_command(label="Exit", command=self.root.quit)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def search_menu(self):
        """Search menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Clear Results", command=self.clear_results)
        menu.add_command(label="Refresh Keywords", command=self.load_keywords)
        menu.add_command(label="Test Connection", command=self.test_reddit_connection)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def export_menu(self):
        """Export menu options"""
        if not self.search_results:
            messagebox.showwarning("No Data", "No search results to export.")
            return
            
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Export as CSV", command=self.export_csv)
        menu.add_command(label="Export as Markdown", command=self.export_markdown)
        menu.add_command(label="Export as PDF", command=self.export_pdf)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def keywords_menu(self):
        """Keywords menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Keywords", command=self.edit_keywords)
        menu.add_command(label="Add Keywords", command=self.add_keywords)
        menu.add_command(label="Reset to Defaults", command=self.reset_keywords)
        menu.add_command(label="Show Current Keywords", command=self.show_loaded_keywords)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def help_menu(self):
        """Help menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="About", command=self.show_about)
        menu.add_command(label="User Guide", command=self.show_help)
        menu.add_command(label="Open Program Folder", command=self.open_program_folder)
        menu.add_command(label="Debug Console", command=self.show_debug_window)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def edit_keywords(self):
        """Open keywords editor window"""
        editor = ctk.CTkToplevel(self.root)
        editor.title("Edit Keywords")
        editor.geometry("600x500")
        editor.transient(self.root)
        editor.grab_set()
        
        # Keywords text area
        ctk.CTkLabel(editor, text="Edit Keywords (one per line):", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        keywords_text = ctk.CTkTextbox(editor, width=550, height=350)
        keywords_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Load current keywords
        keywords_text.insert("0.0", "\n".join(self.keywords))
        
        # Buttons frame
        button_frame = ctk.CTkFrame(editor)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def save_keywords():
            new_keywords = keywords_text.get("0.0", "end-1c").strip().split("\n")
            self.keywords = [k.strip() for k in new_keywords if k.strip()]
            self.save_keywords()
            self.debug_log(f"Keywords edited - now have {len(self.keywords)} keywords")
            editor.destroy()
            messagebox.showinfo("Success", f"Saved {len(self.keywords)} keywords.")
            
        def cancel_edit():
            editor.destroy()
            
        ctk.CTkButton(button_frame, text="Save", command=save_keywords).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=cancel_edit).pack(side="left", padx=5)
        
    def add_keywords(self):
        """Add new keywords dialog"""
        dialog = ctk.CTkInputDialog(text="Enter new keywords (separated by commas):", title="Add Keywords")
        new_keywords = dialog.get_input()
        
        if new_keywords:
            keywords_to_add = [k.strip() for k in new_keywords.split(",") if k.strip()]
            before_count = len(self.keywords)
            self.keywords.extend(keywords_to_add)
            self.keywords = list(set(self.keywords))  # Remove duplicates
            after_count = len(self.keywords)
            self.save_keywords()
            
            added_count = after_count - before_count
            self.debug_log(f"Added {added_count} new unique keywords (total now: {after_count})")
            messagebox.showinfo("Success", f"Added {added_count} new keywords. Total: {after_count}")
            
    def reset_keywords(self):
        """Reset keywords to default list"""
        if messagebox.askyesno("Confirm Reset", "Reset all keywords to default list? This will remove any custom keywords."):
            default_keywords = [
                "manual data entry", "copy and paste", "one by one", "individually processing",
                "manually updating", "doing this manually", "repetitive workflow", "same process over and over",
                "tedious task", "manual process", "time-consuming", "repetitive task", "doing this by hand",
                "takes hours to", "streamline", "workflow", "eating up my time", "consuming hours",
                "spending all day", "full-time job just to", "can't scale", "bottleneck", "slowing us down",
                "wasting so much time", "can't keep up", "organize files", "sort through",
                "file management nightmare", "data scattered", "inconsistent formats", "duplicate entries",
                "merge data", "clean up data", "keep track of", "monitor changes", "get notifications when",
                "alert me if", "check regularly", "status updates", "progress tracking", "losing track",
                "transfer data between", "export from X import to Y", "systems don't talk", "manual sync",
                "update multiple places", "cross-platform", "between systems", "different platforms",
                "migration", "consolidate", "synchronize", "notify team when", "distribute updates",
                "collect responses", "coordinate schedules", "manage requests", "inventory tracking",
                "customer follow-up", "order processing", "appointment scheduling", "invoice generation",
                "report compilation", "lead management", "project status", "manage inventory",
                "track customers", "reporting", "analytics", "wish there was a way",
                "there has to be a better way", "driving me crazy", "hundreds of", "thousands of",
                "bulk", "mass", "optimize", "integration"
            ]
            self.keywords = default_keywords
            self.save_keywords()
            self.debug_log("Keywords reset to default list")
            messagebox.showinfo("Success", "Keywords reset to default list.")
            
    def export_csv(self):
        """Export results to CSV"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_results_{timestamp}.csv"
            filepath = os.path.join(self.exports_folder, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Score', 'Title', 'Subreddit', 'Author', 'Upvotes', 'Comments', 'URL', 'Content']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for post in self.search_results:
                    writer.writerow({
                        'Score': post['score'],
                        'Title': post['title'],
                        'Subreddit': post['subreddit'],
                        'Author': post['author'],
                        'Upvotes': post['upvotes'],
                        'Comments': post['comments'],
                        'URL': post['url'],
                        'Content': post['content']
                    })
                    
            self.debug_log(f"Exported {len(self.search_results)} results to CSV: {filename}")
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export CSV: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Export Error", error_msg)
            
    def export_markdown(self):
        """Export results to Markdown"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_results_{timestamp}.md"
            filepath = os.path.join(self.exports_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as mdfile:
                mdfile.write("# Reddit Helper Helper Results\n\n")
                mdfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                mdfile.write(f"Total Results: {len(self.search_results)}\n\n")
                mdfile.write("---\n\n")
                
                for i, post in enumerate(self.search_results, 1):
                    mdfile.write(f"## {i}. {post['title']}\n\n")
                    mdfile.write(f"**Score:** {post['score']} | **Subreddit:** r/{post['subreddit']} | **Author:** u/{post['author']}\n\n")
                    mdfile.write(f"**Engagement:** {post['upvotes']} upvotes, {post['comments']} comments\n\n")
                    mdfile.write(f"**URL:** [{post['url']}]({post['url']})\n\n")
                    
                    if post['content']:
                        mdfile.write(f"**Content:**\n{post['content']}\n\n")
                    
                    mdfile.write("---\n\n")
                    
            self.debug_log(f"Exported {len(self.search_results)} results to Markdown: {filename}")
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export Markdown: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Export Error", error_msg)
            
    def export_pdf(self):
        """Export results to PDF"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_results_{timestamp}.pdf"
            filepath = os.path.join(self.exports_folder, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("Reddit Helper Helper Results", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Metadata
            meta_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Total Results: {len(self.search_results)}"
            meta = Paragraph(meta_text, styles['Normal'])
            story.append(meta)
            story.append(Spacer(1, 12))
            
            # Results
            for i, post in enumerate(self.search_results, 1):
                # Post header
                header_text = f"<b>{i}. {post['title']}</b>"
                header = Paragraph(header_text, styles['Heading2'])
                story.append(header)
                
                # Post metadata
                meta_text = f"Score: {post['score']} | Subreddit: r/{post['subreddit']} | Author: u/{post['author']}<br/>Engagement: {post['upvotes']} upvotes, {post['comments']} comments"
                meta = Paragraph(meta_text, styles['Normal'])
                story.append(meta)
                
                # URL
                url_text = f"URL: {post['url']}"
                url = Paragraph(url_text, styles['Normal'])
                story.append(url)
                
                # Content
                if post['content']:
                    content_text = post['content'][:500] + "..." if len(post['content']) > 500 else post['content']
                    content = Paragraph(f"Content: {content_text}", styles['Normal'])
                    story.append(content)
                
                story.append(Spacer(1, 12))
            
            doc.build(story)
            self.debug_log(f"Exported {len(self.search_results)} results to PDF: {filename}")
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export PDF: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Export Error", error_msg)
            
    def clear_cache(self):
        """Clear application cache"""
        if messagebox.askyesno("Clear Cache", "Clear all cached data? This will not affect your keywords or exported files."):
            self.search_results = []
            self.update_display()
            self.debug_log("Application cache cleared by user")
            messagebox.showinfo("Cache Cleared", "Application cache has been cleared.")
            
    def show_about(self):
        """Show about dialog"""
        about_text = """Reddit Helper Helper

A tool to find Reddit posts where people might need Diamond Lane Digital to the rescue.

Features:
• Keyword-based search across Reddit
• Multiple view modes (Table, List, Card)
• Export to CSV, Markdown, and PDF
• Customizable keywords list
• Light/Dark theme support
• Real-time debug console
• Reddit API + HTML scraping

Version: 2.0 (Debug Edition)
Created with CustomTkinter"""
        
        messagebox.showinfo("About Reddit Helper Helper", about_text)
        
    def show_help(self):
        """Show help window"""
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("700x600")
        help_window.transient(self.root)
        help_window.grab_set()
        
        help_text = """REDDIT HELPER HELPER - USER GUIDE

GETTING STARTED:
1. Click the "Search Reddit" button to start searching with default keywords
2. Optionally add additional search terms in the "Search Terms" field
3. Optionally specify a subreddit to focus your search
4. Use the Stop button to halt a search in progress

SEARCH FEATURES:
• Searches using Reddit's API first, then HTML scraping as backup
• Uses intelligent keyword matching from your keyword list
• Scores posts based on keyword relevance and engagement
• Finds posts where people express problems that need solutions

VIEW MODES:
• Table View: Spreadsheet-like display with sortable columns
• List View: Text-based list format
• Card View: Visual cards showing post details

KEYWORDS:
• Edit keywords through the Keywords menu
• Add your own custom keywords
• Reset to default list anytime
• Keywords are saved automatically in JSON format

DEBUGGING:
• Use the Debug Console to see real-time search activity
• Test your connection to Reddit
• View loaded keywords and search progress
• Debug any search issues

EXPORTING:
• CSV: For spreadsheet analysis
• Markdown: For documentation
• PDF: For reports and sharing

TIPS:
• Higher scored posts are more likely to need solutions
• Double-click table rows to open posts in browser
• Use the Clear Results button to start fresh
• Check the status bar for search progress
• Open Debug Console if searches aren't working

TROUBLESHOOTING:
• If no results found, check Debug Console for errors
• Test Reddit connection using Debug menu
• Verify keywords are loaded correctly
• Try different search terms or subreddits

FILES LOCATION:
All program files are saved in:
Documents/Reddit Helper Helper/
• keywords.json - Your keyword list
• Exports/ - Exported search results"""
        
        help_textbox = ctk.CTkTextbox(help_window, width=650, height=500)
        help_textbox.pack(padx=20, pady=20, fill="both", expand=True)
        help_textbox.insert("0.0", help_text)
        help_textbox.configure(state="disabled")
        
        ctk.CTkButton(help_window, text="Close", command=help_window.destroy).pack(pady=10)
        
    def open_program_folder(self):
        """Open the program folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.program_folder)
                self.debug_log(f"Opened program folder: {self.program_folder}")
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{self.program_folder}"')
                self.debug_log(f"Opened program folder: {self.program_folder}")
        except Exception as e:
            error_msg = f"Could not open folder: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def run(self):
        """Start the application"""
        self.debug_log("Starting main application loop")
        self.root.mainloop()

def main():
    """Main function to run the application"""
    try:
        app = RedditHelperHelper()
        app.run()
    except Exception as e:
        error_msg = f"Application error: {str(e)}"
        print(error_msg)
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()