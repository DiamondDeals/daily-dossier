#!/usr/bin/env python3
"""
Fix titles that start with emojis
"""

with open('Exports/complete_everything.md', 'r') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Check if line starts with a number, period, space, then has content
    # but the bold wrapping might have missed it
    if line.startswith('5. 🎙️'):
        # This line needs the emoji and text wrapped in bold
        line = line.replace('5. 🎙️ Episode', '5. **🎙️ Episode').replace('...', '...**', 1)
    fixed_lines.append(line)

with open('Exports/complete_everything.md', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed emoji title")
