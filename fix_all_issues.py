#!/usr/bin/env python3
"""
Fix all the issues:
1. Split header into two small links
2. Clean up Moltbook author JSON
3. Remove duplicate Health section
4. Archive happens automatically before each run
"""

import re

# Read current markdown
with open('Exports/complete_everything.md', 'r') as f:
    content = f.read()

# 1. Replace the header link
old_header = '[View Complete Archive with Summaries →](Database/complete_with_titles.html)'
new_header = '<small>[Complete Digest](Database/complete_with_titles.html) • [All Items Archive](https://github.com/DiamondDeals/daily-dossier/tree/master/Database)</small>'
content = content.replace(old_header, new_header)

# 2. Clean up Moltbook author JSON
# Find patterns like: @{'id': '...', 'name': 'Name', 'description': '...', ...}
def clean_moltbook_author(match):
    raw = match.group(0)
    # Extract name and description
    name_match = re.search(r"'name': '([^']+)'", raw)
    desc_match = re.search(r"'description': '([^']+)'", raw)
    
    if name_match:
        name = name_match.group(1)
        if desc_match:
            desc = desc_match.group(1)
            return f"@{name} • {desc}"
        return f"@{name}"
    return raw

content = re.sub(r"@\{'id':[^}]+\}", clean_moltbook_author, content)

# 3. Remove duplicate Health section
# Find all occurrences of "## 🟢 Health & Wellness"
health_sections = [m.start() for m in re.finditer(r'## 🟢 Health & Wellness', content)]
if len(health_sections) > 1:
    print(f"Found {len(health_sections)} Health sections, removing duplicates...")
    # Keep only the first one by removing text from 2nd occurrence to the next section
    first_end = content.find('\n## ', health_sections[0] + 10)
    second_start = health_sections[1]
    second_end = content.find('\n## ', second_start + 10)
    
    if second_end == -1:
        # It's the last section
        content = content[:second_start]
    else:
        # Remove the duplicate section
        content = content[:second_start] + content[second_end:]

# Save
with open('Exports/complete_everything.md', 'w') as f:
    f.write(content)

print("✅ Fixed all issues")
print("  - Header split into two small links")
print("  - Moltbook author JSON cleaned up")
print("  - Duplicate Health section removed")
