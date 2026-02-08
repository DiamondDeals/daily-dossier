#!/usr/bin/env python3
"""
Add navigation link back to main dossier at top of complete database
"""

with open('Database/all_items_latest.html', 'r') as f:
    html = f.read()

# Add navigation header after the opening container div
nav_header = '''        <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #424245;">
            <a href="../dossier.html" style="
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                background: #0a84ff;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
                transition: all 0.2s ease;
            " onmouseover="this.style.background='#409cff'" onmouseout="this.style.background='#0a84ff'">
                ← Back to Main Dossier
            </a>
        </div>
'''

# Insert after the first h1
h1_end = html.find('</h1>')
if h1_end > 0:
    # Find the stats line after h1
    stats_end = html.find('</p>', h1_end)
    if stats_end > 0:
        next_p_end = html.find('</p>', stats_end + 4)
        if next_p_end > 0:
            html = html[:next_p_end + 4] + '\n' + nav_header + html[next_p_end + 4:]

with open('Database/all_items_latest.html', 'w') as f:
    f.write(html)

print("✅ Added navigation link to main dossier")

# Also update Daily folder
import shutil
shutil.copy('Database/all_items_latest.html', 'Daily/2026-02-07-10PM/all_items.html')
print("✅ Updated Daily/2026-02-07-10PM/all_items.html")
