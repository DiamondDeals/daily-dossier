#!/usr/bin/env python3
"""
Fix get_all_items.py to include all platforms
"""

import re

# Read current script
with open('get_all_items.py', 'r') as f:
    content = f.read()

# After the Twitter count line, add code to parse Twitter items
twitter_code = '''twitter_count = 15  # Keep existing
print(f"✅ Twitter total: {twitter_count}")
print()

# Parse Twitter from /tmp/twitter.txt
try:
    with open('/tmp/twitter.txt', 'r') as f:
        twitter_text = f.read()
    for line in twitter_text.split('\\n'):
        if line.strip().startswith('https://'):
            url = line.strip().split()[0]
            if 'twitter.com' in url or 'x.com' in url:
                all_items.append({'platform': 'twitter', 'url': url})
except:
    pass
'''

# Replace Twitter section
content = re.sub(
    r"twitter_count = 15.*?print\(f'✅ Twitter total: {twitter_count}'\)\nprint\(\)",
    twitter_code.strip(),
    content,
    flags=re.DOTALL
)

# After YouTube count, add YouTube parsing
youtube_code = '''youtube_count = 4  # Keep existing (only 4 new in last 48h)
print(f"✅ YouTube total: {youtube_count}")
print()

# Parse YouTube from /tmp/youtube.txt
try:
    with open('/tmp/youtube.txt', 'r') as f:
        youtube_text = f.read()
    import re as regex
    urls = regex.findall(r'https://www\\.youtube\\.com/watch\\?v=[^\\s]+', youtube_text)
    for url in urls:
        all_items.append({'platform': 'youtube', 'url': url})
except:
    pass
'''

content = re.sub(
    r"youtube_count = 4.*?print\(f'✅ YouTube total: {youtube_count}'\)\nprint\(\)",
    youtube_code.strip(),
    content,
    flags=re.DOTALL
)

# After Moltbook count, add Moltbook parsing
moltbook_code = '''moltbook_count = 73
print(f"✅ Moltbook total: {moltbook_count}")
print()

# Parse Moltbook from /tmp/moltbook.txt
try:
    with open('/tmp/moltbook.txt', 'r') as f:
        moltbook_text = f.read()
    import re as regex
    urls = regex.findall(r'https://moltbook\\.com/post/[^\\s]+', moltbook_text)
    for url in urls:
        all_items.append({'platform': 'moltbook', 'url': url})
except:
    pass
'''

content = re.sub(
    r"moltbook_count = 73\nprint\(f'✅ Moltbook total: {moltbook_count}'\)\nprint\(\)",
    moltbook_code.strip(),
    content
)

# After RSS count, add RSS parsing
rss_code = '''# Already have RSS from /tmp/rss.txt
rss_count = 23
print(f"✅ RSS total: {rss_count}")
print()

# Parse RSS from /tmp/rss.txt
try:
    with open('/tmp/rss.txt', 'r') as f:
        rss_text = f.read()
    import re as regex
    urls = regex.findall(r'Link: (https://[^\\s]+)', rss_text)
    for url in urls:
        all_items.append({'platform': 'rss', 'url': url})
except:
    pass
'''

# Find RSS section
content = re.sub(
    r"# RSS.*?rss_count = \d+.*?print\(f'✅ RSS total: {rss_count}'\)\nprint\(\)",
    rss_code.strip(),
    content,
    flags=re.DOTALL
)

with open('get_all_items.py', 'w') as f:
    f.write(content)

print("✅ Fixed get_all_items.py to include all platforms")
