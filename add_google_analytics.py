#!/usr/bin/env python3
"""
Add Google Analytics tracking to all HTML pages
import os
For now, using placeholder - will update with real GA4 ID
"""

import sys

# Placeholder GA4 Measurement ID - will be updated after creating property
GA4_ID = "G-PLACEHOLDER"

if len(sys.argv) > 1:
    GA4_ID = sys.argv[1]

GA_CODE = f'''
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA4_ID}', {{
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
'''

# Add to html_generator.py
with open('html_generator.py', 'r') as f:
    content = f.read()

# Insert GA code after <head> tag
if GA4_ID not in content and '<head>' in content:
    content = content.replace('<head>', '<head>' + GA_CODE, 1)
    
    with open('html_generator.py', 'w') as f:
        f.write(content)
    
    print(f"✅ Added Google Analytics ({GA4_ID}) to html_generator.py")
else:
    print(f"ℹ️  GA already present or placeholder")

# Also add to stats.html
if os.path.exists('stats.html'):
    with open('stats.html', 'r') as f:
        stats_html = f.read()
    
    if GA4_ID not in stats_html and '<head>' in stats_html:
        stats_html = stats_html.replace('<head>', '<head>' + GA_CODE, 1)
        
        with open('stats.html', 'w') as f:
            f.write(stats_html)
        
        print(f"✅ Added Google Analytics to stats.html")

print("\n📝 TO COMPLETE GA4 SETUP:")
print("1. Go to https://analytics.google.com/")
print("2. Log in with drew@poolhallpros.com")
print("3. Create property: 'Daily Business Dossier'")
print("4. Copy Measurement ID (G-XXXXXXXXXX)")
print("5. Run: python3 add_google_analytics.py G-XXXXXXXXXX")
print("6. Commit and push to GitHub")
