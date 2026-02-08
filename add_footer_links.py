#!/usr/bin/env python3
"""
Add footer to dossier with links to complete databases
"""

from datetime import datetime
import os
import glob

# Get today's date
date_str = datetime.now().strftime('%Y-%m-%d')

# Find all Daily folders for today
daily_folders = sorted(glob.glob(f'Daily/{date_str}-*'))

# Build footer HTML
footer_html = '''
<hr style="margin: 60px 0 40px 0; border: none; border-top: 1px solid var(--border);">

<div style="text-align: center; padding: 30px 0;">
    <h3 style="color: var(--accent); font-size: 24px; margin-bottom: 20px;">📊 Complete Databases</h3>
    <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 20px;">
        The main dossier above shows curated highlights. Click below to see EVERY item found:
    </p>
    <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
'''

# Add links for each Daily folder found
for folder in daily_folders:
    folder_name = os.path.basename(folder)  # e.g., "2026-02-07-6AM" or "2026-02-07-5PM"
    time_label = folder_name.split('-')[-1]  # "6AM" or "5PM"
    
    footer_html += f'''
        <a href="{folder}/all_items.html" style="
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
        ">
            {time_label} Complete ({date_str})
        </a>
'''

footer_html += '''
    </div>
    <p style="color: var(--text-secondary); font-size: 13px; margin-top: 20px;">
        <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Daily" style="color: var(--accent);">View All Historical Archives →</a>
    </p>
</div>
'''

# Read current dossier
with open('dossier.html', 'r') as f:
    html = f.read()

# Check if footer already exists
if '📊 Complete Databases' in html:
    # Replace existing footer
    start = html.find('<hr style="margin: 60px 0 40px 0;')
    end = html.find('</div>\n</main>', start)
    if start > 0 and end > 0:
        html = html[:start] + footer_html + '\n</main>' + html[html.find('</main>', end) + 7:]
else:
    # Add new footer before </main>
    html = html.replace('</main>', footer_html + '\n</main>')

# Save
with open('dossier.html', 'w') as f:
    f.write(html)

print(f"✅ Added footer with {len(daily_folders)} complete database link(s)")
