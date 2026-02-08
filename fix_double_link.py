#!/usr/bin/env python3
"""
Don't apply link regex if content already has <a> tags
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Find and fix the link regex application
old_code = """                else:
                    # It's markdown, apply transformations
                    import re
                    content = re.sub(r'\\*\\*(.+?)\\*\\*', r'<strong>\\1</strong>', content)
                    content = re.sub(r'(https?://[^\\s]+)', r'<a href="\\1" target="_blank">\\1</a>', content)"""

new_code = """                else:
                    # It's markdown, apply transformations
                    import re
                    content = re.sub(r'\\*\\*(.+?)\\*\\*', r'<strong>\\1</strong>', content)
                    # Only apply link regex if there are no existing <a> tags
                    if '<a href=' not in content:
                        content = re.sub(r'(https?://[^\\s]+)', r'<a href="\\1" target="_blank">\\1</a>', content)"""

content = content.replace(old_code, new_code)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Fixed double-link issue")
