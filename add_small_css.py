#!/usr/bin/env python3
"""
Add CSS for small links
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Add small tag CSS after the link CSS
old_css = """        a {{
            color: var(--accent);
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}"""

new_css = """        a {{
            color: var(--accent);
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        small {{
            font-size: 13px;
            color: var(--text-secondary);
            display: block;
            margin: 15px 0;
            text-align: center;
        }}
        small a {{
            font-size: 13px;
            margin: 0 10px;
        }}"""

content = content.replace(old_css, new_css)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Added CSS for small links")
