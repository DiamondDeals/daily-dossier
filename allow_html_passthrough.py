#!/usr/bin/env python3
"""
Update markdown parser to allow raw HTML passthrough
"""

with open('html_generator.py', 'r') as f:
    content = f.read()

# Find the section handling regular paragraphs and add HTML passthrough
old_section = """            # Regular paragraphs
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                
                content = stripped
                import re
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
                
                if content and content != '---':
                    html_lines.append(f'<p>{content}</p>')"""

new_section = """            # Regular paragraphs
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                
                content = stripped
                
                # Allow raw HTML passthrough for <small> and other tags
                if content.startswith('<') and '>' in content:
                    # It's HTML, pass it through
                    html_lines.append(content)
                else:
                    # It's markdown, convert it
                    import re
                    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                    content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
                    
                    if content and content != '---':
                        html_lines.append(f'<p>{content}</p>')"""

content = content.replace(old_section, new_section)

with open('html_generator.py', 'w') as f:
    f.write(content)

print("✅ Updated parser to allow HTML passthrough")
