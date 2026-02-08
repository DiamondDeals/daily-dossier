#!/usr/bin/env python3
"""
Fix the table row detection to not catch regular text with pipes
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Replace the table row condition
# Old: elif '|' in stripped and not stripped.startswith('|---'):
# New: elif stripped.startswith('|') and '|' in stripped[1:] and not stripped.startswith('|---'):

old_condition = """            # Table rows
            elif '|' in stripped and not stripped.startswith('|---'):
                continue"""

new_condition = """            # Table rows (must start with |)
            elif stripped.startswith('|') and '|' in stripped[1:] and not stripped.startswith('|---'):
                continue"""

content = content.replace(old_condition, new_condition)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Fixed pipe filter")
