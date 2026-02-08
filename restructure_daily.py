#!/usr/bin/env python3
"""
Restructure to Daily/ folder with AM/PM subdirectories
Each scan creates datetime-stamped complete databases
"""

import os
import shutil
from datetime import datetime

# Create Daily folder structure
date_str = datetime.now().strftime('%Y-%m-%d')
time_str = datetime.now().strftime('%I%p').lstrip('0')  # "6AM" or "5PM"
daily_folder = f'Daily/{date_str}-{time_str}'

os.makedirs(daily_folder, exist_ok=True)
print(f"✅ Created: {daily_folder}/")

# Move/copy today's complete database there
source_html = 'Database/all_items_2026-02-07.html'
source_json = 'Database/complete_2026-02-07.json'

if os.path.exists(source_html):
    dest_html = f'{daily_folder}/all_items.html'
    shutil.copy(source_html, dest_html)
    print(f"✅ Copied: {dest_html}")

if os.path.exists(source_json):
    dest_json = f'{daily_folder}/complete.json'
    shutil.copy(source_json, dest_json)
    print(f"✅ Copied: {dest_json}")

# Also copy the highlights digest
if os.path.exists('dossier.html'):
    dest_digest = f'{daily_folder}/digest.html'
    shutil.copy('dossier.html', dest_digest)
    print(f"✅ Copied: {dest_digest}")

print(f"\n📁 Daily folder ready: {daily_folder}/")
