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
import markdown

class RedditHelperHelper:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Reddit Helper Helper v3.0")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Theme settings
        self.dark_mode = True
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Data storage
        self.keywords = []
        self.subreddits_data = {}
        self.all_subreddits_list = []
        self.master_subreddits_list = []
        self.search_results = []
        self.cache_data = {}
        self.current_view = "table"
        self.is_searching = False
        self.search_mode = "scrape"

        # Add these delay settings
        self.delay_min = 1.0
        self.delay_max = 3.0
        self.max_total_results = 100000  # Add this
        self.max_results_per_subreddit = 10000  # Add this
        self.enable_pagination = True  # Add this
        
        # Search scope settings
        self.search_scope = "all_our_subreddits"  # "all_reddit", "all_our_subreddits", or specific subreddit
        self.selected_subreddit = None
        
        # Debug window reference
        self.debug_window = None
        self.debug_text = None
        
        # Create directories
        self.create_directories()
        
        # Load data files
        self.load_keywords()
        self.load_subreddits()
        self.load_master_subreddits()
        
        # Setup GUI
        self.setup_gui()
        
        # Variables for search control
        self.search_thread = None
        self.stop_search = False
        
        # Log initial status
        self.debug_log("=== Reddit Helper Helper v3.0 Started ===")
        self.debug_log(f"Program folder: {self.program_folder}")
        self.debug_log(f"Keywords loaded: {len(self.keywords)}")
        self.debug_log(f"Subreddits loaded: {len(self.all_subreddits_list)}")
        self.debug_log(f"Search mode: {self.search_mode}")
        self.debug_log(f"Default search scope: {self.search_scope}")
        
    def debug_log(self, message):
        """Add message to debug log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # If debug window exists, update it
        if self.debug_text:
            try:
                self.debug_text.insert(tk.END, log_message + "\n")
                self.debug_text.see(tk.END)
            except:
                pass
                
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
            "bulk", "mass", "optimize", "integration", "automate", "automation"
        ]
        
        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r') as f:
                    self.keywords = json.load(f)
                self.debug_log(f"✓ Loaded {len(self.keywords)} keywords from JSON file")
            except Exception as e:
                self.debug_log(f"Error loading keywords: {str(e)}")
                self.keywords = default_keywords
                self.save_keywords()
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
            self.debug_log(f"✓ Saved {len(self.keywords)} keywords")
        except Exception as e:
            self.debug_log(f"Error saving keywords: {str(e)}")
            
    def load_subreddits(self):
        """Load subreddits from JSON file or create default structure"""
        subreddits_file = os.path.join(self.program_folder, "subreddits.json")
        self.debug_log(f"Loading subreddits from: {subreddits_file}")
        
        default_subreddits = {
            "metadata": {
                "version": "3.0",
                "last_updated": "2025-01-07",
                "total_subreddits": 58,
                "description": "Categorized subreddits for finding business problems and automation opportunities"
            },
            "categories": {
                "core_business": {
                    "description": "Primary business and entrepreneurship subreddits",
                    "subreddits": [
                        "entrepreneur", "smallbusiness", "business", "startups", "startup",
                        "solopreneur", "SmallBusinessOwners", "small_business_ideas"
                    ]
                },
                "marketing_sales": {
                    "description": "Marketing, sales, and customer acquisition",
                    "subreddits": [
                        "marketing", "sales", "DigitalMarketingHelp", "MarketingHelp",
                        "ecommerce", "agency", "customerservice", "growth"
                    ]
                },
                "freelance_consulting": {
                    "description": "Independent contractors and consultants",
                    "subreddits": [
                        "freelance", "consulting", "digitalnomad", "remotework", "coaching"
                    ]
                },
                "productivity_tools": {
                    "description": "Productivity, workflow, and process optimization",
                    "subreddits": [
                        "productivity", "workflow", "automation", "organization", 
                        "projectmanagement", "excel", "Efficiency"
                    ]
                },
                "finance_operations": {
                    "description": "Financial management and business operations",
                    "subreddits": [
                        "accounting", "Bookkeeping", "finance", "crm", "analytics", "data"
                    ]
                },
                "tech_development": {
                    "description": "Technology and software development",
                    "subreddits": [
                        "webdev", "programming", "SaaS", "it", "sysadmin", "msp"
                    ]
                },
                "industry_specific": {
                    "description": "Industry-specific business communities",
                    "subreddits": [
                        "realestate", "insurance", "legaladvice", "legal", "nonprofit",
                        "restaurantowners", "restaurant", "retailowners", "retail",
                        "healthcare", "education", "Training"
                    ]
                },
                "support_help": {
                    "description": "General help and motivation communities",
                    "subreddits": [
                        "help", "getmotivated", "juststart", "StartupsHelpStartups"
                    ]
                },
                "fitness_wellness": {
                    "description": "Fitness and wellness business communities", 
                    "subreddits": [
                        "fitness", "personaltraining"
                    ]
                }
            },
            "search_priorities": {
                "high_priority": [
                    "entrepreneur", "smallbusiness", "help", "startup", "DigitalMarketingHelp", 
                    "MarketingHelp", "SmallBusinessOwners", "automation", "excel", "productivity"
                ],
                "medium_priority": [
                    "consulting", "freelance", "ecommerce", "analytics", "Bookkeeping", 
                    "projectmanagement", "customerservice", "workflow"
                ],
                "specialized": [
                    "sysadmin", "msp", "realestate", "healthcare", "legal", "restaurant", 
                    "retail", "nonprofit", "insurance"
                ]
            }
        }
        
        if os.path.exists(subreddits_file):
            try:
                with open(subreddits_file, 'r') as f:
                    self.subreddits_data = json.load(f)
                self._extract_subreddit_list()
                self.debug_log(f"✓ Loaded {len(self.all_subreddits_list)} subreddits from JSON file")
            except Exception as e:
                self.debug_log(f"Error loading subreddits: {str(e)}")
                self.subreddits_data = default_subreddits
                self._extract_subreddit_list()
                self.save_subreddits()
        else:
            self.debug_log("Subreddits file not found, creating with defaults")
            self.subreddits_data = default_subreddits
            self._extract_subreddit_list()
            self.save_subreddits()

    def load_master_subreddits(self):
        """Load master subreddits from subreddit_master.json file"""
        master_file = os.path.join(os.path.dirname(__file__), "subreddit_master.json")
        self.debug_log(f"Loading master subreddits from: {master_file}")
        
        self.master_subreddits_list = []
        
        if os.path.exists(master_file):
            try:
                with open(master_file, 'r', encoding='utf-8') as f:
                    master_data = json.load(f)
                
                if 'subreddits' in master_data:
                    self.master_subreddits_list = [sub['name'] for sub in master_data['subreddits']]
                    self.debug_log(f"✓ Loaded {len(self.master_subreddits_list)} master subreddits")
                else:
                    self.debug_log("Master file missing 'subreddits' key")
                    
            except Exception as e:
                self.debug_log(f"Error loading master subreddits: {str(e)}")
                self.master_subreddits_list = []
        else:
            self.debug_log("Master subreddits file not found")
            self.master_subreddits_list = []        
            
    def _extract_subreddit_list(self):
        """Extract flat list of all subreddits from categorized data"""
        self.all_subreddits_list = []
        if 'categories' in self.subreddits_data:
            for category_data in self.subreddits_data['categories'].values():
                if 'subreddits' in category_data:
                    self.all_subreddits_list.extend(category_data['subreddits'])
        
        # Remove duplicates and sort
        self.all_subreddits_list = sorted(list(set(self.all_subreddits_list)))
        
    def save_subreddits(self):
        """Save subreddits to JSON file"""
        subreddits_file = os.path.join(self.program_folder, "subreddits.json")
        try:
            with open(subreddits_file, 'w') as f:
                json.dump(self.subreddits_data, f, indent=2)
            self.debug_log(f"✓ Saved subreddits data with {len(self.all_subreddits_list)} total subreddits")
        except Exception as e:
            self.debug_log(f"Error saving subreddits: {str(e)}")
            
    def setup_gui(self):
        """Setup the main GUI"""
        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
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
        self.menu_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.menu_frame.grid_columnconfigure(8, weight=1)
        
        # Menu buttons
        ctk.CTkButton(self.menu_frame, text="File", width=60, command=self.file_menu).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Search", width=60, command=self.search_menu).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Export", width=60, command=self.export_menu).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Keywords", width=80, command=self.keywords_menu).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Subreddits", width=80, command=self.subreddits_menu).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Debug", width=60, command=self.show_debug_window).grid(row=0, column=5, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Help", width=60, command=self.help_menu).grid(row=0, column=6, padx=5, pady=5)
        
        # Search mode toggle
        self.mode_label = ctk.CTkLabel(self.menu_frame, text="Mode:")
        self.mode_label.grid(row=0, column=7, padx=5, pady=5)
        
        self.mode_switch = ctk.CTkSwitch(self.menu_frame, text="Scrape", command=self.toggle_search_mode)
        self.mode_switch.grid(row=0, column=8, padx=5, pady=5)
        self.mode_switch.select()  # Default to scrape mode
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(self.menu_frame, text="🌙 Dark", width=80, command=self.toggle_theme)
        self.theme_button.grid(row=0, column=9, padx=5, pady=5, sticky="e")
        
    def create_toolbar(self):
        """Create the toolbar with subreddit scope selector"""
        self.toolbar_frame = ctk.CTkFrame(self.root, height=80)
        self.toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.toolbar_frame.grid_columnconfigure(1, weight=1)
        
        # Top row - Scope selection
        scope_frame = ctk.CTkFrame(self.toolbar_frame)
        scope_frame.grid(row=0, column=0, columnspan=6, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(scope_frame, text="Search Scope:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        
        # Scope dropdown
        self.scope_dropdown = ctk.CTkComboBox(
            scope_frame, 
            width=300,
            values=self.get_scope_options(),
            command=self.on_scope_changed
        )
        self.scope_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.scope_dropdown.set("All Our Subreddits")
        
        # Refresh subreddits button
        ctk.CTkButton(scope_frame, text="🔄 Refresh", command=self.refresh_subreddits, width=80).grid(row=0, column=2, padx=5, pady=5)
        
        # Bottom row - Search controls
        search_frame = ctk.CTkFrame(self.toolbar_frame)
        search_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=5, pady=5)
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Custom Keywords:").grid(row=0, column=0, padx=5, pady=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Leave empty to use default keywords, or enter custom terms...")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Add delay controls here
        delay_frame = ctk.CTkFrame(search_frame)
        delay_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(delay_frame, text="Request Delay (seconds):").grid(row=0, column=0, padx=5, pady=5)

        # Min delay
        ctk.CTkLabel(delay_frame, text="Min:").grid(row=0, column=1, padx=(20, 5), pady=5)
        self.delay_min_var = ctk.StringVar(value=str(self.delay_min))
        self.delay_min_entry = ctk.CTkEntry(delay_frame, width=60, textvariable=self.delay_min_var)
        self.delay_min_entry.grid(row=0, column=2, padx=5, pady=5)

        # Max delay
        ctk.CTkLabel(delay_frame, text="Max:").grid(row=0, column=3, padx=(20, 5), pady=5)
        self.delay_max_var = ctk.StringVar(value=str(self.delay_max))
        self.delay_max_entry = ctk.CTkEntry(delay_frame, width=60, textvariable=self.delay_max_var)
        self.delay_max_entry.grid(row=0, column=4, padx=5, pady=5)

        # After the delay controls, add result limit controls
        limits_frame = ctk.CTkFrame(search_frame)
        limits_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(limits_frame, text="Result Limits:").grid(row=0, column=0, padx=5, pady=5)

        # Max total results
        ctk.CTkLabel(limits_frame, text="Total:").grid(row=0, column=1, padx=(20, 5), pady=5)
        self.max_total_var = ctk.StringVar(value=str(self.max_total_results))
        self.max_total_entry = ctk.CTkEntry(limits_frame, width=80, textvariable=self.max_total_var)
        self.max_total_entry.grid(row=0, column=2, padx=5, pady=5)

        # Max per subreddit
        ctk.CTkLabel(limits_frame, text="Per Sub:").grid(row=0, column=3, padx=(20, 5), pady=5)
        self.max_per_sub_var = ctk.StringVar(value=str(self.max_results_per_subreddit))
        self.max_per_sub_entry = ctk.CTkEntry(limits_frame, width=80, textvariable=self.max_per_sub_var)
        self.max_per_sub_entry.grid(row=0, column=4, padx=5, pady=5)

        # Pagination toggle
        self.enable_pagination_var = ctk.BooleanVar(value=self.enable_pagination)
        pagination_check = ctk.CTkCheckBox(limits_frame, text="Enable Pagination", variable=self.enable_pagination_var)
        pagination_check.grid(row=0, column=5, padx=(20, 5), pady=5)

        # Control buttons (keep only this section)
        self.search_button = ctk.CTkButton(search_frame, text="🔍 Search Reddit", command=self.start_search, width=120)
        self.search_button.grid(row=3, column=0, padx=5, pady=5)

        self.stop_button = ctk.CTkButton(search_frame, text="⏹ Stop", command=self.stop_search_func, state="disabled", width=80)
        self.stop_button.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkButton(search_frame, text="🗑 Clear Results", command=self.clear_results, width=120).grid(row=3, column=2, padx=5, pady=5)
        ctk.CTkButton(search_frame, text="💾 Clear Cache", command=self.clear_cache, width=100).grid(row=3, column=3, padx=5, pady=5)
        
    def get_scope_options(self):
        """Get list of scope options for dropdown"""
        options = ["All Reddit", "All Our Subreddits", "Master"]  # Add "Master" here
        options.extend([f"r/{sub}" for sub in self.all_subreddits_list])
        return options
        
    def refresh_subreddits(self):
        """Refresh subreddit list from JSON file"""
        self.load_subreddits()
        self.load_master_subreddits()  # Add this line
        
        # Update dropdown options
        new_options = self.get_scope_options()
        self.scope_dropdown.configure(values=new_options)
        
        # Reset to default if current selection is invalid
        current_selection = self.scope_dropdown.get()
        if current_selection not in new_options:
            self.scope_dropdown.set("All Our Subreddits")
            self.search_scope = "all_our_subreddits"
            
        self.debug_log(f"Refreshed subreddits: {len(self.all_subreddits_list)} total, {len(self.master_subreddits_list)} master")
        self.update_status(f"Refreshed {len(self.all_subreddits_list)} subreddits from JSON")
        
    def on_scope_changed(self, selection):
        """Handle scope dropdown change"""
        if selection == "All Reddit":
            self.search_scope = "all_reddit"
            self.selected_subreddit = None
            self.debug_log("Search scope: All Reddit (site-wide)")
        elif selection == "All Our Subreddits":
            self.search_scope = "all_our_subreddits"
            self.selected_subreddit = None
            self.debug_log("Search scope: All Our Subreddits")
        elif selection == "Master":  # Add this elif block
            self.search_scope = "master"
            self.selected_subreddit = None
            # Safety check in case master list isn't loaded
            if hasattr(self, 'master_subreddits_list'):
                count = len(self.master_subreddits_list)
            else:
                count = 0
            self.debug_log(f"Search scope: Master ({count} subreddits)")
        elif selection.startswith("r/"):
            self.search_scope = "single_subreddit"
            self.selected_subreddit = selection[2:]  # Remove "r/" prefix
            self.debug_log(f"Search scope: Single subreddit - r/{self.selected_subreddit}")
        
        self.update_status(f"Search scope: {selection}")
        
    def create_main_content(self):
        """Create the main content area"""
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
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
        self.tree.column("Subreddit", width=120)
        self.tree.column("Title", width=500)
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
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready to search Reddit for business problems...")
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.grid(row=0, column=1, padx=5, pady=5)
        self.progress_bar.set(0)
        
        # Results count
        self.results_count_label = ctk.CTkLabel(self.status_frame, text="Results: 0")
        self.results_count_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Scope indicator
        self.scope_label = ctk.CTkLabel(self.status_frame, text="Scope: All Our Subreddits")
        self.scope_label.grid(row=0, column=3, padx=5, pady=5)
        
    def toggle_search_mode(self):
        """Toggle between scrape and API modes"""
        if self.mode_switch.get():
            self.search_mode = "scrape"
            self.mode_switch.configure(text="Scrape")
            self.debug_log("Search mode: HTML Scraping")
        else:
            self.search_mode = "api"
            self.mode_switch.configure(text="API")
            self.debug_log("Search mode: Reddit API")
            
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
            self.debug_log(f"Search mode: {self.search_mode}")
            self.debug_log(f"Search scope: {self.search_scope}")
            if self.selected_subreddit:
                self.debug_log(f"Target subreddit: r/{self.selected_subreddit}")
            
            # Start search thread
            self.search_thread = threading.Thread(target=self.search_reddit)
            self.search_thread.daemon = True
            self.search_thread.start()
            
    def stop_search_func(self):
        """Stop the current search"""
        self.stop_search = True
        self.debug_log("Search stop requested by user")
        self.update_status("Stopping search...")
        
    def search_reddit(self):
        """Main search function - handles different search scopes"""
        try:
            # Determine search keywords
            custom_keywords = self.search_entry.get().strip()
            if custom_keywords:
                # Use custom keywords
                search_keywords = [k.strip() for k in custom_keywords.split(',')]
                self.debug_log(f"Using custom keywords: {len(search_keywords)} terms")
            else:
                # Use default keywords
                search_keywords = self.keywords.copy()
                self.debug_log(f"Using default keywords: {len(search_keywords)} terms")
            
            posts = []
            
            # Execute search based on scope
            if self.search_scope == "all_reddit":
                self.debug_log("Executing site-wide Reddit search")
                posts = self.search_all_reddit(search_keywords)
            elif self.search_scope == "all_our_subreddits":
                self.debug_log(f"Searching all {len(self.all_subreddits_list)} subreddits")
                posts = self.search_multiple_subreddits(self.all_subreddits_list, search_keywords)
            elif self.search_scope == "master":  # Add this elif block
                if hasattr(self, 'master_subreddits_list') and self.master_subreddits_list:
                    self.debug_log(f"Searching master list: {len(self.master_subreddits_list)} subreddits")
                    posts = self.search_multiple_subreddits(self.master_subreddits_list, search_keywords)
                else:
                    self.debug_log("Master subreddits list not available or empty")
                    posts = []
            elif self.search_scope == "single_subreddit":
                self.debug_log(f"Searching single subreddit: r/{self.selected_subreddit}")
                posts = self.search_single_subreddit(self.selected_subreddit, search_keywords)
            
            # Process and score posts
            if posts:
                self.debug_log(f"Found {len(posts)} posts, filtering and scoring...")
                
                for post in posts:
                    if self.stop_search:
                        break
                        
                    score = self.calculate_post_score(post, search_keywords)
                    if score > 0:
                        post['score'] = score
                        self.search_results.append(post)
                        
                        # Update display every 5 posts
                        if len(self.search_results) % 5 == 0:  # Update every 5 instead of every 5
                            self.root.after(0, self.update_display)
                
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
            
    def search_all_reddit(self, keywords):
        """Search all of Reddit using multiple strategies to avoid rate limits"""
        posts = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache'
            }
            
            # Strategy 1: Use popular general subreddits that often have business discussions
            general_business_subreddits = [
                'AskReddit', 'LifeProTips', 'YouShouldKnow', 'NoStupidQuestions',
                'personalfinance', 'jobs', 'careeradvice', 'WorkOnline',
                'findapath', 'careerguidance', 'cscareerquestions'
            ]
            
            # Strategy 2: Combine a few keywords into one search to reduce API calls
            if len(keywords) > 5:
                # Group keywords into broader search terms
                keyword_groups = [
                    '"manual process" OR "time consuming" OR "repetitive task"',
                    '"workflow" OR "automation" OR "streamline"',
                    '"data entry" OR "copy paste" OR "manually updating"',
                    '"business problem" OR "help" OR "solution needed"'
                ]
            else:
                # Use individual keywords if we have few
                keyword_groups = [f'"{keyword}"' for keyword in keywords[:3]]
            
            self.debug_log(f"Site-wide search using {len(keyword_groups)} keyword groups and {len(general_business_subreddits)} general subreddits")
            
            # First try: Search general subreddits with our keywords
            for i, subreddit in enumerate(general_business_subreddits):
                if self.stop_search:
                    break
                    
                progress = (i + 1) / (len(general_business_subreddits) + len(keyword_groups)) * 0.7
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                
                # Search this general subreddit
                subreddit_url = f"https://old.reddit.com/r/{subreddit}/search/.json?q=business+problem+help&restrict_sr=1&sort=new&limit=100"
                
                self.debug_log(f"Searching general subreddit: r/{subreddit}")
                self.root.after(0, lambda s=subreddit: self.update_status(f"Searching r/{s} for business problems..."))
                
                try:
                    response = requests.get(subreddit_url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            subreddit_posts = self.extract_from_json_sitewide(data, keywords, subreddit)
                            posts.extend(subreddit_posts)
                            
                            if subreddit_posts:
                                self.debug_log(f"✓ r/{subreddit}: {len(subreddit_posts)} relevant posts")
                            
                        except json.JSONDecodeError as e:
                            self.debug_log(f"JSON parse error for r/{subreddit}: {str(e)}")
                    elif response.status_code == 429:
                        self.debug_log(f"Rate limited on r/{subreddit}, waiting...")
                        time.sleep(3)  # Wait longer for rate limits
                    else:
                        self.debug_log(f"r/{subreddit} search failed: {response.status_code}")
                        
                except Exception as e:
                    self.debug_log(f"Error searching r/{subreddit}: {str(e)}")
                    
                time.sleep(2)  # Longer delay to avoid rate limits
                
            # Second try: Use Reddit's main search with fewer, broader terms
            if len(posts) < 10:  # Only if we don't have enough results
                self.debug_log("Trying Reddit main search with broader terms...")
                
                for i, search_term in enumerate(keyword_groups):
                    if self.stop_search:
                        break
                        
                    progress = 0.7 + (i + 1) / len(keyword_groups) * 0.25
                    self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                    
                    # Use main Reddit search
                    search_query = quote(search_term)
                    main_search_url = f"https://old.reddit.com/search/.json?q={search_query}&sort=new&limit=100&t=week"
                    
                    self.debug_log(f"Main Reddit search: {search_term[:30]}...")
                    self.root.after(0, lambda t=search_term: self.update_status(f"Site-wide search: {t[:30]}..."))
                    
                    try:
                        response = requests.get(main_search_url, headers=headers, timeout=20)
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                main_posts = self.extract_from_json_sitewide(data, keywords, "site_search")
                                posts.extend(main_posts)
                                
                                if main_posts:
                                    self.debug_log(f"✓ Main search '{search_term[:20]}...': {len(main_posts)} posts")
                                    
                            except json.JSONDecodeError as e:
                                self.debug_log(f"JSON parse error in main search: {str(e)}")
                                
                        elif response.status_code == 429:
                            self.debug_log(f"Rate limited on main search, waiting longer...")
                            time.sleep(5)  # Wait even longer
                            
                        else:
                            self.debug_log(f"Main search failed: {response.status_code}")
                            
                    except Exception as e:
                        self.debug_log(f"Error in main search: {str(e)}")
                        
                    time.sleep(3)  # Longer delay between main searches
                    
        except Exception as e:
            self.debug_log(f"Overall site-wide search error: {str(e)}")
            
        # Remove duplicates
        unique_posts = []
        seen_urls = set()
        
        for post in posts:
            if post['url'] not in seen_urls:
                unique_posts.append(post)
                seen_urls.add(post['url'])
                
        self.debug_log(f"Site-wide search complete. Found {len(unique_posts)} unique posts (from {len(posts)} total).")
        return unique_posts
        
    def extract_from_json_sitewide(self, data, keywords, source_info):
        """Extract posts from site-wide search JSON response"""
        posts = []
        
        try:
            if 'data' in data and 'children' in data['data']:
                for post_data in data['data']['children']:
                    if self.stop_search:
                        break
                        
                    if post_data['kind'] == 't3':  # Link/post type
                        post = post_data['data']
                        
                        # Skip if deleted, removed, or from banned subreddits
                        if (post.get('removed_by_category') or 
                            post.get('author') == '[deleted]' or
                            post.get('subreddit', '').lower() in ['shadowban', 'spam']):
                            continue
                        
                        title = post.get('title', '').strip()
                        if not title or len(title) < 15:  # Stricter title length for site-wide
                            continue
                        
                        content = post.get('selftext', '')
                        
                        post_info = {
                            'title': title,
                            'content': content,
                            'author': post.get('author', ''),
                            'subreddit': post.get('subreddit', source_info),
                            'upvotes': post.get('ups', 0),
                            'comments': post.get('num_comments', 0),
                            'url': f"https://www.reddit.com{post.get('permalink', '')}",
                            'score': 0,
                            'source': 'site_wide'
                        }
                        
                        # More strict relevance check for site-wide search
                        if self.is_relevant_post_strict(post_info, keywords):
                            posts.append(post_info)
                                
        except Exception as e:
            self.debug_log(f"Error parsing site-wide JSON: {str(e)}")
            
        return posts
        
    def is_relevant_post_strict(self, post_data, keywords):
        """Stricter relevance check for site-wide search"""
        text_content = f"{post_data['title']} {post_data['content']}".lower()
        
        # Check for keyword matches
        matches = 0
        for keyword in keywords:
            if keyword.lower() in text_content:
                matches += 1
                
        # For site-wide search, require at least 1 match AND business indicators
        if matches == 0:
            return False
            
        # Look for business/problem indicators
        business_indicators = [
            'business', 'work', 'job', 'company', 'startup', 'entrepreneur',
            'help', 'problem', 'issue', 'solution', 'advice', 'tip',
            'process', 'workflow', 'efficiency', 'time', 'money', 'cost',
            'customer', 'client', 'management', 'organize', 'track'
        ]
        
        has_business_context = any(indicator in text_content for indicator in business_indicators)
        
        # Also check post length - avoid very short posts
        total_length = len(post_data['title']) + len(post_data['content'])
        
        return has_business_context and total_length > 50
        
    def search_multiple_subreddits(self, subreddits, keywords):
        """Search multiple subreddits with pagination support"""
        posts = []
        seen_urls = set()
        seen_titles = set()
        
        try:
            # Use priority order for efficiency
            priority_subreddits = []
            if 'search_priorities' in self.subreddits_data:
                for priority_level in ['high_priority', 'medium_priority', 'specialized']:
                    if priority_level in self.subreddits_data['search_priorities']:
                        priority_subreddits.extend(self.subreddits_data['search_priorities'][priority_level])
            
            # Add remaining subreddits
            all_ordered_subreddits = priority_subreddits + [s for s in subreddits if s not in priority_subreddits]
            
            # Define how many results per subreddit (adjust this for total volume)
            results_per_subreddit = 100000 // len(all_ordered_subreddits) if len(all_ordered_subreddits) > 0 else 10000
            results_per_subreddit = max(results_per_subreddit, 1000)  # Minimum 1000 per subreddit
            
            sort_methods = ['new', 'hot', 'top']
            total_subreddits = len(all_ordered_subreddits)
            
            for i, subreddit in enumerate(all_ordered_subreddits):
                if self.stop_search:
                    break
                    
                progress = (i + 1) / total_subreddits * 0.95
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                
                subreddit_posts = []
                
                for sort_method in sort_methods:
                    if self.stop_search or len(subreddit_posts) >= results_per_subreddit:
                        break
                        
                    # Use pagination for each sort method
                    method_posts = self.search_subreddit_with_pagination(
                        subreddit, 
                        sort_method, 
                        keywords, 
                        seen_titles, 
                        seen_urls, 
                        max_results=results_per_subreddit // len(sort_methods)
                    )
                    
                    subreddit_posts.extend(method_posts)
                
                posts.extend(subreddit_posts)
                
                if subreddit_posts:
                    self.debug_log(f"✓ r/{subreddit} COMPLETE: {len(subreddit_posts)} total posts")
                
                # Update running total
                self.root.after(0, lambda t=len(posts): self.update_status(f"Found {t} posts so far..."))
                        
        except Exception as e:
            self.debug_log(f"Error in multiple subreddit search: {str(e)}")
            
        self.debug_log(f"Multiple subreddit search complete. Found {len(posts)} unique relevant posts.")
        return posts
        
    def search_single_subreddit(self, subreddit, keywords):
        """Search a single subreddit thoroughly"""
        posts = []
        seen_urls = set()
        seen_titles = set()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Get delay settings
            try:
                delay_min = float(self.delay_min_var.get())
                delay_max = float(self.delay_max_var.get())
                if delay_min > delay_max:
                    delay_min, delay_max = delay_max, delay_min
            except:
                delay_min, delay_max = 1.0, 3.0
            
            sort_methods = ['new', 'hot', 'rising', 'top']
            time_filters = ['day', 'week', 'month'] if subreddit in ['new', 'hot'] else [None]
            
            operations = []
            for sort_method in sort_methods:
                if sort_method == 'top':
                    for time_filter in time_filters:
                        operations.append((sort_method, time_filter))
                else:
                    operations.append((sort_method, None))
                    
            total_operations = len(operations)
            
            for i, (sort_method, time_filter) in enumerate(operations):
                if self.stop_search:
                    break
                    
                progress = (i + 1) / total_operations * 0.9
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                
                # Build URL
                url_parts = [f"https://old.reddit.com/r/{subreddit}/{sort_method}/.json?limit=100"]
                if time_filter:
                    url_parts[0] += f"&t={time_filter}"
                    
                json_url = url_parts[0]
                
                status_text = f"r/{subreddit} ({sort_method}"
                if time_filter:
                    status_text += f" - {time_filter}"
                status_text += ")"
                
                self.debug_log(f"Single subreddit search: {status_text}")
                self.root.after(0, lambda s=status_text: self.update_status(f"Searching {s}..."))
                
                try:
                    response = requests.get(json_url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            json_posts = self.extract_from_json(data, keywords, seen_titles, seen_urls, subreddit)
                            posts.extend(json_posts)
                            
                            if json_posts:
                                self.debug_log(f"✓ {status_text}: {len(json_posts)} new relevant posts")
                                
                        except json.JSONDecodeError as e:
                            self.debug_log(f"JSON parse error for {status_text}: {str(e)}")
                    else:
                        self.debug_log(f"Failed to access {status_text}: {response.status_code}")
                        
                except Exception as e:
                    self.debug_log(f"Error in {status_text}: {str(e)}")
                
                # Apply user-defined delay
                if i < total_operations - 1 and not self.stop_search:
                    import random
                    delay = random.uniform(delay_min, delay_max)
                    self.debug_log(f"Waiting {delay:.1f}s before next request...")
                    time.sleep(delay)
                    
        except Exception as e:
            self.debug_log(f"Error in single subreddit search: {str(e)}")
            
        self.debug_log(f"Single subreddit search complete. Found {len(posts)} unique relevant posts from r/{subreddit}.")
        return posts

    def search_subreddit_with_pagination(self, subreddit, sort_method, keywords, seen_titles, seen_urls, max_results=100000):
        """Search a subreddit with pagination support for massive results"""
        posts = []
        after_token = None
        page_count = 0
        max_pages = max_results // 100  # 100 is Reddit's max per request
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Get delay settings
            try:
                delay_min = float(self.delay_min_var.get())
                delay_max = float(self.delay_max_var.get())
                if delay_min > delay_max:
                    delay_min, delay_max = delay_max, delay_min
            except:
                delay_min, delay_max = 1.0, 3.0
            
            while len(posts) < max_results and page_count < max_pages:
                if self.stop_search:
                    break
                    
                # Build URL with pagination
                json_url = f"https://old.reddit.com/r/{subreddit}/{sort_method}/.json?limit=100"
                if after_token:
                    json_url += f"&after={after_token}"
                
                self.debug_log(f"Fetching page {page_count + 1} from r/{subreddit} ({sort_method})")
                self.root.after(0, lambda s=subreddit, p=page_count+1: self.update_status(f"r/{s} - Page {p}..."))
                
                try:
                    response = requests.get(json_url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract posts from this page
                        page_posts = self.extract_from_json(data, keywords, seen_titles, seen_urls, subreddit)
                        posts.extend(page_posts)
                        
                        # Get next page token
                        after_token = data.get('data', {}).get('after')
                        
                        if not after_token:
                            self.debug_log(f"No more pages available for r/{subreddit}")
                            break
                            
                        if page_posts:
                            self.debug_log(f"✓ Page {page_count + 1}: {len(page_posts)} relevant posts (Total: {len(posts)})")
                        
                        page_count += 1
                        
                        # Apply delay between pages
                        if after_token and not self.stop_search:
                            import random
                            delay = random.uniform(delay_min, delay_max)
                            self.debug_log(f"Waiting {delay:.1f}s before next page...")
                            time.sleep(delay)
                            
                    elif response.status_code == 429:
                        self.debug_log(f"Rate limited on r/{subreddit}, waiting longer...")
                        time.sleep(30)  # Wait longer for rate limits
                    else:
                        self.debug_log(f"Failed to access r/{subreddit}: {response.status_code}")
                        break
                        
                except Exception as e:
                    self.debug_log(f"Error on page {page_count + 1} for r/{subreddit}: {str(e)}")
                    break
                    
        except Exception as e:
            self.debug_log(f"Error in pagination search for r/{subreddit}: {str(e)}")
        
        self.debug_log(f"Pagination complete for r/{subreddit}: {len(posts)} posts from {page_count} pages")
        return posts

    def extract_from_json(self, data, keywords, seen_titles, seen_urls, source_subreddit="unknown"):
        """Extract posts from Reddit JSON response"""
        posts = []
        
        try:
            if 'data' in data and 'children' in data['data']:
                for post_data in data['data']['children']:
                    if self.stop_search:
                        break
                        
                    if post_data['kind'] == 't3':  # Link/post type
                        post = post_data['data']
                        
                        # Skip if deleted or removed
                        if post.get('removed_by_category') or post.get('author') == '[deleted]':
                            continue
                        
                        title = post.get('title', '').strip()
                        if not title or len(title) < 10:
                            continue
                        
                        post_info = {
                            'title': title,
                            'content': post.get('selftext', ''),
                            'author': post.get('author', ''),
                            'subreddit': post.get('subreddit', source_subreddit),
                            'upvotes': post.get('ups', 0),
                            'comments': post.get('num_comments', 0),
                            'url': f"https://www.reddit.com{post.get('permalink', '')}",
                            'score': 0,
                            'source': 'json'
                        }
                        
                        # Check for duplicates
                        title_key = title.lower().strip()
                        url_key = post_info['url'].lower().strip()
                        
                        if title_key not in seen_titles and url_key not in seen_urls:
                            if self.is_relevant_post(post_info, keywords):
                                posts.append(post_info)
                                seen_titles.add(title_key)
                                seen_urls.add(url_key)
                                
        except Exception as e:
            self.debug_log(f"Error parsing JSON: {str(e)}")
            
        return posts
        
    def is_relevant_post(self, post_data, keywords):
        """Check if post is relevant based on keywords"""
        text_content = f"{post_data['title']} {post_data['content']}".lower()
        
        # Check for keyword matches
        matches = 0
        for keyword in keywords:
            if keyword.lower() in text_content:
                matches += 1
                
        # Must have at least 1 keyword match to be relevant
        return matches > 0
        
    def calculate_post_score(self, post, keywords):
        """Calculate relevance score for a post"""
        score = 0
        text_content = f"{post['title']} {post['content']}".lower()
        
        matched_keywords = []
        
        # Keyword matching (primary scoring)
        for keyword in keywords:
            if keyword.lower() in text_content:
                score += 1
                matched_keywords.append(keyword)
                
        # Bonus scoring for engagement
        if post['upvotes'] > 10:
            score += 1
        if post['upvotes'] > 50:
            score += 2
        if post['comments'] > 5:
            score += 1
        if post['comments'] > 20:
            score += 2
            
        # Bonus for multiple keyword matches
        if len(matched_keywords) > 2:
            score += 3
        if len(matched_keywords) > 5:
            score += 5
            
        # Problem-specific bonuses
        problem_indicators = [
            "help", "how to", "how can", "need", "struggling", "problem", 
            "issue", "difficulty", "challenge", "stuck", "frustrated"
        ]
        
        for indicator in problem_indicators:
            if indicator in text_content:
                score += 2
                break
                
        return score
        
    def update_display(self):
        """Update the display with current results"""
        if self.current_view == "table":
            self.update_table_view()
        elif self.current_view == "list":
            self.update_list_view()
        elif self.current_view == "card":
            self.update_card_view()
            
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
                f"r/{post['subreddit']}",
                post['title'][:100] + "..." if len(post['title']) > 100 else post['title'],
                post['author'],
                post['upvotes'],
                post['comments']
            ))
            
    def update_list_view(self):
        """Update the list view"""
        self.list_text.delete(1.0, tk.END)
        
        for i, post in enumerate(self.search_results, 1):
            self.list_text.insert(tk.END, f"{i}. [Score: {post['score']}] {post['title']}\n")
            self.list_text.insert(tk.END, f"   r/{post['subreddit']} | u/{post['author']} | {post['upvotes']} upvotes | {post['comments']} comments\n")
            self.list_text.insert(tk.END, f"   {post['url']}\n")
            if post['content']:
                content_preview = post['content'][:200] + "..." if len(post['content']) > 200 else post['content']
                self.list_text.insert(tk.END, f"   Preview: {content_preview}\n")
            self.list_text.insert(tk.END, "\n" + "="*80 + "\n\n")
            
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
            
            ctk.CTkLabel(title_frame, text=f"[Score: {post['score']}] {post['title']}", 
                        font=ctk.CTkFont(size=14, weight="bold"), wraplength=600).pack(anchor="w", padx=5, pady=2)
            
            # Metadata with subreddit prominently displayed
            meta_text = f"r/{post['subreddit']} | u/{post['author']} | {post['upvotes']} upvotes | {post['comments']} comments"
            ctk.CTkLabel(card, text=meta_text, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5, pady=2)
            
            # Content preview
            if post['content']:
                content_preview = post['content'][:300] + "..." if len(post['content']) > 300 else post['content']
                ctk.CTkLabel(card, text=content_preview, wraplength=600, justify="left").pack(anchor="w", padx=5, pady=2)
            
            # URL button
            ctk.CTkButton(card, text="Open Post", width=100, 
                         command=lambda url=post['url']: webbrowser.open(url)).pack(anchor="w", padx=5, pady=2)
            
    def clear_results(self):
        """Clear search results display only"""
        self.search_results = []
        self.update_display()
        self.update_status("Search results cleared.")
        self.debug_log("Search results cleared by user")
        
    def clear_cache(self):
        """Clear memory cache"""
        self.cache_data = {}
        self.search_results = []
        self.update_display()
        self.update_status("Cache cleared.")
        self.debug_log("Memory cache cleared by user")
        messagebox.showinfo("Cache Cleared", "Memory cache has been cleared.")
        
    def update_status(self, message):
        """Update the status label"""
        self.status_label.configure(text=message)
        # Also update scope indicator
        scope_text = self.scope_dropdown.get() if hasattr(self, 'scope_dropdown') else "Unknown"
        if hasattr(self, 'scope_label'):
            self.scope_label.configure(text=f"Scope: {scope_text}")
        
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
            ctk.CTkButton(button_frame, text="Show Subreddits", command=self.show_subreddits_debug).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Show Keywords", command=self.show_keywords_debug).pack(side="left", padx=5)
            
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get("https://www.reddit.com", headers=headers, timeout=10)
            self.debug_log(f"Status Code: {response.status_code}")
            self.debug_log(f"Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                self.debug_log("✓ Successfully connected to Reddit")
            else:
                self.debug_log(f"✗ Failed to connect: {response.status_code}")
                
        except Exception as e:
            self.debug_log(f"✗ Connection error: {str(e)}")
            
    def show_subreddits_debug(self):
        """Show the currently loaded subreddits in debug"""
        self.debug_log("=== Loaded Subreddits ===")
        self.debug_log(f"Our subreddits: {len(self.all_subreddits_list)}")
        self.debug_log(f"Master subreddits: {len(self.master_subreddits_list)}")  # Add this line
        
        if 'categories' in self.subreddits_data:
            for category_name, category_data in self.subreddits_data['categories'].items():
                self.debug_log(f"\n{category_name.upper().replace('_', ' ')}:")
                if 'subreddits' in category_data:
                    for subreddit in category_data['subreddits']:
                        self.debug_log(f"  r/{subreddit}")
                        
        self.debug_log(f"\nSearch scope options: {len(self.get_scope_options())}")
            
    def show_keywords_debug(self):
        """Show the currently loaded keywords in debug"""
        self.debug_log("=== Loaded Keywords ===")
        self.debug_log(f"Total keywords: {len(self.keywords)}")
        
        for i, keyword in enumerate(self.keywords[:10]):
            self.debug_log(f"  {i+1}. {keyword}")
            
        if len(self.keywords) > 10:
            self.debug_log(f"  ... and {len(self.keywords) - 10} more")
            
    # MENU FUNCTIONS
    def file_menu(self):
        """File menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Clear Cache", command=self.clear_cache)
        menu.add_command(label="Show Debug Console", command=self.show_debug_window)
        menu.add_command(label="Open Program Folder", command=self.open_program_folder)
        menu.add_command(label="Exit", command=self.root.quit)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def search_menu(self):
        """Search menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Clear Results", command=self.clear_results)
        menu.add_command(label="Refresh Subreddits", command=self.refresh_subreddits)
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
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def keywords_menu(self):
        """Keywords menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Keywords", command=self.edit_keywords)
        menu.add_command(label="Add Keywords", command=self.add_keywords)
        menu.add_command(label="Reset to Defaults", command=self.reset_keywords)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def subreddits_menu(self):
        """Subreddits menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Subreddits", command=self.edit_subreddits)
        menu.add_command(label="Add Subreddits", command=self.add_subreddits)
        menu.add_command(label="View Categories", command=self.view_subreddit_categories)
        menu.add_command(label="Reset to Defaults", command=self.reset_subreddits)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def help_menu(self):
        """Help menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="About", command=self.show_about)
        menu.add_command(label="User Guide", command=self.show_help)
        menu.add_command(label="Open Program Folder", command=self.open_program_folder)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def edit_keywords(self):
        """Open keywords editor window"""
        editor = ctk.CTkToplevel(self.root)
        editor.title("Edit Keywords")
        editor.geometry("600x500")
        editor.transient(self.root)
        editor.grab_set()
        
        ctk.CTkLabel(editor, text="Edit Keywords (one per line):", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        keywords_text = ctk.CTkTextbox(editor, width=550, height=350)
        keywords_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        keywords_text.insert("0.0", "\n".join(self.keywords))
        
        button_frame = ctk.CTkFrame(editor)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def save_keywords():
            new_keywords = keywords_text.get("0.0", "end-1c").strip().split("\n")
            self.keywords = [k.strip() for k in new_keywords if k.strip()]
            self.save_keywords()
            self.debug_log(f"Keywords edited - now have {len(self.keywords)} keywords")
            editor.destroy()
            messagebox.showinfo("Success", f"Saved {len(self.keywords)} keywords.")
            
        ctk.CTkButton(button_frame, text="Save", command=save_keywords).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=editor.destroy).pack(side="left", padx=5)
        
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
            self.debug_log(f"Added {added_count} new keywords")
            messagebox.showinfo("Success", f"Added {added_count} new keywords. Total: {after_count}")
            
    def reset_keywords(self):
        """Reset keywords to default list"""
        if messagebox.askyesno("Confirm Reset", "Reset all keywords to default list?"):
            self.load_keywords()  # Reload defaults
            messagebox.showinfo("Success", "Keywords reset to default list.")
            
    def edit_subreddits(self):
        """Open subreddits editor window"""
        editor = ctk.CTkToplevel(self.root)
        editor.title("Edit Subreddits JSON")
        editor.geometry("800x600")
        editor.transient(self.root)
        editor.grab_set()
        
        ctk.CTkLabel(editor, text="Edit Subreddits JSON Structure:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # JSON text editor
        json_text = ctk.CTkTextbox(editor, width=750, height=450)
        json_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Load current JSON with formatting
        try:
            formatted_json = json.dumps(self.subreddits_data, indent=2)
            json_text.insert("0.0", formatted_json)
        except Exception as e:
            json_text.insert("0.0", f"Error loading JSON: {str(e)}")
        
        button_frame = ctk.CTkFrame(editor)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def save_subreddits():
            try:
                new_json_text = json_text.get("0.0", "end-1c").strip()
                new_data = json.loads(new_json_text)
                
                # Validate structure
                if 'categories' not in new_data:
                    raise ValueError("JSON must contain 'categories' key")
                
                self.subreddits_data = new_data
                self._extract_subreddit_list()
                self.save_subreddits()
                
                # Update dropdown
                self.refresh_subreddits()
                
                self.debug_log(f"Subreddits JSON edited - now have {len(self.all_subreddits_list)} subreddits")
                editor.destroy()
                messagebox.showinfo("Success", f"Saved subreddits data. Total: {len(self.all_subreddits_list)} subreddits.")
                
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Invalid JSON format:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save subreddits:\n{str(e)}")
            
        def validate_json():
            try:
                json_content = json_text.get("0.0", "end-1c").strip()
                json.loads(json_content)
                messagebox.showinfo("Valid", "JSON structure is valid!")
            except json.JSONDecodeError as e:
                messagebox.showerror("Invalid JSON", f"JSON validation failed:\n{str(e)}")
            
        ctk.CTkButton(button_frame, text="Validate JSON", command=validate_json).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Save", command=save_subreddits).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=editor.destroy).pack(side="left", padx=5)
        
    def add_subreddits(self):
        """Add new subreddits dialog"""
        dialog = ctk.CTkInputDialog(text="Enter new subreddits (separated by commas, no r/ prefix):", title="Add Subreddits")
        new_subreddits = dialog.get_input()
        
        if new_subreddits:
            subreddits_to_add = [s.strip().replace('r/', '') for s in new_subreddits.split(",") if s.strip()]
            
            # Add to 'core_business' category by default
            if 'categories' in self.subreddits_data and 'core_business' in self.subreddits_data['categories']:
                before_count = len(self.all_subreddits_list)
                self.subreddits_data['categories']['core_business']['subreddits'].extend(subreddits_to_add)
                self._extract_subreddit_list()  # Refresh the flat list
                after_count = len(self.all_subreddits_list)
                
                self.save_subreddits()
                self.refresh_subreddits()
                
                added_count = after_count - before_count
                self.debug_log(f"Added {added_count} new subreddits to core_business category")
                messagebox.showinfo("Success", f"Added {added_count} new subreddits. Total: {after_count}")
            else:
                messagebox.showerror("Error", "Could not find core_business category in subreddits data.")
                
    def view_subreddit_categories(self):
        """Show subreddit categories in a viewer window"""
        viewer = ctk.CTkToplevel(self.root)
        viewer.title("Subreddit Categories")
        viewer.geometry("700x500")
        viewer.transient(self.root)
        
        # Create scrollable text area
        text_area = ctk.CTkTextbox(viewer, width=650, height=400)
        text_area.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Display categories
        display_text = "=== SUBREDDIT CATEGORIES ===\n\n"
        
        if 'categories' in self.subreddits_data:
            for category_name, category_data in self.subreddits_data['categories'].items():
                display_text += f"{category_name.upper().replace('_', ' ')}:\n"
                if 'description' in category_data:
                    display_text += f"Description: {category_data['description']}\n"
                if 'subreddits' in category_data:
                    display_text += f"Count: {len(category_data['subreddits'])}\n"
                    for subreddit in category_data['subreddits']:
                        display_text += f"  • r/{subreddit}\n"
                display_text += "\n" + "="*50 + "\n\n"
        
        display_text += f"TOTAL SUBREDDITS: {len(self.all_subreddits_list)}\n"
        display_text += f"TOTAL CATEGORIES: {len(self.subreddits_data.get('categories', {}))}"
        
        text_area.insert("0.0", display_text)
        text_area.configure(state="disabled")
        
        ctk.CTkButton(viewer, text="Close", command=viewer.destroy).pack(pady=10)
        
    def reset_subreddits(self):
        """Reset subreddits to default structure"""
        if messagebox.askyesno("Confirm Reset", "Reset all subreddits to default structure?"):
            self.load_subreddits()  # Reload defaults
            self.refresh_subreddits()
            messagebox.showinfo("Success", "Subreddits reset to default structure.")
            
    def export_csv(self):
        """Export results to CSV with file dialog"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"reddit_results_{timestamp}.csv"
            
            # Ask user where to save and what to name it
            filepath = filedialog.asksaveasfilename(
                title="Save CSV Export",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if not filepath:  # User cancelled
                return
                
            # Define the specific columns we want to export
            fieldnames = ['Score', 'Title', 'Subreddit', 'Author', 'Upvotes', 'Comments', 'URL', 'Content']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for post in self.search_results:
                    # Create a filtered dictionary with only the columns we want
                    filtered_item = {
                        'Score': post.get('score', 0),
                        'Title': post.get('title', ''),
                        'Subreddit': f"r/{post.get('subreddit', '')}",
                        'Author': post.get('author', ''),
                        'Upvotes': post.get('upvotes', 0),
                        'Comments': post.get('comments', 0),
                        'URL': post.get('url', ''),
                        'Content': post.get('content', '')
                    }
                    writer.writerow(filtered_item)
                    
            self.debug_log(f"Exported {len(self.search_results)} results to CSV: {filepath}")
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export CSV: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Export Error", error_msg)
            
    def export_markdown(self):
        """Export results to Markdown with file dialog"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"reddit_results_{timestamp}.md"
            
            # Ask user where to save and what to name it
            filepath = filedialog.asksaveasfilename(
                title="Save Markdown Export",
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if not filepath:  # User cancelled
                return
                
            with open(filepath, 'w', encoding='utf-8') as mdfile:
                mdfile.write("# Reddit Helper Helper Results\n\n")
                mdfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                mdfile.write(f"Search Scope: {self.scope_dropdown.get()}\n\n")
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
                    
            self.debug_log(f"Exported {len(self.search_results)} results to Markdown: {filepath}")
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export Markdown: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Export Error", error_msg)
            
    def show_about(self):
        """Show about dialog"""
        about_text = """Reddit Helper Helper v3.0

A tool to find Reddit posts where people might need Diamond Lane Digital to the rescue.

NEW IN V3.0:
• JSON-based subreddit management
• Scope selector (All Reddit, All Our Subreddits, Individual)
• Categorized subreddit organization  
• Enhanced search algorithms
• Better duplicate detection

Features:
• JSON subreddit categories with 58+ business subreddits
• Three search scopes: Site-wide, All Subreddits, Individual
• Custom or default keyword searching
• Multiple view modes (Table, List, Card)
• Export to CSV and Markdown
• Real-time debug console
• Memory cache management
• Light/Dark theme support

Created with CustomTkinter"""
        
        messagebox.showinfo("About Reddit Helper Helper", about_text)
        
    def show_help(self):
        """Show help window"""
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("700x600")
        help_window.transient(self.root)
        
        help_text = """REDDIT HELPER HELPER v3.0 - USER GUIDE

GETTING STARTED:
1. Select your search scope from the dropdown
2. Enter custom keywords or leave empty for defaults
3. Click "Search Reddit" to start
4. View results in Table, List, or Card format

SEARCH SCOPES:
• All Reddit: Site-wide search across all of Reddit
• All Our Subreddits: Search all 58+ business subreddits from JSON
• Individual Subreddits: Search one specific subreddit (r/entrepreneur, etc.)

KEYWORDS:
• Empty search box = uses default business problem keywords
• Custom keywords = overrides defaults (comma separated)
• Edit/add keywords through Keywords menu

SUBREDDIT MANAGEMENT:
• Subreddits stored in categorized JSON structure
• Edit through Subreddits menu
• Categories: Core Business, Marketing, Tech, etc.
• Auto-updates dropdown when JSON changes

SCORING SYSTEM:
Posts scored based on:
• Keyword matches (primary factor)
• Engagement (upvotes and comments)
• Problem indicators ("help", "need", "struggling", etc.)
• Multiple keyword bonuses

VIEW MODES:
• Table: Sortable columns with key data
• List: Detailed text format with previews
• Card: Visual cards with full content

EXPORTING:
• CSV: For spreadsheet analysis with all data
• Markdown: For documentation with formatting

DEBUG CONSOLE:
• Real-time search logging
• Connection testing
• Data structure viewing
• Error troubleshooting

CACHE MANAGEMENT:
• Clear Results: Clears current search display
• Clear Cache: Clears memory cache completely

TIPS:
• Higher scored posts = more likely to need solutions
• Use "All Reddit" for broader discovery
• Use individual subreddits for focused searches
• Check Debug Console if searches aren't working
• Subreddit categories help organize target markets"""
        
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