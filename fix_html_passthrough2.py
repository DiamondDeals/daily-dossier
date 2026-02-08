#!/usr/bin/env python3
"""
Better HTML passthrough - don't apply regex to HTML
"""

with open('html_generator.py', 'r') as f:
    lines = f.readlines()

# Find and replace the passthrough section
new_lines = []
in_section = False
section_lines = []

for i, line in enumerate(lines):
    if '# Regular paragraphs' in line:
        in_section = True
        section_lines = [line]
    elif in_section:
        section_lines.append(line)
        # Check if we've collected the whole section (ends with html_lines.append)
        if 'html_lines.append(f\'<p>{content}</p>\')' in line:
            # Replace entire section
            new_section = '''            # Regular paragraphs
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                
                content = stripped
                
                # Allow raw HTML passthrough (don't apply regex transformations)
                if '<' in content and '>' in content and content.startswith('<'):
                    # It's HTML, pass through as-is
                    html_lines.append(content)
                else:
                    # It's markdown, apply transformations
                    import re
                    content = re.sub(r'\\*\\*(.+?)\\*\\*', r'<strong>\\1</strong>', content)
                    content = re.sub(r'(https?://[^\\s]+)', r'<a href="\\1" target="_blank">\\1</a>', content)
                    
                    if content and content != '---':
                        html_lines.append(f'<p>{content}</p>')
'''
            new_lines.append(new_section)
            in_section = False
            section_lines = []
        elif i+1 < len(lines) and 'if in_list:' in lines[i+1] and not 'else:' in line:
            # We passed the section without finding the end marker
            new_lines.extend(section_lines)
            in_section = False
            section_lines = []
    else:
        new_lines.append(line)

with open('html_generator.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed HTML passthrough v2")
