#!/usr/bin/env python3
"""
Reduce section and article title font sizes
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Reduce h2 (section headers) from 48px to 36px
old_h2 = """        h2 {
            color: var(--accent);
            font-size: 48px;
            font-weight: 800;
            margin-top: 60px;
            margin-bottom: 30px;
            letter-spacing: -0.5px;
            border-left: 6px solid var(--accent);
            padding-left: 24px;
            text-transform: uppercase;"""

new_h2 = """        h2 {
            color: var(--accent);
            font-size: 36px;
            font-weight: 800;
            margin-top: 50px;
            margin-bottom: 24px;
            letter-spacing: -0.4px;
            border-left: 5px solid var(--accent);
            padding-left: 20px;
            text-transform: uppercase;"""

content = content.replace(old_h2, new_h2)

# Reduce strong (article titles) from 28px to 22px
old_strong = """        strong {
            display: block;
            font-size: 28px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 12px;
            margin-top: 24px;
            line-height: 1.3;
        }"""

new_strong = """        strong {
            display: block;
            font-size: 22px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 10px;
            margin-top: 20px;
            line-height: 1.4;
        }"""

content = content.replace(old_strong, new_strong)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Reduced font sizes:")
print("  - Section headers: 48px → 36px")
print("  - Article titles: 28px → 22px")
