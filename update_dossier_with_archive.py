#!/usr/bin/env python3
"""
Update main dossier to include archive link
"""

from html_generator import DigestHTMLGenerator
from datetime import datetime

# Read current markdown
with open('Exports/complete_everything.md', 'r') as f:
    md = f.read()

# Add archive link at the top
date_str = datetime.now().strftime('%Y-%m-%d')
archive_link = f"\n\n**📁 [View Complete Database with Summaries →](Database/complete_with_titles.html)**\n\n"

# Insert after the first line
lines = md.split('\n')
lines.insert(2, archive_link)
md_with_link = '\n'.join(lines)

# Generate HTML
gen = DigestHTMLGenerator()
gen.archive_current_html()
html = gen.markdown_to_html(md_with_link, "Daily Business Dossier")
gen.save_html(html)

print("✅ Added archive link to main dossier")
