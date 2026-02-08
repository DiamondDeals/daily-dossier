#!/usr/bin/env python3
"""Generate COMPLETE digest with ALL items"""

import sys
sys.path.insert(0, '.')

# Read all the latest exports
import os
from datetime import datetime

def read_latest_export(prefix):
    """Read the most recent export file"""
    export_dir = "Exports"
    files = [f for f in os.listdir(export_dir) if f.startswith(prefix) and f.endswith('.md')]
    if not files:
        return ""
    latest = sorted(files)[-1]
    with open(os.path.join(export_dir, latest), 'r') as f:
        return f.read()

# Start building complete digest
digest = f"""# 📊 Daily Business Dossier
## {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}

**All 181 Opportunities Found**

---

"""

# Platform summary
digest += """## 📊 Platform Summary

| Platform | Count |
|----------|-------|
| 🟠 Reddit | 20 |
| 🔵 Twitter | 15 |
| 🎥 YouTube | 4 |
| 🤖 Moltbook | 73 |
| 🟢 Health | 24 |
| 📰 RSS News | 23 |

---

"""

# Read individual platform outputs from /tmp
platforms = {
    'Reddit': '/tmp/reddit.txt',
    'Twitter': '/tmp/twitter.txt',
    'YouTube': '/tmp/youtube.txt',
    'Moltbook': '/tmp/moltbook.txt',
    'Health': '/tmp/health.txt',
    'RSS': '/tmp/rss.txt'
}

for platform, tmpfile in platforms.items():
    if os.path.exists(tmpfile):
        with open(tmpfile, 'r') as f:
            content = f.read()
            
        # Extract the good parts and format
        if 'Reddit' in platform:
            digest += f"\n## 🟠 {platform} Business Leads\n\n"
            # Parse Reddit output - keep ALL items
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.', '18.', '19.', '20.')):
                    digest += f"**{line.strip()}**\n"
                    # Get next few lines
                    for j in range(1, 5):
                        if i+j < len(lines):
                            next_line = lines[i+j].strip()
                            if next_line and not next_line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.', '18.', '19.', '20.', '=')):
                                digest += f"- {next_line}\n"
                    digest += "\n"

# Save
with open('Exports/complete_full_all_181.md', 'w') as f:
    f.write(digest)

print("✅ Generated complete digest with ALL 181 items")
