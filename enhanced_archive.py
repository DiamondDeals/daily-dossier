#!/usr/bin/env python3
"""
Enhanced archiving with verification
"""
import subprocess
import os
from datetime import datetime

def archive_current_dossier():
    """Archive dossier with verification"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_path = f'Archive/dossier_{timestamp}.html'
    
    # Copy current dossier
    if os.path.exists('dossier.html'):
        subprocess.run(['cp', 'dossier.html', archive_path], check=True)
        print(f"✅ Archived: {archive_path}")
        
        # Verify
        if os.path.exists(archive_path):
            size = os.path.getsize(archive_path)
            print(f"   Size: {size} bytes")
            return archive_path
    
    return None

def verify_archives():
    """Count and verify all archives"""
    archives = subprocess.run(
        ['find', 'Archive/', '-name', 'dossier_*.html'],
        capture_output=True, text=True
    )
    count = len(archives.stdout.strip().split('\n'))
    print(f"✅ Total archives: {count}")
    return count

if __name__ == '__main__':
    print("✅ Enhanced archive system created")
