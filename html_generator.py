#!/usr/bin/env python3
"""
HTML Generator for Daily Digest
Converts markdown digest to HTML and deploys to GitHub Pages
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class DigestHTMLGenerator:
    def __init__(self):
        self.github_repo = "daily-dossier"
        self.github_user = "DiamondDeals"
        self.archive_dir = "Archive"
        self.current_html = "dossier.html"
        
    def markdown_to_html(self, markdown_content: str, title: str = "Daily Business Dossier") -> str:
        """Convert markdown digest to HTML with Apple-style design"""
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p PST")
        
        # Simple markdown to HTML conversion
        html = markdown_content
        
        # Headers
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n')
        
        # Bold
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Links - CRITICAL: Make all URLs clickable
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html)
        html = re.sub(r'(https?://[^\s<]+)', r'<a href="\1" target="_blank">\1</a>', html)
        
        # Bullet points
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'((?:<li>.*</li>\n)+)', r'<ul>\n\1</ul>\n', html)
        
        # Paragraphs
        lines = html.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            if line.startswith('<'):
                formatted_lines.append(line)
                in_list = '<ul>' in line or '<li>' in line
            elif line.strip():
                if not in_list:
                    formatted_lines.append(f'<p>{line}</p>')
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        html = '\n'.join(formatted_lines)
        
        # Apple-style HTML template (NO GRADIENTS!)
        full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3600">
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
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }}
        
        th {{
            background: #f5f5f7;
            color: #1d1d1f;
            font-weight: 600;
            text-align: left;
            padding: 16px;
            font-size: 15px;
        }}
        
        td {{
            padding: 16px;
            border-top: 1px solid #d2d2d7;
            color: #1d1d1f;
        }}
        
        .platform-section {{
            background: #ffffff;
            padding: 24px;
            border-radius: 12px;
            margin: 24px 0;
            border: 1px solid #d2d2d7;
        }}
        
        footer {{
            margin-top: 60px;
            padding-top: 24px;
            border-top: 1px solid #d2d2d7;
            text-align: center;
            color: #86868b;
            font-size: 14px;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #d2d2d7;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 {title}</h1>
            <p class="timestamp">Last Updated: {timestamp}</p>
            <p class="timestamp">Auto-refreshes hourly • Updates at 6 AM & 5 PM PST</p>
        </header>
        
        <main>
{html}
        </main>
        
        <footer>
            <p>Generated by Bishop • Powered by OpenClaw</p>
            <p><a href="https://github.com/DiamondDeals/daily-dossier/tree/master/Archive">View Archive</a></p>
        </footer>
    </div>
</body>
</html>'''
        
        return full_html
    
    def archive_current_html(self):
        """Archive the current HTML file with timestamp"""
        if not os.path.exists(self.current_html):
            return None
        
        os.makedirs(self.archive_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"dossier_{timestamp}.html"
        archive_path = os.path.join(self.archive_dir, archive_filename)
        
        # Copy current to archive
        subprocess.run(['cp', self.current_html, archive_path], check=True)
        
        print(f"📦 Archived current HTML to: {archive_path}")
        return archive_path
    
    def save_html(self, html_content: str):
        """Save HTML to file"""
        with open(self.current_html, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Saved HTML to: {self.current_html}")
    
    def deploy_to_github(self):
        """Deploy to GitHub Pages"""
        try:
            # Git commands (uses configured credentials)
            commands = [
                ['git', 'add', 'dossier.html', 'Archive'],
                ['git', 'commit', '-m', f'Update digest: {datetime.now().strftime("%Y-%m-%d %I:%M %p PST")}'],
                ['git', 'push']
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0 and 'nothing to commit' not in result.stdout:
                    print(f"⚠️ Git command failed: {' '.join(cmd)}")
                    print(f"   Error: {result.stderr}")
            
            url = f"https://{self.github_user}.github.io/{self.github_repo}/dossier.html"
            print(f"✅ Deployed to GitHub Pages: {url}")
            return url
            
        except Exception as e:
            print(f"❌ GitHub deployment failed: {str(e)}")
            return None

def main():
    generator = DigestHTMLGenerator()
    markdown_content = "# Test"
    generator.archive_current_html()
    html = generator.markdown_to_html(markdown_content)
    generator.save_html(html)
    generator.deploy_to_github()

if __name__ == "__main__":
    main()
