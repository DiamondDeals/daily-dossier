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
        self.cache_data = {}  # Memory cache
        self.current_view = "table"
        self.is_searching = False
        self.search_mode = "scrape"  # "scrape" or "api"
        
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
        self.debug_log(f"Search mode: {self.search_mode}")
        
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
        ctk.CTkButton(self.menu_frame, text="Debug", width=60, command=self.show_debug_window).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkButton(self.menu_frame, text="Help", width=60, command=self.help_menu).grid(row=0, column=5, padx=5, pady=5)
        
        # Search mode toggle
        self.mode_label = ctk.CTkLabel(self.menu_frame, text="Mode:")
        self.mode_label.grid(row=0, column=6, padx=5, pady=5)
        
        self.mode_switch = ctk.CTkSwitch(self.menu_frame, text="Scrape", command=self.toggle_search_mode)
        self.mode_switch.grid(row=0, column=7, padx=5, pady=5)
        self.mode_switch.select()  # Default to scrape mode
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(self.menu_frame, text="🌙 Dark", width=80, command=self.toggle_theme)
        self.theme_button.grid(row=0, column=8, padx=5, pady=5, sticky="e")
        
    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar_frame = ctk.CTkFrame(self.root, height=60)
        self.toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.toolbar_frame.grid_columnconfigure(3, weight=1)
        
        # Search controls
        ctk.CTkLabel(self.toolbar_frame, text="Additional Keywords:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ctk.CTkEntry(self.toolbar_frame, width=300, placeholder_text="Enter extra search terms...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Search button
        self.search_button = ctk.CTkButton(self.toolbar_frame, text="🔍 Search Reddit", command=self.start_search, width=120)
        self.search_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Stop button
        self.stop_button = ctk.CTkButton(self.toolbar_frame, text="⏹ Stop", command=self.stop_search_func, state="disabled", width=80)
        self.stop_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Clear buttons
        ctk.CTkButton(self.toolbar_frame, text="🗑 Clear Results", command=self.clear_results, width=120).grid(row=0, column=6, padx=5, pady=5)
        ctk.CTkButton(self.toolbar_frame, text="💾 Clear Cache", command=self.clear_cache, width=100).grid(row=0, column=7, padx=5, pady=5)
        
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
        self.tree.column("Subreddit", width=100)
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
        """Main search function - prioritizes scraping over API"""
        try:
            additional_keywords = self.search_entry.get().strip()
            
            # Combine keywords
            search_keywords = self.keywords.copy()
            if additional_keywords:
                new_keywords = [k.strip() for k in additional_keywords.split(',')]
                search_keywords.extend(new_keywords)
                self.debug_log(f"Added {len(new_keywords)} additional keywords")
            
            self.debug_log(f"Total keywords to search: {len(search_keywords)}")
            
            if self.search_mode == "scrape":
                self.debug_log("Primary: HTML Scraping")
                posts = self.scrape_reddit_posts(search_keywords)
                
                # API fallback (commented out for now)
                # if not posts:
                #     self.debug_log("Scraping failed, trying API...")
                #     posts = self.search_reddit_api(search_keywords)
                    
            else:
                self.debug_log("Primary: Reddit API")
                # API search (commented out for now)
                # posts = self.search_reddit_api(search_keywords)
                posts = []
                
                # Scraping fallback
                if not posts:
                    self.debug_log("API failed, trying scraping...")
                    posts = self.scrape_reddit_posts(search_keywords)
            
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
                        if len(self.search_results) % 5 == 0:
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
            
    def scrape_reddit_posts(self, keywords):
        """Scrape Reddit posts using JSON API + HTML fallback - IMPROVED VERSION"""
        posts = []
        seen_urls = set()  # Track URLs to prevent duplicates
        seen_titles = set()  # Track titles to prevent duplicates
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
            }
            
            # Search popular subreddits for business problems
            subreddits = [
                # Core business subreddits
                'entrepreneur', 'smallbusiness', 'freelance', 'productivity', 'business', 'startups',
                # Extended business subreddits
                'solopreneur', 'consulting', 'marketing', 'sales', 'ecommerce', 'digitalnomad',
                'remotework', 'SaaS', 'webdev', 'programming', 'getmotivated', 'juststart',
                # Problem-focused subreddits
                'sysadmin', 'msp', 'it', 'excel', 'automation', 'workflow', 'organization',
                'projectmanagement', 'agency', 'customerservice', 'crm', 'accounting',
                # Industry-specific subreddits
                'realestate', 'insurance', 'legaladvice', 'nonprofit', 'restaurantowners',
                'retailowners', 'healthcare', 'fitness', 'personaltraining', 'coaching'
            ]
            sort_methods = ['new', 'hot', 'rising']  # Added 'rising' for more variety
            
            total_checks = len(subreddits) * len(sort_methods) * 3  # 3 pages per combination
            current_check = 0
            
            for subreddit in subreddits:
                if self.stop_search:
                    break
                    
                for sort_method in sort_methods:
                    if self.stop_search:
                        break
                        
                    current_check += 1
                    progress = min(current_check / total_checks, 0.95)  # Cap at 95% until complete
                    self.root.after(0, lambda p=progress: self.progress_bar.set(p))

                    
                    # Try JSON API first (more reliable)
                    json_url = f"https://old.reddit.com/r/{subreddit}/{sort_method}/.json?limit=100"  # Changed from 25 to 100
                    html_url = f"https://www.reddit.com/r/{subreddit}/{sort_method}/"

                    
                    self.debug_log(f"Trying JSON API: {json_url}")
                    self.root.after(0, lambda: self.update_status(f"JSON API: r/{subreddit} {sort_method}..."))
                    
                    try:
                        # Try JSON API first
                        response = requests.get(json_url, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                json_posts = self.extract_from_json(data, keywords, seen_titles, seen_urls)
                                posts.extend(json_posts)
                                self.debug_log(f"✓ JSON API success: {len(json_posts)} relevant posts from r/{subreddit}")
                                
                                # If JSON worked, skip HTML scraping for this URL
                                if json_posts:
                                    time.sleep(0.3)  # Be respectful
                                    continue
                                    
                            except json.JSONDecodeError as e:
                                self.debug_log(f"JSON parse error: {str(e)}")
                        else:
                            self.debug_log(f"JSON API failed with status: {response.status_code}")
                            
                    except Exception as e:
                        self.debug_log(f"JSON API error: {str(e)}")
                    
                    # Fallback to HTML scraping if JSON failed
                    self.debug_log(f"Fallback to HTML scraping: {html_url}")
                    self.root.after(0, lambda: self.update_status(f"HTML Scraping: r/{subreddit} {sort_method}..."))
                    
                    try:
                        response = requests.get(html_url, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            
                            # Extract posts using improved selectors
                            post_elements = self.find_post_elements_improved(soup)
                            self.debug_log(f"HTML: Found {len(post_elements)} post elements")
                            
                            posts_found_this_page = 0
                            
                            for post_elem in post_elements:
                                if self.stop_search:
                                    break
                                    
                                post_data = self.extract_post_data_improved(post_elem)
                                
                                if post_data:
                                    # Check for duplicates
                                    title_key = post_data['title'].lower().strip()
                                    url_key = post_data['url'].lower().strip()
                                    
                                    if title_key not in seen_titles and url_key not in seen_urls:
                                        if self.is_relevant_post(post_data, keywords):
                                            posts.append(post_data)
                                            seen_titles.add(title_key)
                                            seen_urls.add(url_key)
                                            posts_found_this_page += 1
                                            self.debug_log(f"HTML: Found relevant post: {post_data['title'][:50]}...")
                                    else:
                                        self.debug_log(f"Skipping duplicate: {post_data['title'][:30]}...")
                                        
                            self.debug_log(f"HTML: Added {posts_found_this_page} new posts from this page")
                            
                        else:
                            self.debug_log(f"HTML request failed: {response.status_code}")
                            
                    except Exception as e:
                        self.debug_log(f"HTML scraping error: {str(e)}")
                        
                    # Small delay to be respectful
                    time.sleep(0.8)
                    
        except Exception as e:
            self.debug_log(f"Overall scraping error: {str(e)}")
            
        self.debug_log(f"Scraping complete. Found {len(posts)} unique relevant posts.")
        return posts
    
    def extract_from_json(self, data, keywords, seen_titles, seen_urls):
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
                            'subreddit': post.get('subreddit', ''),
                            'upvotes': post.get('ups', 0),
                            'comments': post.get('num_comments', 0),
                            'url': f"https://www.reddit.com{post.get('permalink', '')}",
                            'score': 0,
                            'source': 'json'  # ADD THIS LINE
                        }

                        
                        # Check for duplicates
                        title_key = title.lower().strip()
                        url_key = post_info['url'].lower().strip()
                        
                        if title_key not in seen_titles and url_key not in seen_urls:
                            if self.is_relevant_post(post_info, keywords):
                                posts.append(post_info)
                                seen_titles.add(title_key)
                                seen_urls.add(url_key)
                                self.debug_log(f"JSON: Added post: {title[:50]}...")
                                
        except Exception as e:
            self.debug_log(f"Error parsing JSON: {str(e)}")
            
        return posts

    def find_post_elements_improved(self, soup):
        """Find post elements using updated selectors for current Reddit"""
        post_elements = []
        
        # Updated selectors for current Reddit structure
        selectors = [
            'shreddit-post:not([data-testid*="promoted"])',  # Current Reddit posts, exclude ads
            'article[data-testid="post-container"]',  # Alternative current structure
            'div[data-testid="post-container"]',  # Another alternative
            'div[slot="post-media-container"]',  # Media posts
            '[data-post-click-location="background"]',  # Click target areas
            'div[tabindex="-1"]:has(h3)',  # Elements with h3 children (likely posts)
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                # Filter out sidebar elements
                filtered_elements = []
                
                for elem in elements:
                    text_content = elem.get_text(strip=True)
                    if not self.is_sidebar_content(text_content):
                        filtered_elements.append(elem)
                
                # Must find actual posts (between 3 and 50)
                if 3 <= len(filtered_elements) <= 100:  # Changed from 50 to 100
                    self.debug_log(f"✓ Using selector: {selector} (found {len(filtered_elements)} valid posts)")
                    post_elements = filtered_elements
                    break
                elif filtered_elements:
                    self.debug_log(f"Selector {selector}: found {len(filtered_elements)} elements (outside valid range)")
            except Exception as e:
                self.debug_log(f"Error with selector {selector}: {str(e)}")
                
        # Fallback: look for any divs containing Reddit comment links
        if not post_elements or len(post_elements) < 3:
            self.debug_log("Using fallback method: searching for post links")
            all_divs = soup.find_all('div')
            potential_posts = []
            
            for div in all_divs:
                # Look for divs containing Reddit comment links
                links = div.find_all('a', href=re.compile(r'/r/.+/comments/'))
                if links and not self.is_sidebar_content(div.get_text(strip=True)):
                    potential_posts.append(div)
                    
            if potential_posts:
                self.debug_log(f"Fallback found {len(potential_posts)} potential posts")
                post_elements = potential_posts[:50]  # Changed from 25 to 50

                
        return post_elements

    def is_sidebar_content(self, text):
        """Check if text is from sidebar/navigation"""
        sidebar_indicators = [
            "TOPICS", "RESOURCES", "Internet Culture", "Games", "Q&As", 
            "Technology", "Pop Culture", "Movies & TV", "No hiring",
            "Post only questions", "No blog links", "No advertising",
            "No direct sales", "Relevant Content Only", "Feedback Has a Place",
            "Always Be Kind", "No Unscheduled AMAs", "Follow reddiquette",
            "Be Civil and Stay Positive", "No Listicles", "No NSFW Content"
        ]
        return any(indicator in text for indicator in sidebar_indicators)

    def extract_post_data_improved(self, post_elem):
        """Extract post data from HTML element - IMPROVED VERSION"""
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
            
            # Extract title with improved selectors
            title_text = self.extract_title_improved(post_elem)
            if not title_text:
                return None
                
            post_data['title'] = title_text
            
            # Extract content
            post_data['content'] = self.extract_content(post_elem)
            
            # Extract metadata
            self.extract_metadata_improved(post_elem, post_data)
            
            # Validate that we have minimum required data
            if not post_data['title'] or len(post_data['title']) < 10:
                return None
                
            # Generate URL if not found
            if not post_data['url']:
                post_data['url'] = self.generate_reddit_url(post_data)
                
            return post_data
            
        except Exception as e:
            self.debug_log(f"Error extracting post data: {str(e)}")
            return None

    def extract_title_improved(self, post_elem):
        """Extract title with current Reddit structure"""
        title_selectors = [
            'h3[slot="title"]',  # Current Reddit title slot
            'a[slot="full-post-link"] h3',  # Title within link
            '[data-testid="post-content"] h3',  # Content area title
            'shreddit-post-title',  # Post title element
            'h3 a',  # H3 with link inside
            'h3',  # Generic h3 fallback
            'a[data-testid="post-title"]',
            'a[href*="/comments/"]',
        ]
        
        for selector in title_selectors:
            try:
                title_elem = post_elem.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    # Validate it's actually a post title
                    if (title_text and 
                        20 <= len(title_text) <= 300 and  # Reasonable title length
                        not self.is_sidebar_content(title_text)):  # Not sidebar content
                        return title_text
            except:
                continue
        return None

    def test_specific_subreddit(self):
        """Test scraping a specific subreddit - ADD TO DEBUG MENU"""
        self.debug_log("=== Testing Specific Subreddit ===")
        url = "https://old.reddit.com/r/entrepreneur/new/.json?limit=5"
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RedditScraper/1.0)',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            self.debug_log(f"Test URL: {url}")
            self.debug_log(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data['data']['children']
                self.debug_log(f"✓ Found {len(posts)} posts")
                
                for i, post in enumerate(posts[:3]):
                    title = post['data'].get('title', 'No title')
                    author = post['data'].get('author', 'No author')
                    subreddit = post['data'].get('subreddit', 'No subreddit')
                    self.debug_log(f"Post {i+1}: {title[:50]}... (by u/{author} in r/{subreddit})")
                    
                self.debug_log("✓ Connection test successful!")
            else:
                self.debug_log(f"✗ Failed with status: {response.status_code}")
                
        except Exception as e:
            self.debug_log(f"✗ Test failed: {str(e)}")

    def test_json_vs_html(self):
        """Compare JSON vs HTML scraping - ADD TO DEBUG MENU"""
        self.debug_log("=== JSON vs HTML Comparison ===")
        
        # Test JSON
        json_url = "https://old.reddit.com/r/entrepreneur/new/.json?limit=3"
        html_url = "https://www.reddit.com/r/entrepreneur/new/"
        
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; RedditScraper/1.0)'}
        
        try:
            # JSON Test
            self.debug_log("Testing JSON API...")
            json_response = requests.get(json_url, headers=headers, timeout=10)
            if json_response.status_code == 200:
                json_data = json_response.json()
                json_posts = len(json_data['data']['children'])
                self.debug_log(f"✓ JSON: Found {json_posts} posts")
            else:
                self.debug_log(f"✗ JSON failed: {json_response.status_code}")
                
            # HTML Test
            self.debug_log("Testing HTML scraping...")
            html_response = requests.get(html_url, headers=headers, timeout=10)
            if html_response.status_code == 200:
                soup = BeautifulSoup(html_response.content, 'html.parser')
                post_elements = self.find_post_elements_improved(soup)
                self.debug_log(f"✓ HTML: Found {len(post_elements)} post elements")
            else:
                self.debug_log(f"✗ HTML failed: {html_response.status_code}")
                
        except Exception as e:
            self.debug_log(f"✗ Comparison test failed: {str(e)}")
        
        
    def find_post_elements(self, soup):
        """Find post elements using updated selectors for current Reddit"""
        post_elements = []
        
        # Updated selectors for current Reddit structure
        selectors = [
            'shreddit-post:not([data-testid*="promoted"])',  # Current Reddit posts, exclude ads
            'article[data-testid="post-container"]',  # Alternative current structure
            'div[data-testid="post-container"]',  # Another alternative
            'div[slot="post-media-container"]',  # Media posts
            '[data-post-click-location="background"]',  # Click target areas
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            # Must find actual posts (more than 5, less than 100)
            if 5 <= len(elements) <= 100:
                self.debug_log(f"✓ Using selector: {selector} (found {len(elements)} posts)")
                post_elements = elements
                break
            elif elements:
                self.debug_log(f"Selector {selector}: found {len(elements)} elements (wrong range)")
                
        # Fallback: look for any divs containing Reddit post links
        if not post_elements or len(post_elements) < 5:
            self.debug_log("Using fallback method: searching for post links")
            all_divs = soup.find_all('div')
            potential_posts = []
            
            for div in all_divs:
                # Look for divs containing Reddit comment links
                links = div.find_all('a', href=re.compile(r'/r/.+/comments/'))
                if links:
                    potential_posts.append(div)
                    
            if potential_posts:
                self.debug_log(f"Fallback found {len(potential_posts)} potential posts")
                post_elements = potential_posts[:50]  # Changed from 25 to 50
                
        # Alternative fallback: look for h3 elements (often post titles)
        if not post_elements or len(post_elements) < 3:
            self.debug_log("Using h3 fallback method")
            h3_elements = soup.find_all('h3')
            post_containers = []
            
            for h3 in h3_elements:
                # Find the parent container of each h3 (likely the post container)
                parent = h3.find_parent()
                if parent and parent not in post_containers:
                    post_containers.append(parent)
                    
            if post_containers:
                self.debug_log(f"H3 fallback found {len(post_containers)} post containers")
                post_elements = post_containers
                
        return post_elements[:50]  # Limit to 50 posts max

    def debug_post_structure(self, post_elem, index=0):
        """Debug what's actually inside a post element"""
        try:
            self.debug_log(f"=== DEBUG POST {index} STRUCTURE ===")
            
            # Show the element tag and some attributes
            self.debug_log(f"Element tag: {post_elem.name}")
            self.debug_log(f"Element classes: {post_elem.get('class', [])}")
            
            # Look for any text content
            text_content = post_elem.get_text(strip=True)
            if text_content:
                self.debug_log(f"Text content (first 200 chars): {text_content[:200]}")
            else:
                self.debug_log("No text content found")
                
            # Look for links
            links = post_elem.find_all('a')
            self.debug_log(f"Found {len(links)} links:")
            for i, link in enumerate(links[:5]):  # Show first 5 links
                href = link.get('href', '')
                text = link.get_text(strip=True)
                self.debug_log(f"  Link {i+1}: href='{href}' text='{text[:50]}'")
                
            # Look for headings
            headings = post_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            self.debug_log(f"Found {len(headings)} headings:")
            for i, heading in enumerate(headings):
                self.debug_log(f"  {heading.name}: '{heading.get_text(strip=True)[:100]}'")
                
            # Look for specific attributes that might indicate post data
            for attr in ['data-testid', 'data-click-id', 'slot']:
                elements_with_attr = post_elem.find_all(attrs={attr: True})
                if elements_with_attr:
                    self.debug_log(f"Elements with {attr}:")
                    for elem in elements_with_attr[:3]:
                        self.debug_log(f"  {elem.name}[{attr}='{elem.get(attr)}']")
                        
            self.debug_log("=== END DEBUG POST STRUCTURE ===")
            
        except Exception as e:
            self.debug_log(f"Error in debug_post_structure: {str(e)}")


    def extract_post_data(self, post_elem):
        """Extract post data from HTML element - WITH DEBUG"""
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
            
            # DEBUG: Show structure of first few posts
            if len(self.search_results) < 3:  # Only debug first 3 posts to avoid spam
                self.debug_post_structure(post_elem, len(self.search_results))
            
            # Extract title with more aggressive searching
            title_text = self.extract_title(post_elem)
            if not title_text:
                self.debug_log("No title found - skipping post")
                return None
                
            post_data['title'] = title_text
            self.debug_log(f"Extracted title: '{title_text[:50]}...'")
            
            # Extract content
            post_data['content'] = self.extract_content(post_elem)
            if post_data['content']:
                self.debug_log(f"Extracted content: '{post_data['content'][:50]}...'")
            
            # Extract metadata
            self.extract_metadata_improved(post_elem, post_data)
            self.debug_log(f"Extracted metadata - author: '{post_data['author']}', subreddit: '{post_data['subreddit']}', url: '{post_data['url'][:50]}...'")
            
            # Validate that we have minimum required data
            if not post_data['title'] or len(post_data['title']) < 10:
                self.debug_log("Post failed validation - title too short")
                return None
                
            # Generate URL if not found
            if not post_data['url']:
                post_data['url'] = self.generate_reddit_url(post_data)
                self.debug_log(f"Generated URL: {post_data['url']}")
                
            self.debug_log(f"Successfully extracted post: '{post_data['title'][:30]}...'")
            return post_data
            
        except Exception as e:
            self.debug_log(f"Error extracting post data: {str(e)}")
            return None
        
    def extract_content(self, post_elem):
        """Extract post content/body text"""
        content_selectors = [
            'div[data-testid="post-content"]',
            'div[class*="usertext-body"]',
            'div[class*="content"]',
            'div[class*="text"]',
            'p',
            '[slot="text-body"]'
        ]
        
        for selector in content_selectors:
            try:
                content_elem = post_elem.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text(strip=True)
                    if content_text and len(content_text) > 20:
                        return content_text[:1000]  # Limit content length
            except:
                continue
                
        return ""
    
    def extract_metadata_improved(self, post_elem, post_data):
        """Extract author, subreddit, votes, etc. - IMPROVED VERSION"""
        try:
            # Extract author with multiple methods
            author_selectors = [
                'a[href*="/user/"]',
                'a[href*="/u/"]',
                '[class*="author"]',
                'faceplate-tracker[source="user"]',
                'a[data-testid="post-title"]'
            ]
            
            for selector in author_selectors:
                try:
                    author_elem = post_elem.select_one(selector)
                    if author_elem:
                        author_text = author_elem.get_text(strip=True)
                        if author_text and not author_text.startswith('r/') and len(author_text) < 50:
                            clean_author = author_text.replace('u/', '').replace('/u/', '').replace('by ', '')
                            if clean_author and not clean_author.startswith('http'):
                                post_data['author'] = clean_author
                                break
                except:
                    continue
                    
            # Extract subreddit with multiple methods
            subreddit_selectors = [
                'a[href*="/r/"]',
                '[class*="subreddit"]',
                'faceplate-tracker[source="subreddit"]'
            ]
            
            for selector in subreddit_selectors:
                try:
                    subreddit_elem = post_elem.select_one(selector)
                    if subreddit_elem:
                        subreddit_text = subreddit_elem.get_text(strip=True)
                        if subreddit_text and subreddit_text.startswith('r/'):
                            post_data['subreddit'] = subreddit_text.replace('r/', '')
                            break
                        elif subreddit_text and not subreddit_text.startswith('http'):
                            # Sometimes subreddit doesn't have r/ prefix
                            post_data['subreddit'] = subreddit_text
                            break
                except:
                    continue
                    
            # Extract URL with multiple methods
            url_selectors = [
                'a[href*="/comments/"]',
                'a[data-click-id="body"]',
                'a[data-testid="post-title"]'
            ]
            
            for selector in url_selectors:
                try:
                    url_elem = post_elem.select_one(selector)
                    if url_elem:
                        href = url_elem.get('href', '')
                        if '/comments/' in href:
                            if href.startswith('/'):
                                post_data['url'] = f"https://www.reddit.com{href}"
                            elif href.startswith('http'):
                                post_data['url'] = href
                            break
                except:
                    continue
                    
            # Extract vote counts and comments with improved regex
            self.extract_numbers(post_elem, post_data)
            
        except Exception as e:
            self.debug_log(f"Error in extract_metadata_improved: {str(e)}")

    def extract_numbers(self, post_elem, post_data):
        """Extract upvotes and comment counts"""
        try:
            # Look for vote buttons and comment links
            vote_patterns = [
                r'(\d+)\s*upvote',
                r'(\d+)\s*point',
                r'(\d+)\s*karma'
            ]
            
            comment_patterns = [
                r'(\d+)\s*comment',
                r'(\d+)\s*replies'
            ]
            
            # Get all text from the element
            full_text = post_elem.get_text()
            
            # Extract upvotes
            for pattern in vote_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    post_data['upvotes'] = int(match.group(1))
                    break
                    
            # Extract comments
            for pattern in comment_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    post_data['comments'] = int(match.group(1))
                    break
                    
            # Fallback: look for any numbers in specific elements
            if post_data['upvotes'] == 0 or post_data['comments'] == 0:
                # Look for button elements or spans with numbers
                number_elements = post_elem.find_all(['button', 'span', 'div'], string=re.compile(r'\d+'))
                numbers = []
                
                for elem in number_elements:
                    try:
                        text = elem.get_text(strip=True)
                        match = re.search(r'(\d+)', text)
                        if match:
                            num = int(match.group(1))
                            if 0 <= num <= 100000:  # Reasonable range
                                numbers.append(num)
                    except:
                        continue
                        
                # Assign numbers if we found any
                if numbers and post_data['upvotes'] == 0:
                    post_data['upvotes'] = numbers[0]
                if len(numbers) > 1 and post_data['comments'] == 0:
                    post_data['comments'] = numbers[1]
                    
        except Exception as e:
            self.debug_log(f"Error extracting numbers: {str(e)}")

    def generate_reddit_url(self, post_data):
        """Generate Reddit URL if not found"""
        if post_data['subreddit'] and post_data['title']:
            # Create a simple URL (won't be perfect but better than nothing)
            title_slug = re.sub(r'[^a-zA-Z0-9\s]', '', post_data['title'])
            title_slug = '_'.join(title_slug.split()[:5])  # Use first 5 words
            return f"https://www.reddit.com/r/{post_data['subreddit']}/comments/{title_slug}/"
        return "https://www.reddit.com"
    
    def extract_title(self, post_elem):
        """Extract title with current Reddit structure"""
        title_selectors = [
            'h3[slot="title"]',  # Current Reddit title slot
            'a[slot="full-post-link"] h3',  # Title within link
            '[data-testid="post-content"] h3',  # Content area title
            'shreddit-post-title',  # Post title element
            'h3',  # Generic h3 fallback
        ]
        
        for selector in title_selectors:
            try:
                title_elem = post_elem.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    # Validate it's actually a post title
                    if (title_text and 
                        20 <= len(title_text) <= 300 and  # Reasonable title length
                        not self.is_sidebar_content(title_text)):  # Not sidebar content
                        return title_text
            except:
                continue
        return None

    def is_sidebar_content(self, text):
        """Check if text is from sidebar/navigation"""
        sidebar_indicators = [
            "TOPICS", "RESOURCES", "Internet Culture", "Games", "Q&As", 
            "Technology", "Pop Culture", "Movies & TV", "No hiring",
            "Post only questions", "No blog links", "No advertising"
        ]
        return any(indicator in text for indicator in sidebar_indicators)


            
    def extract_metadata(self, post_elem, post_data):
        """Extract author, subreddit, votes, etc."""
        try:
            # Extract author
            author_selectors = ['a[href*="/user/"]', 'a[href*="/u/"]', '[class*="author"]']
            for selector in author_selectors:
                author_elem = post_elem.select_one(selector)
                if author_elem:
                    author_text = author_elem.get_text(strip=True)
                    if author_text and not author_text.startswith('r/'):
                        post_data['author'] = author_text.replace('u/', '').replace('/u/', '')
                        break
                        
            # Extract subreddit
            subreddit_selectors = ['a[href*="/r/"]', '[class*="subreddit"]']
            for selector in subreddit_selectors:
                subreddit_elem = post_elem.select_one(selector)
                if subreddit_elem:
                    subreddit_text = subreddit_elem.get_text(strip=True)
                    if subreddit_text and subreddit_text.startswith('r/'):
                        post_data['subreddit'] = subreddit_text.replace('r/', '')
                        break
                        
            # Extract URL
            url_selectors = ['a[href*="/comments/"]', 'a[data-click-id="body"]']
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
                        
            # Extract vote counts and comments
            vote_elements = post_elem.find_all(string=re.compile(r'\d+'))
            numbers = []
            for elem in vote_elements:
                try:
                    num = int(re.search(r'\d+', elem).group())
                    numbers.append(num)
                except:
                    continue
                    
            if numbers:
                post_data['upvotes'] = numbers[0] if len(numbers) > 0 else 0
                post_data['comments'] = numbers[1] if len(numbers) > 1 else 0
                
        except Exception as e:
            self.debug_log(f"Error extracting metadata: {str(e)}")
            
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
                
        if score > 0:
            self.debug_log(f"Post scored {score}: '{post['title'][:50]}...' (matched: {len(matched_keywords)} keywords)")
            
        return score
        
    # API SEARCH FUNCTIONS (COMMENTED OUT - READY TO UNCOMMENT WHEN NEEDED)
    """
    def search_reddit_api(self, keywords):
        '''Search Reddit using JSON API - CURRENTLY DISABLED'''
        posts = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Build search query
            search_terms = keywords[:10]  # Use first 10 keywords
            search_query = " AND ".join([f'"{term}"' for term in search_terms])
            
            search_url = f"https://www.reddit.com/search.json?q={quote(search_query)}&sort=new&limit=100"
            
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
                        
                        if post_info['title']:
                            posts.append(post_info)
                            
                except json.JSONDecodeError as e:
                    self.debug_log(f"Failed to parse API response: {str(e)}")
                    return []
                    
            else:
                self.debug_log(f"API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            self.debug_log(f"API search error: {str(e)}")
            return []
            
        return posts
    """
        
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
            
            # Control buttons frame (UPDATE THIS SECTION)
            button_frame = ctk.CTkFrame(self.debug_window)
            button_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkButton(button_frame, text="Clear Log", command=self.clear_debug_log).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Test Connection", command=self.test_reddit_connection).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Test Subreddit", command=self.test_specific_subreddit).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="JSON vs HTML", command=self.test_json_vs_html).pack(side="left", padx=5)
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
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
    def keywords_menu(self):
        """Keywords menu options"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Keywords", command=self.edit_keywords)
        menu.add_command(label="Add Keywords", command=self.add_keywords)
        menu.add_command(label="Reset to Defaults", command=self.reset_keywords)
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
            
    def export_csv(self):
        """Export results to CSV - FIXED VERSION"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_results_{timestamp}.csv"
            filepath = os.path.join(self.exports_folder, filename)
            
            # Define the specific columns we want to export
            fieldnames = ['Score', 'Title', 'Subreddit', 'Author', 'Upvotes', 'Comments', 'URL', 'Content']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for post in self.search_results:
                    # Create a filtered dictionary with only the columns we want
                    # This ensures all required fields exist and prevents KeyError
                    filtered_item = {
                        'Score': post.get('score', 0),
                        'Title': post.get('title', ''),
                        'Subreddit': post.get('subreddit', ''),
                        'Author': post.get('author', ''),
                        'Upvotes': post.get('upvotes', 0),
                        'Comments': post.get('comments', 0),
                        'URL': post.get('url', ''),
                        'Content': post.get('content', '')
                    }
                    writer.writerow(filtered_item)
                    
            self.debug_log(f"Exported {len(self.search_results)} results to CSV")
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
                    
            self.debug_log(f"Exported {len(self.search_results)} results to Markdown")
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export Markdown: {str(e)}"
            self.debug_log(error_msg)
            messagebox.showerror("Export Error", error_msg)
            
    def show_about(self):
        """Show about dialog"""
        about_text = """Reddit Helper Helper v2.0

A tool to find Reddit posts where people might need Diamond Lane Digital to the rescue.

Features:
• HTML Scraping primary, API ready for toggle
• Keyword-based business problem detection
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
        
        help_text = """REDDIT HELPER HELPER - USER GUIDE

GETTING STARTED:
1. Click "Search Reddit" to start searching with default keywords
2. Add extra keywords in the search box if needed
3. Use the Scrape/API toggle to switch search methods
4. View results in Table, List, or Card format

SEARCH MODES:
• Scrape Mode (Default): Uses HTML scraping for reliable results
• API Mode: Uses Reddit's API (ready to enable when needed)

SCORING SYSTEM:
Posts are scored based on:
• Keyword matches (primary factor)
• Engagement (upvotes and comments)
• Problem indicators ("help", "need", "struggling", etc.)

KEYWORDS:
• Edit through Keywords menu
• Add custom business problem keywords
• Reset to defaults anytime

CACHE MANAGEMENT:
• Clear Results: Clears current search display
• Clear Cache: Clears memory cache completely

EXPORTING:
• CSV: For spreadsheet analysis
• Markdown: For documentation

DEBUG CONSOLE:
• Real-time search logging
• Connection testing
• Keyword verification

TIPS:
• Higher scored posts are more likely to need solutions
• Double-click table rows to open posts
• Use Debug Console if searches aren't working
• Add specific industry keywords for better targeting"""
        
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