#!/usr/bin/env python3
"""
Upgrade all old all_items_*.html archives to the new layout:
- Page layout with archive sidebar
- Bookmark system with filter/search
- Custom dark scrollbar
- Scroll-to-top button
- Platform filter bar
"""
import re
from pathlib import Path

DB_DIR = Path('Database')

# Get all archive files
archive_files = sorted(DB_DIR.glob('all_items_*.html'))
archive_dates = []
for f in archive_files:
    if f.stem == 'all_items_latest':
        continue
    d = f.stem.replace('all_items_', '')
    archive_dates.append(d)

def build_sidebar_links(current_date):
    html = ""
    for d in sorted(archive_dates, reverse=True)[:30]:
        if d == current_date:
            html += f'<div class="arc-link current">{d} (today)</div>\n'
        else:
            html += f'<a class="arc-link" href="all_items_{d}.html">{d}</a>\n'
    return html


def build_new_html(date_str, items_html, total):
    sidebar = build_sidebar_links(date_str)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Complete Database - {date_str}</title>
    <style>
        * {{ scrollbar-width: thin; scrollbar-color: #424245 #1d1d1f; }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #1d1d1f; }}
        ::-webkit-scrollbar-thumb {{ background: #424245; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #636366; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #1d1d1f; color: #f5f5f7; padding: 20px; margin: 0; }}
        .page-layout {{ display: flex; max-width: 1280px; margin: 0 auto; gap: 24px; }}
        .main-content {{ flex: 1; min-width: 0; }}
        .archive-sidebar {{ width: 200px; flex-shrink: 0; position: sticky; top: 20px; align-self: flex-start;
                            max-height: calc(100vh - 40px); overflow-y: auto; }}
        .archive-sidebar h3 {{ color: #a1a1a6; font-size: 13px; text-transform: uppercase;
                               letter-spacing: 1px; margin: 0 0 12px 0; }}
        .arc-link {{ display: block; padding: 6px 10px; color: #0a84ff; text-decoration: none;
                     font-size: 13px; border-radius: 6px; margin-bottom: 2px; }}
        .arc-link:hover {{ background: #2d2d2f; }}
        .arc-link.current {{ color: #30d158; font-weight: bold; background: #2d2d2f; }}
        h1 {{ color: #0a84ff; }}
        h2 {{ color: #0a84ff; margin-top: 40px; }}
        .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .count {{ color: #30d158; font-size: 20px; font-weight: bold; }}
        .item {{ margin: 12px 0; padding: 15px; background: #2d2d2f; border-radius: 8px;
                 display: flex; align-items: flex-start; gap: 12px; }}
        .item-content {{ flex: 1; }}
        .platform {{ display: inline-block; padding: 4px 8px; border-radius: 4px;
                     font-size: 12px; font-weight: bold; margin-right: 10px; }}
        .reddit {{ background: #ff4500; }}
        .twitter {{ background: #0085ff; }}
        .youtube {{ background: #ff0000; }}
        .moltbook {{ background: #8b5cf6; }}
        .health {{ background: #10b981; }}
        .rss {{ background: #f59e0b; }}
        a {{ color: #0a84ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .bm {{ cursor: pointer; font-size: 20px; opacity: 0.5; border: none;
               background: none; color: #ffd60a; padding: 4px; flex-shrink: 0; }}
        .bm:hover {{ opacity: 1; }}
        .bm.saved {{ opacity: 1; color: #ffd60a; }}
        .back-link {{ color: #0a84ff; font-size: 15px; }}
        .saved-toggle {{ background: #2d2d2f; border: 1px solid #424245; border-radius: 20px;
                         padding: 8px 16px; color: #f5f5f7; cursor: pointer; font-size: 14px; }}
        .saved-toggle:hover {{ background: #0a84ff; color: white; }}
        .saved-panel {{ display: none; position: fixed; top: 0; right: 0; width: 420px;
                        height: 100vh; background: #2d2d2f; border-left: 1px solid #424245;
                        z-index: 2000; overflow-y: auto; padding: 24px;
                        box-shadow: -4px 0 20px rgba(0,0,0,0.5); }}
        .saved-panel.open {{ display: block; }}
        .saved-panel h2 {{ font-size: 22px; margin: 0 0 16px 0; }}
        .close-btn {{ position: absolute; top: 20px; right: 20px; background: none;
                      border: none; color: #a1a1a6; font-size: 24px; cursor: pointer; }}
        .si {{ padding: 12px 0; border-bottom: 1px solid #424245; }}
        .si a {{ font-weight: 600; font-size: 15px; display: block; margin-bottom: 4px; }}
        .si .meta {{ font-size: 12px; color: #a1a1a6; }}
        .si .rm {{ cursor: pointer; color: #a1a1a6; font-size: 12px; border: none;
                   background: none; padding: 2px 6px; margin-top: 4px; }}
        .si .rm:hover {{ color: #ff453a; }}
        .sv-filter {{ padding: 4px 10px; border-radius: 12px; border: 1px solid #424245;
                      background: none; color: #a1a1a6; cursor: pointer; font-size: 12px; }}
        .sv-filter:hover, .sv-filter.active {{ background: #0a84ff; color: white; border-color: #0a84ff; }}
        .sv-gh {{ font-size: 13px; font-weight: 700; color: #0a84ff;
                  margin: 16px 0 6px 0; padding-bottom: 4px; border-bottom: 1px solid #424245; }}
        .filter-bar {{ margin: 20px 0; display: flex; gap: 8px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 6px 14px; border-radius: 16px; border: 1px solid #424245;
                       background: none; color: #a1a1a6; cursor: pointer; font-size: 13px; }}
        .filter-btn:hover, .filter-btn.active {{ background: #0a84ff; color: white; border-color: #0a84ff; }}
        .scroll-top {{ position: fixed; bottom: 30px; right: 30px; width: 48px; height: 48px;
                       border-radius: 50%; background: #0a84ff; color: white; border: none;
                       font-size: 22px; cursor: pointer; z-index: 1000; opacity: 0;
                       pointer-events: none; transition: opacity 0.3s ease;
                       box-shadow: 0 2px 10px rgba(0,0,0,0.4); }}
        .scroll-top.visible {{ opacity: 1; pointer-events: auto; }}
        .scroll-top:hover {{ transform: scale(1.1); }}
        @media (max-width: 900px) {{
            .page-layout {{ flex-direction: column; }}
            .archive-sidebar {{ width: 100%; position: static; max-height: none;
                                display: flex; flex-wrap: wrap; gap: 4px; }}
            .archive-sidebar h3 {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="top-bar" style="max-width: 1280px; margin: 0 auto 20px auto;">
        <a class="back-link" href="../dossier.html">&larr; Back to Dossier</a>
        <button class="saved-toggle" onclick="togglePanel()">Saved (0)</button>
    </div>
    <button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&uarr;</button>

    <div class="page-layout">
    <div class="main-content">
    <h1>Complete Database - {date_str}</h1>
    <p class="count">Total Items: {total}</p>

    <div class="filter-bar">
        <button class="filter-btn active" onclick="filterPlatform('all', this)">All</button>
        <button class="filter-btn" onclick="filterPlatform('reddit', this)">Reddit</button>
        <button class="filter-btn" onclick="filterPlatform('twitter', this)">Bluesky</button>
        <button class="filter-btn" onclick="filterPlatform('youtube', this)">YouTube</button>
        <button class="filter-btn" onclick="filterPlatform('moltbook', this)">Moltbook</button>
        <button class="filter-btn" onclick="filterPlatform('health', this)">Health</button>
        <button class="filter-btn" onclick="filterPlatform('rss', this)">RSS</button>
    </div>

    <div class="saved-panel" id="sp">
        <button class="close-btn" onclick="togglePanel()">&times;</button>
        <h2>Saved Items</h2>
        <p style="color:#a1a1a6;font-size:12px;margin:0 0 8px 0;">Bookmarks persist across visits.</p>
        <div style="display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap;">
            <button class="sv-filter active" onclick="svF('all',this)">All</button>
            <button class="sv-filter" onclick="svF('date',this)">By Date</button>
            <button class="sv-filter" onclick="svF('platform',this)">By Platform</button>
        </div>
        <input id="svQ" type="text" placeholder="Search saved..." oninput="rList()"
               style="width:100%;padding:7px 10px;border-radius:8px;border:1px solid #424245;
               background:#1d1d1f;color:#f5f5f7;font-size:12px;margin-bottom:10px;box-sizing:border-box;">
        <div id="sl"></div>
    </div>

{items_html}

    </div><!-- end main-content -->
    <div class="archive-sidebar">
        <h3>Prior Days</h3>
        {sidebar}
    </div>
    </div><!-- end page-layout -->

<script>
function gBm(){{try{{return JSON.parse(localStorage.getItem('dossier_bookmarks')||'[]')}}catch{{return[]}}}}
function sBm(b){{localStorage.setItem('dossier_bookmarks',JSON.stringify(b));uBadge()}}
function uBadge(){{document.querySelector('.saved-toggle').textContent='Saved ('+gBm().length+')'}}
function togglePanel(){{var p=document.getElementById('sp');p.classList.toggle('open');if(p.classList.contains('open'))rList()}}
var _svM='all';
function svF(mode,btn){{_svM=mode;document.querySelectorAll('.sv-filter').forEach(b=>b.classList.remove('active'));btn.classList.add('active');rList()}}
function siHtml(m,i){{return'<div class="si"><a href="'+m.url+'" target="_blank">'+m.title+'</a><span class="meta">'+(m.section||'')+' &middot; '+(m.date||'')+'</span><br><button class="rm" onclick="rbm('+i+')">&times; Remove</button></div>'}}
function rList(){{var l=document.getElementById('sl'),b=gBm(),q=(document.getElementById('svQ')||{{}}).value||'';
if(q)b=b.filter(m=>(m.title+' '+(m.section||'')).toLowerCase().includes(q.toLowerCase()));
if(!b.length){{l.innerHTML='<p style="color:#a1a1a6;font-style:italic">'+(q?'No matches.':'No saved items yet.')+'</p>';return}}
var h='<div style="margin-bottom:10px;display:flex;gap:6px;flex-wrap:wrap;">';
h+='<button onclick="exportBm()" style="padding:4px 8px;border-radius:8px;border:1px solid #424245;background:none;color:#0a84ff;cursor:pointer;font-size:11px;">Export</button>';
h+='<label style="padding:4px 8px;border-radius:8px;border:1px solid #424245;color:#0a84ff;cursor:pointer;font-size:11px;">Import<input type="file" accept=".json" onchange="importBm(event)" style="display:none;"></label>';
h+='<button onclick="if(confirm(\'Clear all?\')){{sBm([]);rList();syncBtns()}}" style="padding:4px 8px;border-radius:8px;border:1px solid #ff453a;background:none;color:#ff453a;cursor:pointer;font-size:11px;">Clear</button>';
h+='</div>';
if(_svM==='date'){{var g={{}};b.forEach(function(m,i){{var d=m.date||'Unknown';if(!g[d])g[d]=[];g[d].push({{m:m,i:i}})}});Object.keys(g).sort().reverse().forEach(function(d){{h+='<div class="sv-gh">'+d+' ('+g[d].length+')</div>';g[d].forEach(function(o){{h+=siHtml(o.m,o.i)}})}})}}
else if(_svM==='platform'){{var g={{}};b.forEach(function(m,i){{var s=m.section||'Other';if(!g[s])g[s]=[];g[s].push({{m:m,i:i}})}});Object.keys(g).sort().forEach(function(s){{h+='<div class="sv-gh">'+s+' ('+g[s].length+')</div>';g[s].forEach(function(o){{h+=siHtml(o.m,o.i)}})}})}}
else{{b.forEach(function(m,i){{h+=siHtml(m,i)}})}}
l.innerHTML=h}}
function exportBm(){{var b=gBm(),bl=new Blob([JSON.stringify(b,null,2)],{{type:'application/json'}}),a=document.createElement('a');a.href=URL.createObjectURL(bl);a.download='dossier_saved.json';a.click()}}
function importBm(evt){{var f=evt.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(e){{try{{var imp=JSON.parse(e.target.result);if(!Array.isArray(imp))return;var b=gBm(),ex=new Set(b.map(x=>x.title)),n=0;imp.forEach(function(x){{if(!ex.has(x.title)){{b.push(x);n++}}}});sBm(b);rList();syncBtns();alert('Imported '+n+' new items')}}catch{{}}}};r.readAsText(f)}}
function rbm(i){{var b=gBm();b.splice(i,1);sBm(b);rList();syncBtns()}}
function tbm(btn){{var t=btn.getAttribute('data-title'),u=btn.getAttribute('data-url'),
s=btn.getAttribute('data-section'),b=gBm(),x=b.findIndex(m=>m.title===t);
if(x>=0){{b.splice(x,1);btn.classList.remove('saved');btn.innerHTML='&#9734;'}}
else{{b.push({{title:t,url:u,section:s,date:new Date().toLocaleDateString()}});btn.classList.add('saved');btn.innerHTML='&#9733;'}}
sBm(b)}}
function syncBtns(){{var b=gBm();document.querySelectorAll('.bm').forEach(btn=>{{
var t=btn.getAttribute('data-title'),s=b.some(m=>m.title===t);
btn.classList.toggle('saved',s);btn.innerHTML=s?'&#9733;':'&#9734;'}})}}
function filterPlatform(p,btn){{document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
btn.classList.add('active');document.querySelectorAll('.item').forEach(el=>{{
el.style.display=(p==='all'||el.getAttribute('data-platform')===p)?'flex':'none'}})}}
window.addEventListener('scroll',function(){{document.getElementById('scrollTop').classList.toggle('visible',window.scrollY>400)}});
document.addEventListener('DOMContentLoaded',function(){{uBadge();syncBtns()}});
</script>
</body></html>"""


def upgrade_old_format(html_content, date_str):
    """Upgrade old format items to new format with data-platform and bookmark buttons"""
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
    if not body_match:
        return ""
    body = body_match.group(1)

    # Extract total
    count_match = re.search(r'Total Items?:\s*(\d+)', body)
    total = count_match.group(1) if count_match else "0"

    lines = body.split('\n')
    new_items = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Keep h2 headers
        if stripped.startswith('<h2>'):
            new_items.append(stripped)
            continue

        # Keep "No items found" paragraphs
        if stripped.startswith('<p>') and ('No items' in stripped or 'No ' in stripped):
            new_items.append(stripped)
            continue

        # Check if it's already new format (has data-platform)
        if 'data-platform=' in stripped:
            new_items.append(stripped)
            continue

        # Old format item: <div class="item"><span class="platform reddit">...
        if '<div class="item">' in stripped:
            # Extract platform
            plat_match = re.search(r'class="platform\s+(\w+)"', stripped)
            platform = plat_match.group(1) if plat_match else 'unknown'

            # Extract title
            title_match = re.search(r'<strong>(.*?)</strong>', stripped)
            title = title_match.group(1) if title_match else 'Untitled'
            safe_title = title.replace('"', '&quot;').replace("'", "&#39;").replace('<', '&lt;').replace('>', '&gt;')

            # Extract URL
            url_match = re.search(r'href="([^"]+)"', stripped)
            url = url_match.group(1) if url_match else '#'

            # Extract section display name
            span_match = re.search(r'<span class="platform[^"]*">(.*?)</span>', stripped)
            section = span_match.group(1) if span_match else platform
            safe_section = section.replace('"', '&quot;').replace("'", "&#39;")

            # Get inner content (everything after <div class="item">)
            inner = stripped.replace('<div class="item">', '', 1)
            # Remove trailing </div>
            if inner.endswith('</div>'):
                inner = inner[:-6]

            new_line = f'<div class="item" data-platform="{platform}"><button class="bm" data-title="{safe_title}" data-url="{url}" data-section="{safe_section}" onclick="tbm(this)">&#9734;</button><div class="item-content">{inner}</div></div>'
            new_items.append(new_line)
            continue

    items_html = '\n'.join(new_items)
    return items_html, total


# Process all files
for date_str in archive_dates:
    filepath = DB_DIR / f'all_items_{date_str}.html'
    print(f"Upgrading {date_str}...", end=" ")

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        old_html = f.read()

    # Check if already upgraded (has page-layout)
    already_upgraded = 'page-layout' in old_html

    if already_upgraded:
        # Just needs scrollbar CSS and sidebar update
        # Extract items between main-content div
        items_match = re.search(r'<div class="filter-bar">.*?</div>\s*\n\s*<div class="saved-panel".*?</div>\s*\n(.*?)</div><!-- end main-content -->', old_html, re.DOTALL)
        if items_match:
            items_html = items_match.group(1)
        else:
            # Try to get content differently
            items_html = ""
            in_items = False
            for line in old_html.split('\n'):
                stripped = line.strip()
                if stripped.startswith('<h2>') and ('items)' in stripped or 'Reddit' in stripped or 'Bluesky' in stripped):
                    in_items = True
                if in_items:
                    if '<!-- end main-content -->' in stripped:
                        break
                    items_html += line + '\n'

        count_match = re.search(r'Total Items?:\s*(\d+)', old_html)
        total = count_match.group(1) if count_match else "0"
    else:
        # Old format - needs full upgrade
        result = upgrade_old_format(old_html, date_str)
        if isinstance(result, tuple):
            items_html, total = result
        else:
            items_html = result
            total = "0"

    sidebar = build_sidebar_links(date_str)
    new_html = build_new_html(date_str, items_html, total)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"OK ({'updated' if already_upgraded else 'full upgrade'})")

print(f"\nDone! Upgraded {len(archive_dates)} files.")
