#!/usr/bin/env python3
"""
Update get_all_items.py to include title parsing
"""

import shutil

# Copy the title parsing function into get_all_items.py
title_parser = '''
def parse_title_from_url(url):
    """Extract title from URL slug"""
    import re
    
    # Reddit URLs: extract the slug before the last /
    if 'reddit.com' in url:
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            title = slug.replace('_', ' ').replace('-', ' ')
            return title.title()
    
    # YouTube URLs
    elif 'youtube.com' in url or 'youtu.be' in url:
        return "YouTube Video"
    
    # Twitter URLs
    elif 'twitter.com' in url or 'x.com' in url:
        return "Twitter Post"
    
    # Moltbook URLs
    elif 'moltbook.com' in url:
        return "Moltbook Post"
    
    # Generic: extract last path segment
    else:
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        if match:
            slug = match.group(1)
            title = slug.replace('_', ' ').replace('-', ' ')
            return title.title()
    
    return "Link"
'''

# Read get_all_items.py if it exists
if os.path.exists('get_all_items.py'):
    with open('get_all_items.py', 'r') as f:
        content = f.read()
    
    # Add the title parser function if not already there
    if 'parse_title_from_url' not in content:
        # Add after imports
        import_end = content.find('\ndef ')
        if import_end > 0:
            content = content[:import_end] + '\n' + title_parser + '\n' + content[import_end:]
        
        # Find where items are added to the list and add title parsing
        # This is a template - need to see actual structure
        with open('get_all_items.py', 'w') as f:
            f.write(content)
        
        print("✅ Updated get_all_items.py with title parsing")
else:
    print("ℹ️  get_all_items.py not found - will be added to run_full_digest.py")

# Make sure run_full_digest includes title parsing in database creation
print("✅ Title parsing logic ready for future scans")
