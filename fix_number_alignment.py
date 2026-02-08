#!/usr/bin/env python3
"""
Fix number alignment - make strong inline-block instead of block
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Find and replace the strong CSS
old_strong = """        strong {{
            display: block;
            font-size: 22px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 10px;
            margin-top: 20px;
            line-height: 1.4;
        }}"""

new_strong = """        strong {{
            display: inline;
            font-size: 22px;
            font-weight: 800;
            color: var(--accent);
        }}"""

content = content.replace(old_strong, new_strong)

# Also update the paragraph styling to handle the spacing
old_p = """        p {{
            margin-bottom: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 15px;
        }}"""

new_p = """        p {{
            margin-bottom: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 15px;
        }}
        
        p:has(strong) {{
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 18px;
        }}"""

content = content.replace(old_p, new_p)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Fixed strong to be inline (number and title on same line)")
