# Update CSS to make individual post titles stand out MORE

css_additions = """
        /* Individual post titles */
        p strong {
            display: block;
            font-size: 20px;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 8px;
            margin-top: 16px;
        }
        
        /* Section headers even bigger */
        h2 {
            font-size: 36px !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
"""

# Read current HTML generator
with open('html_generator.py', 'r') as f:
    content = f.read()

# Find the strong style and replace it
old_strong = """        strong {
            color: var(--text-primary);
            font-weight: 700;
        }"""

new_strong = """        strong {
            display: block;
            font-size: 20px;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 8px;
            margin-top: 16px;
        }"""

content = content.replace(old_strong, new_strong)

# Also update h2 to be even more prominent
old_h2_weight = "font-weight: 700;"
new_h2_weight = "font-weight: 800;"
content = content.replace(old_h2_weight, new_h2_weight)

old_h2_size = "font-size: 32px;"
new_h2_size = "font-size: 36px;"
content = content.replace(old_h2_size, new_h2_size)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Updated CSS to make titles SUPER prominent")
