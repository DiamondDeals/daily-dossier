#!/usr/bin/env python3
"""
Fix the visual hierarchy - article titles need to be HUGE
"""

# Update CSS in html_generator.py
with open('html_generator.py', 'r') as f:
    content = f.read()

# Find and replace h2 (section headers) - make them H1 size
old_h2 = """        h2 {{
            color: var(--text-primary);
            font-size: 36px;
            font-weight: 800;
            margin-top: 48px;
            margin-bottom: 20px;
            letter-spacing: -0.3px;
            border-left: 4px solid var(--accent);
            padding-left: 20px;"""

new_h2 = """        h2 {{
            color: var(--accent);
            font-size: 48px;
            font-weight: 800;
            margin-top: 60px;
            margin-bottom: 30px;
            letter-spacing: -0.5px;
            border-left: 6px solid var(--accent);
            padding-left: 24px;
            text-transform: uppercase;"""

content = content.replace(old_h2, new_h2)

# Fix strong (article titles) - make them MASSIVE
old_strong = """        strong {{
            display: block;
            font-size: 20px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 8px;
            margin-top: 16px;
        }}"""

new_strong = """        strong {{
            display: block;
            font-size: 28px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 12px;
            margin-top: 24px;
            line-height: 1.3;
        }}"""

content = content.replace(old_strong, new_strong)

# Make regular paragraph text smaller so titles stand out more
old_p = """        p {{
            margin-bottom: 16px;
            color: var(--text-primary);
            line-height: 1.6;
        }}"""

new_p = """        p {{
            margin-bottom: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 15px;
        }}"""

content = content.replace(old_p, new_p)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Fixed visual hierarchy")
