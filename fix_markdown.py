#!/usr/bin/env python3
"""
Fix the markdown structure
"""

with open('Exports/complete_everything.md', 'r') as f:
    content = f.read()

# Remove the "# Daily Business Dossier" line
content = content.replace('# Daily Business Dossier\n\n', '')

# Change the "Complete Digest" to a link
content = content.replace(
    '**Complete Digest - All Items Found**',
    '[View Complete Archive with Summaries →](Database/complete_with_titles.html)'
)

with open('Exports/complete_everything.md', 'w') as f:
    f.write(content)

print("✅ Fixed markdown structure")
