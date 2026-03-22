#!/usr/bin/env python3
"""
HTML Generator for Daily Digest - Apple Style with Dark Mode
"""

import os
import shutil
import subprocess
from datetime import datetime

class DigestHTMLGenerator:
    def __init__(self):
        self.github_repo = "daily-dossier"
        self.github_user = "DiamondDeals"
        self.archive_dir = "Archive"
        self.current_html = "dossier.html"
        
    def markdown_to_html(self, markdown_content: str, title: str = "Daily Business Dossier") -> str:
        """Convert markdown to HTML with dark mode"""
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p PST")
        
        # Parse markdown
        lines = markdown_content.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
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
                import re
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
                html_lines.append(f'<li>{content}</li>')
            
            # Table rows (must start with |)
            elif stripped.startswith('|') and '|' in stripped[1:] and not stripped.startswith('|---'):
                continue
            
            # Regular paragraphs
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
                    
                    # Check if this is a numbered title line (e.g., "1. Title...")
                    numbered_match = re.match(r'^(\d+\.)\s+(.+)', content)
                    if numbered_match:
                        # This is a title line - wrap number + title in <strong>
                        content = f'<strong>{numbered_match.group(1)} {numbered_match.group(2)}</strong>'
                    else:
                        # Apply bold markdown
                        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                    
                    # Only apply link regex if there are no existing <a> tags
                    if '<a href=' not in content:
                        content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
                    
                    if content and content != '---':
                        html_lines.append(f'<p>{content}</p>')
        
        if in_list:
            html_lines.append('</ul>')
        
        html_body = '\n'.join(html_lines)
        
        # Full HTML with Apple styling + Dark Mode
        full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PLACEHOLDER"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-PLACEHOLDER', {{
    'send_page_view': true,
    'anonymize_ip': true
  }});

  // Track link clicks
  document.addEventListener('click', function(e) {{
    if (e.target.tagName === 'A' && e.target.href) {{
      gtag('event', 'click', {{
        'event_category': 'outbound',
        'event_label': e.target.href,
        'transport_type': 'beacon'
      }});
    }}
  }});

  // Track dark mode toggle
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {{
    themeToggle.addEventListener('click', function() {{
      gtag('event', 'toggle_theme', {{
        'event_category': 'engagement',
        'event_label': document.documentElement.getAttribute('data-theme') || 'dark'
      }});
    }});
  }}
</script>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-primary: #1d1d1f;
            --bg-secondary: #2d2d2f;
            --text-primary: #f5f5f7;
            --text-secondary: #a1a1a6;
            --accent: #0a84ff;
            --accent-hover: #409cff;
            --border: #424245;
            --shadow: rgba(0, 0, 0, 0.5);
        }}
        
        [data-theme="light"] {{
            --bg-primary: #ffffff;
            --bg-secondary: #fbfbfd;
            --text-primary: #1d1d1f;
            --text-secondary: #86868b;
            --accent: #0071e3;
            --accent-hover: #0077ed;
            --border: #d2d2d7;
            --shadow: rgba(0, 0, 0, 0.07);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-primary);
            padding: 20px;
            font-size: 17px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}
        
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            color: var(--text-primary);
            transition: all 0.3s ease;
            z-index: 1000;
        }}
        
        .theme-toggle:hover {{
            background: var(--accent);
            color: white;
            transform: scale(1.05);
        }}

        .scroll-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--accent);
            color: white;
            border: none;
            font-size: 22px;
            cursor: pointer;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.4);
        }}
        .scroll-top.visible {{
            opacity: 1;
            pointer-events: auto;
        }}
        .scroll-top:hover {{
            transform: scale(1.1);
        }}
        
        .container {{
            max-width: 980px;
            margin: 0 auto;
            background: var(--bg-secondary);
            border-radius: 18px;
            padding: 60px 40px;
            box-shadow: 0 4px 6px var(--shadow);
        }}
        
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        h1 {{
            color: var(--text-primary);
            font-size: 36px;
            font-weight: 600;
            letter-spacing: -0.4px;
            margin-bottom: 12px;
        }}
        
        .timestamp {{
            color: var(--text-secondary);
            font-size: 15px;
            font-weight: 400;
        }}
        
        h2 {{
            color: var(--accent);
            font-size: 36px;
            font-weight: 800;
            margin-top: 50px;
            margin-bottom: 24px;
            letter-spacing: -0.4px;
            border-left: 5px solid var(--accent);
            padding-left: 20px;
            text-transform: uppercase;
        }}
        
        h3 {{
            color: var(--text-primary);
            font-size: 24px;
            font-weight: 800;
            margin-top: 32px;
            margin-bottom: 16px;
        }}
        
        p {{
            margin-bottom: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 15px;
        }}
        
        p:has(strong) {{
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 18px;
        }}
        
        ul {{
            margin-left: 24px;
            margin-bottom: 24px;
        }}
        
        li {{
            margin-bottom: 12px;
            color: var(--text-primary);
            line-height: 1.5;
        }}
        
        strong {{
            display: inline;
            font-size: 22px;
            font-weight: 800;
            color: var(--accent);
        }}
        
        a {{
            color: var(--accent);
            text-decoration: none;
            transition: color 0.15s ease;
        }}
        
        a:hover {{
            color: var(--accent-hover);
            text-decoration: underline;
        }}
        
        footer {{
            margin-top: 60px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-secondary);
            font-size: 14px;
        }}

        /* Bookmark system */
        .bookmark-btn {{
            cursor: pointer;
            font-size: 18px;
            margin-left: 10px;
            color: #ffd60a;
            opacity: 0.5;
            transition: all 0.15s ease;
            border: none;
            background: none;
            padding: 2px 4px;
            vertical-align: middle;
        }}
        .bookmark-btn:hover {{ opacity: 1; }}
        .bookmark-btn.saved {{ opacity: 1; color: #ffd60a; }}

        .saved-panel-toggle {{
            position: fixed;
            top: 20px;
            right: 140px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            color: var(--text-primary);
            transition: all 0.3s ease;
            z-index: 1000;
        }}
        .saved-panel-toggle:hover {{
            background: var(--accent);
            color: white;
        }}

        .saved-panel {{
            display: none;
            position: fixed;
            top: 0; right: 0;
            width: 420px;
            height: 100vh;
            background: var(--bg-secondary);
            border-left: 1px solid var(--border);
            z-index: 2000;
            overflow-y: auto;
            padding: 24px;
            box-shadow: -4px 0 20px var(--shadow);
        }}
        .saved-panel.open {{ display: block; }}

        .saved-panel h2 {{
            font-size: 22px;
            margin: 0 0 8px 0;
            padding: 0;
            border: none;
            text-transform: none;
        }}
        .saved-panel .close-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 24px;
            cursor: pointer;
        }}
        .saved-item {{
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }}
        .saved-item a {{
            font-weight: 600;
            font-size: 15px;
            display: block;
            margin-bottom: 4px;
        }}
        .saved-item .saved-meta {{
            font-size: 12px;
            color: var(--text-secondary);
        }}
        .saved-item .remove-btn {{
            cursor: pointer;
            color: var(--text-secondary);
            font-size: 12px;
            border: none;
            background: none;
            padding: 2px 6px;
            margin-top: 4px;
        }}
        .saved-item .remove-btn:hover {{ color: #ff453a; }}
        .saved-empty {{
            color: var(--text-secondary);
            font-style: italic;
            margin-top: 20px;
        }}
        .sv-filter {{
            padding: 4px 10px; border-radius: 12px; border: 1px solid var(--border);
            background: none; color: var(--text-secondary); cursor: pointer; font-size: 12px;
        }}
        .sv-filter:hover, .sv-filter.active {{
            background: var(--accent); color: white; border-color: var(--accent);
        }}
        .sv-group-header {{
            font-size: 13px; font-weight: 700; color: var(--accent);
            margin: 16px 0 6px 0; padding-bottom: 4px; border-bottom: 1px solid var(--border);
        }}
    </style>
</head>
<body data-theme="dark">
    <button class="theme-toggle" onclick="toggleTheme()">☀️ Light Mode</button>
    <button class="saved-panel-toggle" onclick="toggleSavedPanel()">Saved (0)</button>
    <button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="Back to top">&uarr;</button>

    <div class="saved-panel" id="savedPanel">
        <button class="close-btn" onclick="toggleSavedPanel()">&times;</button>
        <h2>Saved Items</h2>
        <p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 8px;">
            Bookmarks persist in your browser across visits.
        </p>
        <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap;">
            <button class="sv-filter active" onclick="svFilter('all',this)">All</button>
            <button class="sv-filter" onclick="svFilter('date',this)">By Date</button>
            <button class="sv-filter" onclick="svFilter('platform',this)">By Platform</button>
        </div>
        <input id="svSearch" type="text" placeholder="Search saved..." oninput="renderSavedList()"
               style="width:100%;padding:8px 12px;border-radius:8px;border:1px solid #424245;
               background:#1d1d1f;color:#f5f5f7;font-size:13px;margin-bottom:12px;box-sizing:border-box;">
        <div id="savedList"></div>
    </div>

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
    
    <script>
        // Theme toggle functionality
        function toggleTheme() {{
            const body = document.body;
            const button = document.querySelector('.theme-toggle');
            const currentTheme = body.getAttribute('data-theme');
            
            if (currentTheme === 'dark') {{
                body.setAttribute('data-theme', 'light');
                button.textContent = '🌙 Dark Mode';
                localStorage.setItem('theme', 'light');
            }} else {{
                body.setAttribute('data-theme', 'dark');
                button.textContent = '☀️ Light Mode';
                localStorage.setItem('theme', 'dark');
            }}
        }}
        
        // Scroll-to-top button visibility
        window.addEventListener('scroll', function() {{
            document.getElementById('scrollTop').classList.toggle('visible', window.scrollY > 400);
        }});

        // Load saved theme (default to dark)
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);
        document.querySelector('.theme-toggle').textContent = savedTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';

        // ---- Bookmark / Read Later System ----
        function getBookmarks() {{
            try {{ return JSON.parse(localStorage.getItem('dossier_bookmarks') || '[]'); }}
            catch {{ return []; }}
        }}
        function saveBookmarks(bm) {{
            localStorage.setItem('dossier_bookmarks', JSON.stringify(bm));
            updateBadge();
        }}
        function updateBadge() {{
            const count = getBookmarks().length;
            document.querySelector('.saved-panel-toggle').textContent = 'Saved (' + count + ')';
        }}
        function toggleSavedPanel() {{
            const panel = document.getElementById('savedPanel');
            panel.classList.toggle('open');
            if (panel.classList.contains('open')) renderSavedList();
        }}
        var _svMode = 'all';
        function svFilter(mode, btn) {{
            _svMode = mode;
            document.querySelectorAll('.sv-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderSavedList();
        }}
        function renderSavedList() {{
            const list = document.getElementById('savedList');
            let bm = getBookmarks();
            const q = (document.getElementById('svSearch') || {{}}).value || '';
            if (q) bm = bm.filter(b => (b.title + ' ' + (b.section||'')).toLowerCase().includes(q.toLowerCase()));
            if (bm.length === 0) {{
                list.innerHTML = '<p class="saved-empty">' + (q ? 'No matches.' : 'No saved items yet. Click the star next to any item to save it.') + '</p>';
                return;
            }}
            let html = '<div style="margin-bottom:12px;display:flex;gap:8px;flex-wrap:wrap;">';
            html += '<button onclick="exportBookmarks()" style="padding:5px 10px;border-radius:8px;border:1px solid #424245;background:none;color:#0a84ff;cursor:pointer;font-size:12px;">Export</button>';
            html += '<label style="padding:5px 10px;border-radius:8px;border:1px solid #424245;color:#0a84ff;cursor:pointer;font-size:12px;">Import<input type="file" accept=".json" onchange="importBookmarks(event)" style="display:none;"></label>';
            html += '<button onclick="if(confirm(\'Clear all saved items?\')){{saveBookmarks([]);renderSavedList();document.querySelectorAll(\'.bookmark-btn\').forEach(b=>{{b.classList.remove(\'saved\');b.textContent=\'\\u2606\'}})}}" style="padding:5px 10px;border-radius:8px;border:1px solid #ff453a;background:none;color:#ff453a;cursor:pointer;font-size:12px;">Clear All</button>';
            html += '</div>';
            if (_svMode === 'date') {{
                const groups = {{}};
                bm.forEach((item, i) => {{ const d = item.date || 'Unknown'; if (!groups[d]) groups[d] = []; groups[d].push({{item, i}}); }});
                Object.keys(groups).sort().reverse().forEach(d => {{
                    html += '<div class="sv-group-header">' + d + ' (' + groups[d].length + ')</div>';
                    groups[d].forEach(({{item, i}}) => {{ html += svItemHtml(item, i); }});
                }});
            }} else if (_svMode === 'platform') {{
                const groups = {{}};
                bm.forEach((item, i) => {{ const s = item.section || 'Other'; if (!groups[s]) groups[s] = []; groups[s].push({{item, i}}); }});
                Object.keys(groups).sort().forEach(s => {{
                    html += '<div class="sv-group-header">' + s + ' (' + groups[s].length + ')</div>';
                    groups[s].forEach(({{item, i}}) => {{ html += svItemHtml(item, i); }});
                }});
            }} else {{
                bm.forEach((item, i) => {{ html += svItemHtml(item, i); }});
            }}
            list.innerHTML = html;
        }}
        function svItemHtml(item, i) {{
            return '<div class="saved-item"><a href="' + item.url + '" target="_blank">' + item.title + '</a>' +
                '<span class="saved-meta">' + (item.section || '') + ' &middot; Saved ' + (item.date || '') + '</span>' +
                '<br><button class="remove-btn" onclick="removeBookmark(' + i + ')">&times; Remove</button></div>';
        }}
        function exportBookmarks() {{
            const bm = getBookmarks();
            const blob = new Blob([JSON.stringify(bm, null, 2)], {{type: 'application/json'}});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'dossier_saved_items.json';
            a.click();
        }}
        function importBookmarks(evt) {{
            const file = evt.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {{
                try {{
                    const imported = JSON.parse(e.target.result);
                    if (!Array.isArray(imported)) {{ alert('Invalid file'); return; }}
                    const bm = getBookmarks();
                    // Merge without duplicates
                    const existing = new Set(bm.map(b => b.title));
                    let added = 0;
                    imported.forEach(item => {{
                        if (!existing.has(item.title)) {{
                            bm.push(item);
                            added++;
                        }}
                    }});
                    saveBookmarks(bm);
                    renderSavedList();
                    // Sync star buttons
                    document.querySelectorAll('.bookmark-btn').forEach(btn => {{
                        const t = btn.getAttribute('data-title');
                        const s = bm.some(b => b.title === t);
                        btn.classList.toggle('saved', s);
                        btn.textContent = s ? '\u2605' : '\u2606';
                    }});
                    alert('Imported ' + added + ' new items (' + imported.length + ' total in file)');
                }} catch {{ alert('Error reading file'); }}
            }};
            reader.readAsText(file);
        }}
        function removeBookmark(idx) {{
            const bm = getBookmarks();
            bm.splice(idx, 1);
            saveBookmarks(bm);
            renderSavedList();
            // Update all bookmark button states
            document.querySelectorAll('.bookmark-btn').forEach(btn => {{
                const title = btn.getAttribute('data-title');
                btn.classList.toggle('saved', bm.some(b => b.title === title));
                btn.textContent = bm.some(b => b.title === title) ? '\u2605' : '\u2606';
            }});
        }}
        function toggleBookmark(btn) {{
            const title = btn.getAttribute('data-title');
            const url = btn.getAttribute('data-url');
            const section = btn.getAttribute('data-section');
            const bm = getBookmarks();
            const exists = bm.findIndex(b => b.title === title);
            if (exists >= 0) {{
                bm.splice(exists, 1);
                btn.classList.remove('saved');
                btn.textContent = '\u2606';
            }} else {{
                bm.push({{ title, url, section, date: new Date().toLocaleDateString() }});
                btn.classList.add('saved');
                btn.textContent = '\u2605';
            }}
            saveBookmarks(bm);
        }}

        // Inject bookmark buttons into every numbered item
        document.addEventListener('DOMContentLoaded', function() {{
            const bm = getBookmarks();
            updateBadge();

            // Find all strong elements that look like numbered titles
            document.querySelectorAll('p > strong').forEach(el => {{
                const text = el.textContent;
                const match = text.match(/^\d+\.\s+(.+)/);
                if (!match) return;

                const title = match[1];
                // Find the URL in the next sibling list
                let url = '';
                let section = '';
                let sibling = el.parentElement.nextElementSibling;
                while (sibling) {{
                    if (sibling.tagName === 'UL') {{
                        const links = sibling.querySelectorAll('a');
                        if (links.length > 0) url = links[links.length - 1].href;
                        break;
                    }}
                    sibling = sibling.nextElementSibling;
                }}
                // Get section from nearest h2
                let h2 = el.parentElement.previousElementSibling;
                while (h2 && h2.tagName !== 'H2') h2 = h2.previousElementSibling;
                if (h2) section = h2.textContent;

                const isSaved = bm.some(b => b.title === title);
                const btn = document.createElement('button');
                btn.className = 'bookmark-btn' + (isSaved ? ' saved' : '');
                btn.textContent = isSaved ? '\u2605' : '\u2606';
                btn.setAttribute('data-title', title);
                btn.setAttribute('data-url', url);
                btn.setAttribute('data-section', section);
                btn.onclick = function() {{ toggleBookmark(this); }};
                el.appendChild(btn);
            }});
        }});
    </script>
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
        shutil.copy2(self.current_html, archive_path)
        print(f"📦 Archived to: {archive_path}")
        return archive_path
    
    def save_html(self, html_content: str):
        """Save HTML"""
        with open(self.current_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Saved: {self.current_html}")
    
    def deploy_to_github(self):
        """Deploy to GitHub - includes dossier, database, and daily archives"""
        try:
            subprocess.run(['git', 'add', 'dossier.html', 'Archive', 'Database', 'Daily',
                            'html_generator.py', 'youtube_ai_channels.json',
                            'rss_news_feeds.json', 'bluesky_scanner.py',
                            'health_tracker.py', 'youtube_ai_monitor.py',
                            'run_full_digest.py', 'add_footer_links.py'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Update: {datetime.now().strftime("%Y-%m-%d %I:%M %p PST")}'], check=True)
            subprocess.run(['git', 'push'], check=True)
            print(f"✅ Deployed to GitHub Pages")
            return f"https://{self.github_user}.github.io/{self.github_repo}/dossier.html"
        except Exception as e:
            print(f"❌ Deploy failed: {e}")
            return None

if __name__ == "__main__":
    gen = DigestHTMLGenerator()
    with open('Exports/complete_everything.md', 'r') as f:
        md = f.read()
    gen.archive_current_html()
    html = gen.markdown_to_html(md)
    gen.save_html(html)
    gen.deploy_to_github()
