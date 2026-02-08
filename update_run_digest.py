#!/usr/bin/env python3
"""
Update run_full_digest.py to create Daily folders automatically
"""

# Read current run_full_digest.py
with open('run_full_digest.py', 'r') as f:
    content = f.read()

# Check if Daily folder logic already exists
if 'Daily/' not in content:
    # Add Daily folder creation at the end, before git commands
    
    daily_folder_code = '''
# Create Daily folder structure with datetime
date_str = datetime.now().strftime('%Y-%m-%d')
time_str = datetime.now().strftime('%I%p').lstrip('0')  # "6AM" or "5PM"
daily_folder = f'Daily/{date_str}-{time_str}'

os.makedirs(daily_folder, exist_ok=True)
print(f"\\n📁 Creating daily folder: {daily_folder}/")

# Copy complete database files to Daily folder
if os.path.exists(f'Database/all_items_{date_str}.html'):
    shutil.copy(f'Database/all_items_{date_str}.html', f'{daily_folder}/all_items.html')
    print(f"✅ Saved: {daily_folder}/all_items.html")

if os.path.exists(f'Database/complete_{date_str}.json'):
    shutil.copy(f'Database/complete_{date_str}.json', f'{daily_folder}/complete.json')
    print(f"✅ Saved: {daily_folder}/complete.json")

# Copy the digest
if os.path.exists('dossier.html'):
    shutil.copy('dossier.html', f'{daily_folder}/digest.html')
    print(f"✅ Saved: {daily_folder}/digest.html")

# Add footer links to main dossier
subprocess.run(['python3', 'add_footer_links.py'], check=True)
'''

    # Find where to insert (before git commands)
    git_add_line = content.find('subprocess.run([\'git\', \'add\'')
    if git_add_line > 0:
        content = content[:git_add_line] + daily_folder_code + '\n' + content[git_add_line:]
        
        # Also need to add imports at the top
        if 'import shutil' not in content:
            import_line = content.find('import subprocess')
            content = content[:import_line] + 'import shutil\n' + content[import_line:]
    
    with open('run_full_digest.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated run_full_digest.py to create Daily folders")
else:
    print("ℹ️  Daily folder logic already exists in run_full_digest.py")
