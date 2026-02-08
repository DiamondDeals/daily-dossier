#!/usr/bin/env python3
"""
Add Daily folder creation to run_full_digest.py properly
"""

import shutil

# Read the file
with open('run_full_digest.py', 'r') as f:
    lines = f.readlines()

# Find the line with "if __name__ == '__main__':"
main_index = -1
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        main_index = i
        break

if main_index > 0:
    # Add import at the top if not already there
    if 'import shutil' not in ''.join(lines):
        for i, line in enumerate(lines):
            if 'import os' in line:
                lines.insert(i+1, 'import shutil\nimport subprocess\n')
                main_index += 2  # Adjust index
                break
    
    # Add Daily folder logic after run_full_digest() call
    daily_code = '''
    # Create Daily folder structure
    print("\\n📁 Creating Daily folder structure...")
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%I%p').lstrip('0')  # "6AM" or "5PM"
    daily_folder = f'Daily/{date_str}-{time_str}'
    
    os.makedirs(daily_folder, exist_ok=True)
    
    # Copy complete database files to Daily folder
    if os.path.exists(f'Database/all_items_{date_str}.html'):
        shutil.copy(f'Database/all_items_{date_str}.html', f'{daily_folder}/all_items.html')
        print(f"✅ Copied complete database: {daily_folder}/all_items.html")
    
    if os.path.exists(f'Database/complete_{date_str}.json'):
        shutil.copy(f'Database/complete_{date_str}.json', f'{daily_folder}/complete.json')
        print(f"✅ Copied raw data: {daily_folder}/complete.json")
    
    # Copy the digest
    if os.path.exists('dossier.html'):
        shutil.copy('dossier.html', f'{daily_folder}/digest.html')
        print(f"✅ Copied highlights: {daily_folder}/digest.html")
    
    # Add footer links to main dossier
    print("\\n🔗 Adding footer links...")
    subprocess.run(['python3', 'add_footer_links.py'], check=True)
    
    print(f"\\n✅ Daily folder complete: {daily_folder}/")
'''
    
    # Insert after "run_full_digest()" call
    for i in range(main_index, len(lines)):
        if 'run_full_digest()' in lines[i] and 'def' not in lines[i]:
            # Add after this line
            lines.insert(i+1, daily_code)
            break
    
    # Write back
    with open('run_full_digest.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Updated run_full_digest.py with Daily folder creation")
else:
    print("❌ Could not find main section in run_full_digest.py")
