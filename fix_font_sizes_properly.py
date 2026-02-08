#!/usr/bin/env python3
"""
Fix font sizes in html_generator.py with correct double-brace format
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Replace h2 font-size line
content = content.replace('font-size: 48px;', 'font-size: 36px;', 1)  # First occurrence (h2)

# Replace h2 margin-top
content = content.replace('margin-top: 60px;', 'margin-top: 50px;', 1)

# Replace h2 margin-bottom
content = content.replace('margin-bottom: 30px;', 'margin-bottom: 24px;', 1)

# Replace h2 letter-spacing
content = content.replace('letter-spacing: -0.5px;', 'letter-spacing: -0.4px;')

# Replace h2 border-left
content = content.replace('border-left: 6px solid', 'border-left: 5px solid')

# Replace h2 padding-left
content = content.replace('padding-left: 24px;', 'padding-left: 20px;', 1)

# Find and replace strong font-size (need to find the strong block specifically)
lines = content.split('\n')
new_lines = []
in_strong_block = False

for line in lines:
    if 'strong {' in line:
        in_strong_block = True
        new_lines.append(line)
    elif in_strong_block:
        if 'font-size: 28px;' in line:
            new_lines.append(line.replace('28px', '22px'))
        elif 'margin-bottom: 12px;' in line:
            new_lines.append(line.replace('12px', '10px'))
        elif 'margin-top: 24px;' in line:
            new_lines.append(line.replace('24px', '20px'))
        elif 'line-height: 1.3;' in line:
            new_lines.append(line.replace('1.3', '1.4'))
            in_strong_block = False  # End of strong block
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Fixed font sizes in html_generator.py")
