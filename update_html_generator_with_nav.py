#!/usr/bin/env python3
"""
Update add_engagement_and_logos.py to include navigation link automatically
"""

with open('add_engagement_and_logos.py', 'r') as f:
    content = f.read()

# Find where it generates the HTML header and add nav link
nav_code = '''        <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #424245;">
            <a href="../dossier.html" style="
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                background: #0a84ff;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
                transition: all 0.2s ease;
            " onmouseover="this.style.background='#409cff'" onmouseout="this.style.background='#0a84ff'">
                ← Back to Main Dossier
            </a>
        </div>
'''

# Insert after the timestamp line in the HTML
old_line = '        <p style="color: #a1a1a6;">Generated: {data[\'date\'][:10]} • With Engagement & Logos</p>'
new_line = old_line + '\n' + nav_code

content = content.replace(old_line, new_line)

with open('add_engagement_and_logos.py', 'w') as f:
    f.write(content)

print("✅ Updated add_engagement_and_logos.py to include nav link automatically")
