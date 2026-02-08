#!/usr/bin/env python3
"""
Make numbered titles bold in markdown
"""

import re

with open('Exports/complete_everything.md', 'r') as f:
    content = f.read()

# Find all lines that start with a number followed by a period and wrap in **bold**
# But only if they're not already bold
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # Match lines like "1. Title text..." that aren't already bold
    if re.match(r'^\d+\.\s+[^\*]', line):
        # Extract the number and title
        match = re.match(r'^(\d+\.\s+)(.+)$', line)
        if match:
            num, title = match.groups()
            fixed_line = f"{num}**{title}**"
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

content = '\n'.join(fixed_lines)

with open('Exports/complete_everything.md', 'w') as f:
    f.write(content)

print("✅ Made all numbered titles bold")
