#!/usr/bin/env python3
"""
Add footer to dossier with links to complete databases
"""

import sys
from datetime import datetime
import os

# Fix emoji output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Get today's date
date_str = datetime.now().strftime('%Y-%m-%d')

# Check if database file exists
db_file = f'Database/all_items_{date_str}.html'
db_exists = os.path.exists(db_file)

# Build footer HTML
footer_html = '''
<hr style="margin: 60px 0 40px 0; border: none; border-top: 1px solid var(--border);">

<div style="text-align: center; padding: 30px 0;">
    <h3 style="color: var(--accent); font-size: 24px; margin-bottom: 20px;">Complete Databases</h3>
    <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 20px;">
        The dossier above shows curated highlights. Click below to see EVERY item found:
    </p>
    <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
'''

if db_exists:
    footer_html += f'''
        <a href="Database/all_items_{date_str}.html" style="
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 16px 32px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 700;
            font-size: 18px;
            transition: all 0.2s ease;
        ">
            View All Items ({date_str})
        </a>
'''

footer_html += f'''
    </div>
    <p style="color: var(--text-secondary); font-size: 13px; margin-top: 20px;">
        <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Database" style="color: var(--accent);">Browse Historical Databases</a>
        &nbsp;|&nbsp;
        <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Daily" style="color: var(--accent);">Daily Archives</a>
    </p>
</div>
'''

# Read current dossier
with open('dossier.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Check if footer already exists
if 'Complete Databases' in html:
    # Replace existing footer
    start = html.find('<hr style="margin: 60px 0 40px 0;')
    end = html.find('</div>\n</main>', start)
    if start > 0 and end > 0:
        html = html[:start] + footer_html + '\n</main>' + html[html.find('</main>', end) + 7:]
else:
    # Add new footer before </main>
    html = html.replace('</main>', footer_html + '\n</main>')

# Save
with open('dossier.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"{'OK' if db_exists else 'WARN: no database file'} - Added footer with database link(s)")
