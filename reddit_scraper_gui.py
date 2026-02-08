#!/usr/bin/env python3
"""
Reddit Subreddit Description Scraper - Modern GUI Version
A comprehensive tool for scraping Reddit subreddit descriptions with NSFW classification.

Features:
- Modern CustomTkinter GUI with dark theme
- Real-time progress tracking and status updates
- Pause/Resume functionality with state persistence
- Auto-save at configurable intervals
- Recent results table and activity log
- Settings panel for configuration
- Export functionality (CSV format)
- Threading to prevent GUI freezing
- Proper rate limiting and error handling
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import json
import csv
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import random
from typing import Dict, List, Tuple, Optional
import queue

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Drew's preference for dark theme
ctk.set_default_color_theme("blue")

class RedditScraperGUI:
    def __init__(self):
        """Initialize the Reddit Scraper GUI application."""
        # Main window setup
        self.window = ctk.CTk()
        self.window.title("Reddit Subreddit Description Scraper v2.0")
        self.window.geometry("1400x900")
        self.window.minsize(1200, 800)
        
        # State management
        self.is_running = False
        self.is_paused = False
        self.current_thread = None
        self.start_time = None
        self.processed_count = 0
        self.total_count = 0
        self.nsfw_count = 0
        self.safe_count = 0
        self.error_count = 0
        self.consecutive_api_errors = 0
        self.max_consecutive_errors = 3
        self.last_rate_limit_time = None
        
        # Configuration
        self.config = {
            "rate_limit": 2.0,  # seconds between requests
            "auto_save_interval": 50,  # save every N processed items
            "timeout": 10,  # request timeout
            "max_retries": 3,
            "output_dir": "Exports",
            "use_reddit_api": True,  # API by default since HTML is blocked
            "batch_size": 100
        }
        
        # File paths
        self.input_file = None
        self.output_file = None
        self.progress_file = "scraper_progress.json"
        
        # Data storage
        self.results = []
        self.recent_results = []
        self.activity_log = []
        
        # Threading communication
        self.message_queue = queue.Queue()
        
        # NSFW detection patterns
        self.nsfw_indicators = {
            'explicit_content': [
                'adult content', 'nsfw', '18+', 'over 18', 'adult only', 'mature content',
                'explicit', 'pornography', 'sexual content', 'nude', 'nudity', 'xxx'
            ],
            'sexual_terms': [
                'erotic', 'fetish', 'kink', 'bdsm', 'sex', 'sexual', 'porn', 'masturbation',
                'orgasm', 'arousal', 'intimate', 'sensual', 'seduction'
            ],
            'community_markers': [
                'gonewild', 'hookup', 'dating', 'personals', 'singles', 'meet', 'chat',
                'verification required', 'must verify', 'age verification'
            ],
            'body_related': [
                'body', 'curves', 'physique', 'anatomy', 'figure', 'attractive',
                'beautiful', 'gorgeous', 'hot', 'sexy'
            ]
        }
        
        # Initialize GUI
        self.setup_gui()
        self.load_config()
        self.check_message_queue()
        
    def setup_gui(self):
        """Create the complete GUI interface."""
        # Main container with padding
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container, 
            text="Reddit Subreddit Description Scraper", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Top section - File selection and controls
        self.setup_top_section(main_container)
        
        # Middle section - Progress and status
        self.setup_middle_section(main_container)
        
        # Bottom section - Results and log
        self.setup_bottom_section(main_container)
        
    def setup_top_section(self, parent):
        """Setup the top section with file selection and controls."""
        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill="x", pady=(0, 10))
        
        # File selection row
        file_frame = ctk.CTkFrame(top_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(file_frame, text="Input File:").pack(side="left", padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ctk.CTkEntry(
            file_frame, 
            textvariable=self.file_path_var, 
            width=400,
            placeholder_text="Select CSV file containing subreddit list..."
        )
        self.file_entry.pack(side="left", padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            file_frame, 
            text="Browse", 
            command=self.browse_file,
            width=100
        )
        self.browse_btn.pack(side="left", padx=(0, 10))
        
        # Set default file if it exists
        default_file = "Subreddits/Reddit SubReddits - ALL SUBREDDITS.csv"
        if os.path.exists(default_file):
            self.file_path_var.set(default_file)
            self.input_file = default_file
        
        # Control buttons row
        control_frame = ctk.CTkFrame(top_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Left side - Start/Pause/Resume buttons
        left_controls = ctk.CTkFrame(control_frame)
        left_controls.pack(side="left", fill="x", expand=True)
        
        self.start_btn = ctk.CTkButton(
            left_controls, 
            text="Start Scraping", 
            command=self.start_scraping,
            fg_color="green",
            hover_color="darkgreen",
            width=120
        )
        self.start_btn.pack(side="left", padx=(10, 5))
        
        # Add Load Progress button
        self.load_btn = ctk.CTkButton(
            left_controls,
            text="Load Progress",
            command=self.load_progress,
            fg_color="blue",
            hover_color="darkblue",
            width=120
        )
        self.load_btn.pack(side="left", padx=(5, 5))
        
        self.pause_btn = ctk.CTkButton(
            left_controls, 
            text="Pause", 
            command=self.pause_scraping,
            fg_color="orange",
            hover_color="darkorange",
            width=120,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            left_controls, 
            text="Stop", 
            command=self.stop_scraping,
            fg_color="red",
            hover_color="darkred",
            width=120,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(5, 10))
        
        # Right side - Settings and Export buttons
        right_controls = ctk.CTkFrame(control_frame)
        right_controls.pack(side="right")
        
        self.settings_btn = ctk.CTkButton(
            right_controls, 
            text="Settings", 
            command=self.open_settings,
            width=100
        )
        self.settings_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(
            right_controls, 
            text="Export Results", 
            command=self.export_results,
            width=120
        )
        self.export_btn.pack(side="left", padx=(5, 10))
        
    def setup_middle_section(self, parent):
        """Setup the middle section with progress tracking and status."""
        middle_frame = ctk.CTkFrame(parent)
        middle_frame.pack(fill="x", pady=(0, 10))
        
        # Progress section
        progress_frame = ctk.CTkFrame(middle_frame)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        # Progress bars and counters
        left_progress = ctk.CTkFrame(progress_frame)
        left_progress.pack(side="left", fill="both", expand=True, padx=(10, 5))
        
        # Overall progress
        ctk.CTkLabel(left_progress, text="Overall Progress:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.overall_progress = ctk.CTkProgressBar(left_progress, width=300)
        self.overall_progress.pack(fill="x", padx=(0, 10), pady=(0, 5))
        self.overall_progress.set(0)
        
        self.progress_label = ctk.CTkLabel(left_progress, text="0 / 0 (0%)")
        self.progress_label.pack(anchor="w", pady=(0, 10))
        
        # Classification progress
        ctk.CTkLabel(left_progress, text="Classification Results:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        classification_frame = ctk.CTkFrame(left_progress)
        classification_frame.pack(fill="x", pady=(0, 10))
        
        self.nsfw_label = ctk.CTkLabel(classification_frame, text="NSFW: 0", text_color="red")
        self.nsfw_label.pack(side="left", padx=(10, 20))
        
        self.safe_label = ctk.CTkLabel(classification_frame, text="Safe: 0", text_color="green")
        self.safe_label.pack(side="left", padx=(0, 20))
        
        self.error_label = ctk.CTkLabel(classification_frame, text="Errors: 0", text_color="orange")
        self.error_label.pack(side="left", padx=(0, 10))
        
        # Status section
        right_status = ctk.CTkFrame(progress_frame)
        right_status.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        ctk.CTkLabel(right_status, text="Status Information:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(right_status, text="Status: Ready", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=2)
        
        self.time_label = ctk.CTkLabel(right_status, text="Elapsed: 00:00:00", anchor="w")
        self.time_label.pack(fill="x", padx=10, pady=2)
        
        self.rate_label = ctk.CTkLabel(right_status, text="Rate: 0 items/min", anchor="w")
        self.rate_label.pack(fill="x", padx=10, pady=2)
        
        self.eta_label = ctk.CTkLabel(right_status, text="ETA: --:--:--", anchor="w")
        self.eta_label.pack(fill="x", padx=10, pady=2)
        
        self.current_label = ctk.CTkLabel(right_status, text="Current: None", anchor="w")
        self.current_label.pack(fill="x", padx=10, pady=(2, 10))
        
    def setup_bottom_section(self, parent):
        """Setup the bottom section with results table and activity log."""
        bottom_frame = ctk.CTkFrame(parent)
        bottom_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(bottom_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Recent Results tab
        self.setup_results_tab()
        
        # Activity Log tab
        self.setup_activity_tab()
        
    def setup_results_tab(self):
        """Setup the recent results table tab."""
        results_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(results_frame, text="Recent Results")
        
        # Results table with scrollbar
        table_frame = ctk.CTkFrame(results_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Treeview for results
        columns = ("Subreddit", "Status", "Classification", "Confidence", "Description")
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        self.results_tree.heading("Subreddit", text="Subreddit")
        self.results_tree.heading("Status", text="Status")
        self.results_tree.heading("Classification", text="Classification")
        self.results_tree.heading("Confidence", text="Confidence")
        self.results_tree.heading("Description", text="Description Preview")
        
        self.results_tree.column("Subreddit", width=150, minwidth=100)
        self.results_tree.column("Status", width=100, minwidth=80)
        self.results_tree.column("Classification", width=100, minwidth=80)
        self.results_tree.column("Confidence", width=80, minwidth=60)
        self.results_tree.column("Description", width=400, minwidth=300)
        
        # Scrollbars for results table
        results_scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        results_scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=results_scrollbar_y.set, xscrollcommand=results_scrollbar_x.set)
        
        # Pack results table and scrollbars
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scrollbar_y.pack(side="right", fill="y")
        results_scrollbar_x.pack(side="bottom", fill="x")
        
    def setup_activity_tab(self):
        """Setup the activity log tab."""
        activity_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(activity_frame, text="Activity Log")
        
        # Activity log with scrollbar
        log_frame = ctk.CTkFrame(activity_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.activity_text = ctk.CTkTextbox(log_frame, wrap="word", height=400)
        self.activity_text.pack(fill="both", expand=True)
        
        # Log controls
        log_controls = ctk.CTkFrame(activity_frame)
        log_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        self.clear_log_btn = ctk.CTkButton(
            log_controls, 
            text="Clear Log", 
            command=self.clear_activity_log,
            width=100
        )
        self.clear_log_btn.pack(side="left", padx=(10, 0))
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_cb = ctk.CTkCheckBox(
            log_controls, 
            text="Auto-scroll", 
            variable=self.auto_scroll_var
        )
        self.auto_scroll_cb.pack(side="right", padx=(0, 10))
        
    def browse_file(self):
        """Open file browser to select input CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select Subreddit CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.input_file = file_path
            self.log_activity(f"Selected input file: {os.path.basename(file_path)}")
            
            # Count total rows for progress tracking
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    self.total_count = sum(1 for row in reader)
                self.log_activity(f"File contains {self.total_count} subreddits")
            except Exception as e:
                self.log_activity(f"Error reading file: {str(e)}", "ERROR")
                
    def start_scraping(self):
        """Start the scraping process."""
        if not self.input_file:
            messagebox.showerror("Error", "Please select an input CSV file first.")
            return
            
        if not os.path.exists(self.input_file):
            messagebox.showerror("Error", "Selected input file does not exist.")
            return
            
        # Check if we're resuming
        if os.path.exists(self.progress_file) and not self.is_running:
            resume = messagebox.askyesno(
                "Resume Progress", 
                "Found previous progress data. Do you want to resume from where you left off?"
            )
            if resume:
                self.load_progress()
        
        # Setup output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = os.path.join(self.config["output_dir"], f"subreddit_descriptions_{timestamp}.csv")
        
        # Ensure output directory exists
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        # Update UI state
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        
        self.log_activity("Starting scraping process...")
        self.update_status("Running")
        
        # Start scraping thread
        self.current_thread = threading.Thread(target=self.scraping_worker, daemon=True)
        self.current_thread.start()
        
    def pause_scraping(self):
        """Pause/Resume the scraping process."""
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.configure(text="Pause")
            self.log_activity("Resumed scraping")
            self.update_status("Running")
        else:
            self.is_paused = True
            self.pause_btn.configure(text="Resume")
            self.log_activity("Paused scraping")
            self.update_status("Paused")
            
    def stop_scraping(self):
        """Stop the scraping process."""
        self.is_running = False
        self.is_paused = False
        
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="Pause")
        self.stop_btn.configure(state="disabled")
        
        self.log_activity("Stopped scraping")
        self.update_status("Stopped")
        
        # Save progress
        self.save_progress()
        
    def scraping_worker(self):
        """Main scraping worker thread."""
        try:
            processed_in_session = 0
            
            # Load existing progress if resuming
            start_index = getattr(self, 'resume_index', 0)
            
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                rows = list(reader)
                
            # Skip to resume point if resuming
            rows_to_process = rows[start_index:]
            
            # Create/append to output file
            mode = 'a' if start_index > 0 and os.path.exists(self.output_file) else 'w'
            
            with open(self.output_file, mode, newline='', encoding='utf-8') as outfile:
                fieldnames = ['Subreddit', 'Link', 'Description', 'NSFW_Flag', 'NSFW_Reason', 'Confidence_Score', 'Processing_Time']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                
                if mode == 'w':
                    writer.writeheader()
                
                for i, row in enumerate(rows_to_process):
                    if not self.is_running:
                        break
                        
                    # Handle pause
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                        
                    if not self.is_running:
                        break
                        
                    subreddit = row['Subreddit']
                    url = row['Link']
                    
                    # Send status update to GUI
                    self.message_queue.put(("current", subreddit))
                    
                    start_time = time.time()
                    
                    # Get description and classify - process_subreddit handles ALL error logic including 429 pauses
                    description, is_nsfw, reason, confidence = self.process_subreddit(subreddit, url)
                    
                    processing_time = time.time() - start_time
                    
                    # Prepare output row
                    output_row = {
                        'Subreddit': subreddit,
                        'Link': url,
                        'Description': description,
                        'NSFW_Flag': 'YES' if is_nsfw else 'NO',
                        'NSFW_Reason': reason,
                        'Confidence_Score': confidence,
                        'Processing_Time': f"{processing_time:.2f}s"
                    }
                    
                    writer.writerow(output_row)
                    
                    # Update counters
                    self.processed_count = start_index + i + 1
                    processed_in_session += 1
                    
                    if is_nsfw:
                        self.nsfw_count += 1
                    else:
                        self.safe_count += 1
                        
                    # Save result for all cases except API errors
                    if not description.startswith("API error:"):
                        # Send updates to GUI (includes 404s, no description found, etc.)
                        self.message_queue.put(("progress", None))
                        self.message_queue.put(("result", output_row.copy()))
                        if description == "Subreddit not found (404)":
                            self.log_activity(f"Skipped {subreddit}: subreddit not found", "INFO")
                        elif description == "No description found":
                            self.log_activity(f"Processed {subreddit}: no description available", "INFO")
                    else:
                        # Still update progress but don't save API error results
                        self.message_queue.put(("progress", None))
                        self.log_activity(f"Skipping API error for {subreddit}: {description[:50]}...", "WARNING")
                    
                    # Auto-save progress
                    if processed_in_session % self.config["auto_save_interval"] == 0:
                        self.save_progress()
                        
                    # Check if we should stop due to errors
                    if not self.is_running:
                        break
                        
                    # Rate limiting
                    time.sleep(self.config["rate_limit"])
                    
            # Completion
            self.message_queue.put(("complete", None))
            
        except Exception as e:
            self.message_queue.put(("error", str(e)))
            
    def process_subreddit(self, subreddit: str, url: str) -> Tuple[str, bool, str, int]:
        """Process a single subreddit to get description and classify NSFW status."""
        description = "No description found"
        retry_count = 0
        has_rate_limit_error = False
        
        while retry_count < self.config["max_retries"]:
            try:
                if self.config["use_reddit_api"]:
                    description = self.get_description_api(subreddit)
                else:
                    description = self.get_description_html(subreddit, url)
                    
                if description and description != "No description found" and not description.startswith("API error:") and not description.startswith("Network error:"):
                    # Success - reset consecutive error counter
                    self.consecutive_api_errors = 0
                    break
                elif description == "Subreddit not found (404)":
                    # 404 errors should not be retried - treat as final result
                    self.consecutive_api_errors = 0
                    break
                elif "429" in description or "Too Many Requests" in description or "Rate limited by Reddit" in description:
                    # Handle rate limit errors - PAUSE FOR 15 MINUTES then retry
                    has_rate_limit_error = True
                    self.consecutive_api_errors += 1
                    self.log_activity(f"API rate limit reached ({self.consecutive_api_errors}/{self.max_consecutive_errors}) - pausing for 15 minutes", "WARNING")
                    
                    # If too many consecutive errors, stop completely
                    if self.consecutive_api_errors >= self.max_consecutive_errors:
                        self.log_activity("Too many consecutive API errors - stopping scraper", "ERROR")
                        self.message_queue.put(("force_stop", f"Stopped after {self.max_consecutive_errors} consecutive API errors"))
                        return "API limit exceeded - scraper stopped", False, "Scraper stopped", 0
                    
                    self.message_queue.put(("rate_limit_pause", None))
                    self.last_rate_limit_time = time.time()
                    
                    # Wait 15 minutes (900 seconds)
                    for i in range(900):
                        if not self.is_running:
                            break
                        time.sleep(1)
                        if i % 60 == 0:  # Log every minute
                            remaining = (900 - i) // 60
                            self.log_activity(f"Rate limit pause: {remaining} minutes remaining", "INFO")
                    
                    if self.is_running:
                        self.log_activity("Rate limit pause completed - resuming scraping", "INFO")
                        self.message_queue.put(("rate_limit_resume", None))
                        # Retry this same subreddit after the pause
                        retry_count = 0  # Reset retry count after rate limit pause
                        continue
                    
            except Exception as e:
                error_msg = str(e)
                self.log_activity(f"Error processing {subreddit} (attempt {retry_count + 1}): {error_msg}", "ERROR")
                
                # Check for API rate limit error (429)
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    has_rate_limit_error = True
                    self.consecutive_api_errors += 1
                    self.log_activity(f"API rate limit reached ({self.consecutive_api_errors}/{self.max_consecutive_errors}) - pausing for 15 minutes", "WARNING")
                    
                    # If too many consecutive errors, stop completely
                    if self.consecutive_api_errors >= self.max_consecutive_errors:
                        self.log_activity("Too many consecutive API errors - stopping scraper", "ERROR")
                        self.message_queue.put(("force_stop", f"Stopped after {self.max_consecutive_errors} consecutive API errors"))
                        return "API limit exceeded - scraper stopped", False, "Scraper stopped", 0
                    
                    self.message_queue.put(("rate_limit_pause", None))
                    self.last_rate_limit_time = time.time()
                    
                    # Wait 15 minutes (900 seconds)
                    for i in range(900):
                        if not self.is_running:
                            break
                        time.sleep(1)
                        if i % 60 == 0:  # Log every minute
                            remaining = (900 - i) // 60
                            self.log_activity(f"Rate limit pause: {remaining} minutes remaining", "INFO")
                    
                    if self.is_running:
                        self.log_activity("Rate limit pause completed - resuming scraping", "INFO")
                        self.message_queue.put(("rate_limit_resume", None))
                        # Retry this same subreddit after the pause
                        retry_count = 0  # Reset retry count after rate limit pause
                        continue
                
                retry_count += 1
                if retry_count < self.config["max_retries"]:
                    time.sleep(2)  # Increased delay between retries
                else:
                    if has_rate_limit_error:
                        description = f"API error: 429 Client Error: Too Many Requests"
                    else:
                        description = f"Error after {self.config['max_retries']} attempts"
                    self.error_count += 1
                    
        # Only classify if we have a valid description
        if description and not description.startswith("API error:") and description != "No description found" and description != "Subreddit not found (404)":
            is_nsfw, reason, confidence = self.detect_nsfw_from_description(description)
        elif description == "Subreddit not found (404)":
            is_nsfw, reason, confidence = False, "Subreddit does not exist", 0
        else:
            is_nsfw, reason, confidence = False, "No valid description obtained", 0
        
        return description, is_nsfw, reason, confidence
        
    def get_description_html(self, subreddit: str, url: str) -> str:
        """Get subreddit description using HTML scraping."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            # Try old reddit first to avoid cookie consent
            if 'reddit.com/r/' in url:
                old_url = url.replace('www.reddit.com', 'old.reddit.com')
                response = requests.get(old_url, headers=headers, timeout=self.config["timeout"])
            else:
                response = requests.get(url, headers=headers, timeout=self.config["timeout"])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for description
            description_selectors = [
                '[data-testid="subreddit-sidebar"] p',
                '.sidebar .usertext-body p',
                '.subreddit-description',
                '.sidebar-textbox p',
                '[data-click-id="text"] p',
                '.description p',
                '.sidebar .md p'
            ]
            
            description = ""
            for selector in description_selectors:
                elements = soup.select(selector)
                if elements:
                    texts = [elem.get_text().strip() for elem in elements[:3]]
                    description = " ".join(texts)
                    if description:
                        break
                        
            # Fallback: look for any sidebar text
            if not description:
                sidebar = soup.find(['div'], {'class': ['sidebar', 'subreddit-sidebar']})
                if sidebar:
                    text_content = sidebar.get_text().strip()
                    lines = text_content.split('\n')
                    for line in lines:
                        if len(line) > 20 and not line.isupper():
                            description = line
                            break
                            
            # Clean up description
            if description:
                description = re.sub(r'\s+', ' ', description).strip()
                description = description[:500]  # Limit length
                
            return description if description else "No description found"
            
        except requests.exceptions.RequestException as e:
            # Handle specific HTTP errors
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    return "Subreddit not found (404)"
                elif e.response.status_code == 429:
                    return "Rate limited by Reddit (429)"
            return f"Network error: {str(e)[:100]}"
        except Exception as e:
            return f"Parse error: {str(e)[:100]}"
            
    def get_description_api(self, subreddit: str) -> str:
        """Get subreddit description using Reddit API (fallback method)."""
        api_url = f"https://www.reddit.com/r/{subreddit}/about.json"
        headers = {
            'User-Agent': 'SubredditDescriptionScraper/1.0'
        }
        
        try:
            response = requests.get(api_url, headers=headers, timeout=self.config["timeout"])
            response.raise_for_status()
            
            data = response.json()
            if 'data' in data and 'public_description' in data['data']:
                description = data['data']['public_description']
                if not description and 'description' in data['data']:
                    description = data['data']['description']
                    
                if description:
                    # Clean up description
                    description = re.sub(r'\s+', ' ', description).strip()
                    description = description[:500]
                    return description
                    
            return "No description found"
            
        except requests.exceptions.RequestException as e:
            # Handle specific HTTP errors
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    return "Subreddit not found (404)"
                elif e.response.status_code == 429:
                    return "Rate limited by Reddit (429)"
            return f"API error: {str(e)[:100]}"
        except json.JSONDecodeError:
            return "Invalid API response"
        except Exception as e:
            return f"API parse error: {str(e)[:100]}"
            
    def detect_nsfw_from_description(self, description: str) -> Tuple[bool, str, int]:
        """Detect NSFW content based on description text."""
        if not description or "No description found" in description or "error" in description.lower():
            return False, "No description available", 0
            
        desc_lower = description.lower()
        reasons = []
        confidence = 0
        
        # Check for explicit content markers
        explicit_count = 0
        for term in self.nsfw_indicators['explicit_content']:
            if term in desc_lower:
                explicit_count += 1
                if explicit_count == 1:
                    reasons.append("Contains explicit content markers")
                confidence = max(confidence, 9)
                
        # Check for sexual terms
        sexual_count = 0
        for term in self.nsfw_indicators['sexual_terms']:
            if term in desc_lower:
                sexual_count += 1
                if sexual_count == 1:
                    reasons.append("Contains sexual terminology")
                confidence = max(confidence, 7)
                
        # Check for community markers
        community_count = 0
        for term in self.nsfw_indicators['community_markers']:
            if term in desc_lower:
                community_count += 1
                if community_count == 1:
                    reasons.append("Contains NSFW community indicators")
                confidence = max(confidence, 6)
                
        # Check for body-related terms (lower confidence)
        body_count = 0
        for term in self.nsfw_indicators['body_related']:
            if term in desc_lower:
                body_count += 1
                if body_count == 1:
                    reasons.append("Contains body-related terms")
                confidence = max(confidence, 4)
                
        # Age restrictions mentioned
        if any(term in desc_lower for term in ['18+', 'over 18', 'must be 18', 'adult only']):
            reasons.append("Age restrictions mentioned")
            confidence = max(confidence, 8)
            
        # Multiple indicators boost confidence
        total_indicators = explicit_count + sexual_count + community_count
        if total_indicators >= 2:
            confidence = max(confidence, 8)
            
        is_nsfw = confidence >= 6  # Higher threshold for description-based detection
        reason_text = "; ".join(reasons) if reasons else "No NSFW indicators in description"
        
        return is_nsfw, reason_text, confidence
        
    def check_message_queue(self):
        """Check for messages from the worker thread and update GUI."""
        try:
            while not self.message_queue.empty():
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "progress":
                    self.update_progress()
                elif message_type == "result":
                    self.add_result(data)
                elif message_type == "current":
                    self.current_label.configure(text=f"Current: {data}")
                elif message_type == "complete":
                    self.scraping_complete()
                elif message_type == "error":
                    self.handle_error(data)
                elif message_type == "rate_limit_pause":
                    self.update_status("Rate Limited - Pausing 15 min")
                elif message_type == "rate_limit_resume":
                    self.update_status("Running")
                elif message_type == "force_stop":
                    self.force_stop_scraping(data)
                    
        except queue.Empty:
            pass
            
        # Schedule next check
        self.window.after(100, self.check_message_queue)
        
    def update_progress(self):
        """Update progress bars and statistics."""
        if self.total_count > 0:
            progress = self.processed_count / self.total_count
            self.overall_progress.set(progress)
            self.progress_label.configure(
                text=f"{self.processed_count} / {self.total_count} ({progress * 100:.1f}%)"
            )
            
        # Update counters
        self.nsfw_label.configure(text=f"NSFW: {self.nsfw_count}")
        self.safe_label.configure(text=f"Safe: {self.safe_count}")
        self.error_label.configure(text=f"Errors: {self.error_count}")
        
        # Update time and rate information
        if self.start_time:
            elapsed = time.time() - self.start_time
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            self.time_label.configure(text=f"Elapsed: {elapsed_str}")
            
            if self.processed_count > 0 and elapsed > 0:
                rate = (self.processed_count * 60) / elapsed  # items per minute
                self.rate_label.configure(text=f"Rate: {rate:.1f} items/min")
                
                if rate > 0 and self.total_count > self.processed_count:
                    remaining = self.total_count - self.processed_count
                    eta_seconds = (remaining * 60) / rate
                    eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                    self.eta_label.configure(text=f"ETA: {eta_str}")
                    
    def add_result(self, result):
        """Add a new result to the recent results table."""
        # Add to both recent results and main results for export
        self.recent_results.append(result)
        self.results.append(result)
        
        # Keep recent results limited (last 50)
        if len(self.recent_results) > 50:
            self.recent_results.pop(0)
            
        # Update results tree
        self.update_results_tree()
        
        # Log the result
        status = "SUCCESS" if result['Description'] != "No description found" else "NO_DESC"
        classification = result['NSFW_Flag']
        confidence = result['Confidence_Score']
        
        self.log_activity(
            f"Processed {result['Subreddit']}: {classification} (confidence: {confidence})", 
            status
        )
        
    def update_results_tree(self):
        """Update the results tree view with recent results."""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Add recent results (most recent first)
        for result in reversed(self.recent_results[-20:]):  # Show last 20
            status = "✓" if result['Description'] != "No description found" else "⚠"
            classification = result['NSFW_Flag']
            confidence = result['Confidence_Score']
            description_preview = result['Description'][:100] + "..." if len(result['Description']) > 100 else result['Description']
            
            self.results_tree.insert(
                '', 0,  # Insert at top
                values=(result['Subreddit'], status, classification, confidence, description_preview)
            )
            
    def scraping_complete(self):
        """Handle completion of scraping process."""
        self.is_running = False
        self.is_paused = False
        
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="Pause")
        self.stop_btn.configure(state="disabled")
        
        self.update_status("Completed")
        self.current_label.configure(text="Current: Complete")
        
        # Final progress update
        self.update_progress()
        
        # Save final results
        self.save_progress()
        
        self.log_activity("Scraping completed successfully!")
        self.log_activity(f"Total processed: {self.processed_count}")
        self.log_activity(f"NSFW found: {self.nsfw_count}")
        self.log_activity(f"Safe found: {self.safe_count}")
        self.log_activity(f"Errors: {self.error_count}")
        self.log_activity(f"Results saved to: {self.output_file}")
        
        # Show completion dialog
        messagebox.showinfo(
            "Scraping Complete",
            f"Successfully processed {self.processed_count} subreddits!\n\n"
            f"NSFW: {self.nsfw_count}\n"
            f"Safe: {self.safe_count}\n"
            f"Errors: {self.error_count}\n\n"
            f"Results saved to:\n{self.output_file}"
        )
        
    def handle_error(self, error_msg):
        """Handle errors from the worker thread."""
        self.is_running = False
        self.is_paused = False
        
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="Pause")
        self.stop_btn.configure(state="disabled")
        
        self.update_status("Error")
        self.log_activity(f"Scraping error: {error_msg}", "ERROR")
        
        messagebox.showerror("Scraping Error", f"An error occurred during scraping:\n\n{error_msg}")
        
    def force_stop_scraping(self, reason):
        """Force stop the scraping due to too many errors."""
        self.is_running = False
        self.is_paused = False
        
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="Pause")
        self.stop_btn.configure(state="disabled")
        
        self.update_status("Force Stopped")
        self.log_activity(f"Scraping force stopped: {reason}", "ERROR")
        
        # Save progress before stopping
        self.save_progress()
        
        messagebox.showerror(
            "Scraping Force Stopped", 
            f"Scraping has been automatically stopped:\n\n{reason}\n\nProgress has been saved. You can resume later using 'Load Progress'."
        )
        
    def log_activity(self, message: str, level: str = "INFO"):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.activity_log.append(log_entry)
        
        # Update activity text widget
        self.activity_text.insert("end", log_entry + "\n")
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.activity_text.see("end")
            
        # Limit log size
        if len(self.activity_log) > 1000:
            self.activity_log.pop(0)
            
    def clear_activity_log(self):
        """Clear the activity log."""
        self.activity_log.clear()
        self.activity_text.delete("1.0", "end")
        
    def update_status(self, status: str):
        """Update the status label."""
        self.status_label.configure(text=f"Status: {status}")
        
    def open_settings(self):
        """Open the settings configuration dialog."""
        settings_window = ctk.CTkToplevel(self.window)
        settings_window.title("Settings")
        settings_window.geometry("600x500")
        settings_window.transient(self.window)
        settings_window.grab_set()
        
        # Main container
        main_frame = ctk.CTkFrame(settings_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame, 
            text="Scraper Settings", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # Settings sections
        self.create_settings_section(main_frame, "Rate Limiting", [
            ("Rate Limit (seconds)", "rate_limit", "float"),
            ("Request Timeout (seconds)", "timeout", "int"),
            ("Max Retries", "max_retries", "int")
        ])
        
        self.create_settings_section(main_frame, "Auto-Save", [
            ("Auto-save Interval", "auto_save_interval", "int"),
            ("Output Directory", "output_dir", "string")
        ])
        
        self.create_settings_section(main_frame, "Scraping Method", [
            ("Use Reddit API", "use_reddit_api", "boolean"),
            ("Batch Size", "batch_size", "int")
        ])
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame, 
            text="Save Settings", 
            command=lambda: self.save_settings(settings_window),
            width=120
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=settings_window.destroy,
            width=120
        ).pack(side="right")
        
        ctk.CTkButton(
            button_frame, 
            text="Reset to Defaults", 
            command=self.reset_settings,
            width=120
        ).pack(side="left")
        
    def create_settings_section(self, parent, title, settings):
        """Create a section of settings controls."""
        # Section frame
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        ctk.CTkLabel(
            section_frame, 
            text=title, 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Settings controls
        for label, key, setting_type in settings:
            control_frame = ctk.CTkFrame(section_frame)
            control_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(control_frame, text=label).pack(side="left", padx=(10, 0))
            
            if setting_type == "boolean":
                var = tk.BooleanVar(value=self.config[key])
                control = ctk.CTkCheckBox(control_frame, text="", variable=var)
                setattr(self, f"setting_{key}", var)
            else:
                var = tk.StringVar(value=str(self.config[key]))
                control = ctk.CTkEntry(control_frame, textvariable=var, width=150)
                setattr(self, f"setting_{key}", var)
                
            control.pack(side="right", padx=(0, 10))
            
    def save_settings(self, window):
        """Save settings and close the dialog."""
        try:
            # Update config from GUI controls
            for key in self.config:
                if hasattr(self, f"setting_{key}"):
                    var = getattr(self, f"setting_{key}")
                    value = var.get()
                    
                    # Convert types
                    if isinstance(self.config[key], float):
                        self.config[key] = float(value)
                    elif isinstance(self.config[key], int):
                        self.config[key] = int(value)
                    elif isinstance(self.config[key], bool):
                        self.config[key] = bool(value)
                    else:
                        self.config[key] = value
                        
            self.save_config()
            window.destroy()
            self.log_activity("Settings saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
            
    def reset_settings(self):
        """Reset settings to defaults."""
        defaults = {
            "rate_limit": 2.0,
            "auto_save_interval": 50,
            "timeout": 10,
            "max_retries": 3,
            "output_dir": "Exports",
            "use_reddit_api": False,
            "batch_size": 100
        }
        
        self.config.update(defaults)
        
        # Update GUI controls
        for key in defaults:
            if hasattr(self, f"setting_{key}"):
                var = getattr(self, f"setting_{key}")
                var.set(defaults[key])
                
        self.log_activity("Settings reset to defaults")
        
    def export_results(self):
        """Export current results to CSV file."""
        if not self.results:
            messagebox.showwarning("No Data", "No results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.config["output_dir"]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['Subreddit', 'Link', 'Description', 'NSFW_Flag', 'NSFW_Reason', 'Confidence_Score', 'Processing_Time']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.results)
                    
                self.log_activity(f"Results exported to: {file_path}")
                messagebox.showinfo("Export Complete", f"Results exported successfully to:\n{file_path}")
                
            except Exception as e:
                self.log_activity(f"Export error: {str(e)}", "ERROR")
                messagebox.showerror("Export Error", f"Error exporting results:\n{str(e)}")
                
    def save_progress(self):
        """Save current progress to file."""
        try:
            progress_data = {
                "processed_count": self.processed_count,
                "nsfw_count": self.nsfw_count,
                "safe_count": self.safe_count,
                "error_count": self.error_count,
                "input_file": self.input_file,
                "output_file": self.output_file,
                "total_count": self.total_count,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
                
        except Exception as e:
            self.log_activity(f"Error saving progress: {str(e)}", "ERROR")
            
    def load_progress(self):
        """Load progress from file."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    
                self.processed_count = progress_data.get("processed_count", 0)
                self.nsfw_count = progress_data.get("nsfw_count", 0)
                self.safe_count = progress_data.get("safe_count", 0)
                self.error_count = progress_data.get("error_count", 0)
                self.total_count = progress_data.get("total_count", 0)
                self.resume_index = self.processed_count
                
                # Update display
                self.update_progress()
                
                self.log_activity(f"Loaded progress: {self.processed_count} items processed")
                
        except Exception as e:
            self.log_activity(f"Error loading progress: {str(e)}", "ERROR")
            
    def save_config(self):
        """Save configuration to file."""
        try:
            config_file = "scraper_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log_activity(f"Error saving config: {str(e)}", "ERROR")
            
    def load_config(self):
        """Load configuration from file."""
        try:
            config_file = "scraper_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                self.config.update(saved_config)
        except Exception as e:
            self.log_activity(f"Error loading config: {str(e)}", "ERROR")
            
    def on_closing(self):
        """Handle application closing."""
        if self.is_running:
            if messagebox.askyesno("Confirm Exit", "Scraping is in progress. Do you want to stop and exit?"):
                self.stop_scraping()
                self.window.after(1000, self.window.destroy)  # Give time to save progress
        else:
            self.window.destroy()
            
    def run(self):
        """Run the application."""
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial log message
        self.log_activity("Reddit Subreddit Description Scraper v2.0 started")
        self.log_activity("Ready to begin scraping...")
        
        self.window.mainloop()

def main():
    """Main entry point."""
    app = RedditScraperGUI()
    app.run()

if __name__ == "__main__":
    main()