#!/usr/bin/env python3
"""
Add top navigation links to main dossier
"""

import os
import glob

# Read current dossier
with open('dossier.html', 'r') as f:
    html = f.read()

# Count URLs in complete database (use complete_with_titles.html)
url_count = 0
if os.path.exists('Database/complete_with_titles.html'):
    with open('Database/complete_with_titles.html', 'r') as f:
        url_count = f.read().count('<a href="http')

# Build top navigation
top_nav = f'<small><a href="Database/complete_with_titles.html">Complete Database ({url_count} URLs)</a> • <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Database">All Archives</a></small>\n\n'

# Insert after <main> tag
main_pos = html.find('<main>')
if main_pos > 0:
    # Check if already exists
    if 'Complete Database' not in html[main_pos:main_pos+500]:
        # Find the position after <main>\n
        insert_pos = html.find('\n', main_pos) + 1
        html = html[:insert_pos] + top_nav + html[insert_pos:]
        
        with open('dossier.html', 'w') as f:
            f.write(html)
        
        print(f"✅ Added top navigation ({url_count} URLs)")
    else:
        print("✅ Top navigation already exists")
else:
    print("❌ Could not find <main> tag")
