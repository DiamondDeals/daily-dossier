#!/usr/bin/env python3
"""
Fix database links to point to the correct complete database
"""

import shutil
import os
from datetime import datetime

# Copy the complete database to a stable "latest" filename
date_str = datetime.now().strftime('%Y-%m-%d')
source_html = f'Database/all_items_{date_str}.html'
source_json = f'Database/complete_{date_str}.json'

if os.path.exists(source_html):
    shutil.copy(source_html, 'Database/all_items_latest.html')
    print(f"✅ Copied {source_html} → Database/all_items_latest.html")

if os.path.exists(source_json):
    shutil.copy(source_json, 'Database/complete_latest.json')
    print(f"✅ Copied {source_json} → Database/complete_latest.json")

# Update the markdown header
with open('Exports/complete_everything.md', 'r') as f:
    content = f.read()

# Replace the header link
old_link = '<small><a href="Database/complete_with_titles.html">Complete Digest</a> • <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Database">All Items Archive</a></small>'
new_link = '<small><a href="Database/all_items_latest.html">Complete Database (589 URLs)</a> • <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Database">All Archives</a></small>'

content = content.replace(old_link, new_link)

with open('Exports/complete_everything.md', 'w') as f:
    f.write(content)

print("✅ Updated header link in markdown")
