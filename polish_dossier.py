#!/usr/bin/env python3
"""
Polish the dossier design for sharing
"""

# Read current HTML
with open('dossier.html', 'r') as f:
    html = f.read()

# Add meta tags for sharing
meta_tags = '''
    <meta property="og:title" content="Daily Business Dossier - 700+ Opportunities">
    <meta property="og:description" content="Curated business opportunities, AI updates, and health insights from 6 platforms. Updated daily.">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="description" content="700+ daily opportunities from Reddit, Twitter, YouTube, Moltbook, Health forums, and RSS feeds. All in one place.">'''

# Insert after charset
html = html.replace('<meta name="viewport"', meta_tags + '\n    <meta name="viewport"')

# Add sharing section in header
sharing_section = '''
        <div style="margin-top: 20px; padding: 15px; background: rgba(10, 132, 255, 0.1); border-radius: 8px; border-left: 3px solid var(--accent);">
            <p style="margin: 0; font-size: 14px; color: var(--text-secondary);">
                📁 <a href="Database/complete_with_titles.html" style="color: var(--accent); font-weight: 600;">View Complete Archive with Summaries →</a>
            </p>
            <p style="margin: 8px 0 0 0; font-size: 13px; color: var(--text-secondary);">
                🔄 Automatically updated at 6 AM & 5 PM PST • All data stored permanently on GitHub
            </p>
        </div>'''

# Insert after timestamp
html = html.replace('</header>', sharing_section + '\n        </header>')

# Save
with open('dossier.html', 'w') as f:
    f.write(html)

print("✅ Polished dossier for sharing")
