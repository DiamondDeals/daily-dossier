#!/usr/bin/env python3
"""
/mydossier - Daily Business Dossier Command
Run with: python mydossier.py update
"""

import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Handle encoding for Task Scheduler (no console attached)
OUTPUT_DIR = Path(__file__).parent / "OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)

# When run from Task Scheduler, stdout might not support emojis
# Redirect to log file to be safe
if not sys.stdout.isatty():  # No console (Task Scheduler)
    log_file = OUTPUT_DIR / f"scheduled_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    sys.stdout = open(log_file, 'w', encoding='utf-8')
    sys.stderr = sys.stdout

def safe_print(text):
    """Print text, handling encoding issues gracefully"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis and try again
        ascii_text = text.encode('ascii', 'ignore').decode('ascii')
        print(ascii_text)

def print_usage():
    """Show usage information"""
    safe_print("""
====================================================================
            DAILY BUSINESS DOSSIER COMMAND
====================================================================

Usage:
  python mydossier.py update    Run full digest update
  python mydossier.py status    Show last update time
  python mydossier.py help      Show this help

Examples:
  python mydossier.py update    # Scan all platforms & deploy

Output:
  https://DiamondDeals.github.io/daily-dossier/dossier.html
    """)

def get_last_update():
    """Get timestamp of last dossier.html update"""
    dossier_path = Path("C:/Users/Carzl/Documents/Projects/GITHUB/daily-dossier/dossier.html")
    if dossier_path.exists():
        mtime = dossier_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %I:%M %p PST')
    return "Never"

def run_update():
    """Run the complete digest workflow"""
    safe_print("=" * 70)
    safe_print("DAILY BUSINESS DOSSIER - UPDATE STARTED")
    safe_print("=" * 70)
    safe_print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}")
    safe_print(f"Working Dir: {os.getcwd()}")
    safe_print("")

    # Change to daily-dossier directory
    dossier_dir = Path("C:/Users/Carzl/Documents/Projects/GITHUB/daily-dossier")
    if not dossier_dir.exists():
        safe_print("ERROR: daily-dossier directory not found!")
        safe_print(f"Expected: {dossier_dir}")
        return 1

    os.chdir(str(dossier_dir))
    safe_print(f"Changed to: {os.getcwd()}")
    safe_print("")

    # Check if run_full_digest.py exists
    if not Path('run_full_digest.py').exists():
        safe_print("ERROR: run_full_digest.py not found!")
        return 1

    # Run the main digest script
    safe_print("Running digest workflow...")
    safe_print("")

    try:
        # Use python (not python3) on Windows
        result = subprocess.run(
            ['python', 'run_full_digest.py'],
            timeout=600,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Print output
        if result.stdout:
            safe_print(result.stdout)
        if result.stderr:
            safe_print("STDERR:")
            safe_print(result.stderr)

        if result.returncode == 0:
            safe_print("")
            safe_print("=" * 70)
            safe_print("DIGEST UPDATE COMPLETE!")
            safe_print("=" * 70)
            safe_print("Live URL: https://DiamondDeals.github.io/daily-dossier/dossier.html")
            safe_print(f"Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}")
            safe_print("")

            # Also log to main log file
            log_file = OUTPUT_DIR / "mydossier.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: Dossier updated\n")

            return 0
        else:
            safe_print("")
            safe_print(f"ERROR: Digest failed with return code: {result.returncode}")

            # Log failure
            log_file = OUTPUT_DIR / "mydossier.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FAILED: Exit code {result.returncode}\n")

            return result.returncode

    except subprocess.TimeoutExpired:
        safe_print("")
        safe_print("ERROR: Digest timed out after 10 minutes")
        return 1
    except Exception as e:
        safe_print("")
        safe_print(f"ERROR: {e}")

        # Log error
        log_file = OUTPUT_DIR / "mydossier.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {e}\n")

        return 1

def show_status():
    """Show current status"""
    safe_print("=" * 70)
    safe_print("DAILY BUSINESS DOSSIER - STATUS")
    safe_print("=" * 70)
    safe_print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p PST')}")
    safe_print(f"Last Update: {get_last_update()}")
    safe_print("Live URL: https://DiamondDeals.github.io/daily-dossier/dossier.html")
    safe_print(f"Working Dir: {os.getcwd()}")

    # Check if files exist
    dossier_dir = Path("C:/Users/Carzl/Documents/Projects/GITHUB/daily-dossier")
    safe_print("")
    safe_print("Files:")
    files = ['dossier.html', 'run_full_digest.py', 'html_generator.py']
    for f in files:
        file_path = dossier_dir / f
        status = "EXISTS" if file_path.exists() else "MISSING"
        safe_print(f"  {status}: {f}")

    safe_print("")
    return 0

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        return 1

    command = sys.argv[1].lower()

    if command == 'update':
        return run_update()
    elif command == 'status':
        return show_status()
    elif command in ['help', '-h', '--help']:
        print_usage()
        return 0
    else:
        safe_print(f"Unknown command: {command}")
        print_usage()
        return 1

if __name__ == "__main__":
    sys.exit(main())
