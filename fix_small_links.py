#!/usr/bin/env python3
"""
Use HTML directly for small links
"""

with open('Exports/complete_everything.md', 'r') as f:
    content = f.read()

# Replace the markdown links with direct HTML
old_line = '<small>[Complete Digest](Database/complete_with_titles.html) • [All Items Archive](https://github.com/DiamondDeals/daily-dossier/tree/master/Database)</small>'
new_line = '<small><a href="Database/complete_with_titles.html">Complete Digest</a> • <a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Database">All Items Archive</a></small>'

content = content.replace(old_line, new_line)

with open('Exports/complete_everything.md', 'w') as f:
    f.write(content)

print("✅ Fixed small links to use HTML directly")
