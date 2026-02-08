#!/usr/bin/env python3
"""
HTML Generator for Daily Digest - FIXED VERSION
"""

import os
import subprocess
from datetime import datetime

class DigestHTMLGenerator:
    def __init__(self):
        self.github_repo = "daily-dossier"
        self.github_user = "DiamondDeals"
        self.archive_dir = "Archive"
        self.current_html = "dossier.html"
        
    def markdown_to_html(self, markdown_content: str, title: str = "Daily Business Dossier") -> str:
        """Convert markdown to HTML properly"""
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p PST")
        
        # Split into lines for processing
        lines = markdown_content.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('')
                continue
            
            # Headers
            if stripped.startswith('# '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h1>{stripped[2:]}</h1>')
            elif stripped.startswith('## '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h2>{stripped[3:]}</h2>')
            elif stripped.startswith('### '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h3>{stripped[4:]}</h3>')
            
            # Bullet points
            elif stripped.startswith('- '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                content = stripped[2:]
                # Make links clickable
                import re
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
                html_lines.append(f'<li>{content}</li>')
            
            # Table rows
            elif '|' in stripped and not stripped.startswith('|---'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                # Skip for now, tables handled separately
                continue
            
            # Regular paragraphs
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                
                content = stripped
                # Bold
                import re
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                # Links
                content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
                
                if content and content != '---':
                    html_lines.append(f'<p>{content}</p>')
        
        if in_list:
            html_lines.append('</ul>')
        
        html_body = '\n'.join(html_lines)
        
        # Full HTML with Apple styling
        full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1d1d1f;
            background: #ffffff;
            padding: 20px;
            font-size: 17px;
        }}
        
        .container {{
            max-width: 980px;
            margin: 0 auto;
            background: #fbfbfd;
            border-radius: 18px;
            padding: 60px 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        }}
        
        header {{
            border-bottom: 1px solid #d2d2d7;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        h1 {{
            color: #1d1d1f;
            font-size: 48px;
            font-weight: 600;
            letter-spacing: -0.5px;
            margin-bottom: 12px;
        }}
        
        .timestamp {{
            color: #86868b;
            font-size: 15px;
            font-weight: 400;
        }}
        
        h2 {{
            color: #1d1d1f;
            font-size: 32px;
            font-weight: 600;
            margin-top: 48px;
            margin-bottom: 20px;
            letter-spacing: -0.3px;
        }}
        
        h3 {{
            color: #1d1d1f;
            font-size: 24px;
            font-weight: 600;
            margin-top: 32px;
            margin-bottom: 16px;
        }}
        
        p {{
            margin-bottom: 16px;
            color: #1d1d1f;
            line-height: 1.6;
        }}
        
        ul {{
            margin-left: 24px;
            margin-bottom: 24px;
        }}
        
        li {{
            margin-bottom: 12px;
            color: #1d1d1f;
            line-height: 1.5;
        }}
        
        strong {{
            color: #1d1d1f;
            font-weight: 600;
        }}
        
        a {{
            color: #0071e3;
            text-decoration: none;
            transition: color 0.15s ease;
        }}
        
        a:hover {{
            color: #0077ed;
            text-decoration: underline;
        }}
        
        footer {{
            margin-top: 60px;
            padding-top: 24px;
            border-top: 1px solid #d2d2d7;
            text-align: center;
            color: #86868b;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 {title}</h1>
            <p class="timestamp">Last Updated: {timestamp}</p>
            <p class="timestamp">Auto-updates at 6 AM & 5 PM PST</p>
        </header>
        
        <main>
{html_body}
        </main>
        
        <footer>
            <p>Generated by <a href="https://moltbook.com/u/BishopLizard" target="_blank">Bishop</a> • Powered by OpenClaw</p>
            <p><a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Archive">View Archive</a></p>
        </footer>
    </div>
</body>
</html>'''
        
        return full_html
    
    def archive_current_html(self):
        """Archive current HTML"""
        if not os.path.exists(self.current_html):
            return None
        
        os.makedirs(self.archive_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(self.archive_dir, f"dossier_{timestamp}.html")
        subprocess.run(['cp', self.current_html, archive_path], check=True)
        print(f"📦 Archived to: {archive_path}")
        return archive_path
    
    def save_html(self, html_content: str):
        """Save HTML"""
        with open(self.current_html, 'w') as f:
            f.write(html_content)
        print(f"✅ Saved: {self.current_html}")
    
    def deploy_to_github(self):
        """Deploy to GitHub"""
        try:
            subprocess.run(['git', 'add', 'dossier.html', 'Archive'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Update: {datetime.now().strftime("%Y-%m-%d %I:%M %p PST")}'], check=True)
            subprocess.run(['git', 'push'], check=True)
            print(f"✅ Deployed to GitHub Pages")
            return f"https://{self.github_user}.github.io/{self.github_repo}/dossier.html"
        except Exception as e:
            print(f"❌ Deploy failed: {e}")
            return None

if __name__ == "__main__":
    gen = DigestHTMLGenerator()
    with open('Exports/complete_digest_now.md', 'r') as f:
        md = f.read()
    gen.archive_current_html()
    html = gen.markdown_to_html(md)
    gen.save_html(html)
    gen.deploy_to_github()
