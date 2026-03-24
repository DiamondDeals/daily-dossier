#!/usr/bin/env python3
"""
Send daily digest to Slack #ideas channel
Integrates with OpenClaw's message tool
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def send_via_openclaw_message(text: str, channel: str = "ideas") -> bool:
    """Send message via OpenClaw's message command"""
    try:
        # Use openclaw CLI to send message
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'slack',
            '--target', f'#{channel}',
            '--message', text
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Message sent to #{channel}")
            return True
        else:
            print(f"❌ Failed to send: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def split_message_if_needed(message: str, max_length: int = 4000) -> list:
    """Split message if it exceeds Slack's character limit"""
    if len(message) <= max_length:
        return [message]
        
    # Split at category boundaries
    parts = []
    current = ""
    
    for line in message.split('\n'):
        if len(current) + len(line) + 1 > max_length and current:
            parts.append(current)
            current = line + '\n'
        else:
            current += line + '\n'
            
    if current:
        parts.append(current)
        
    return parts


def main():
    """Main entry point"""
    
    # Get digest file from today
    workspace = Path(__file__).parent
    today = datetime.now().strftime('%Y%m%d')
    digest_file = workspace / f"digest_{today}.txt"
    
    if not digest_file.exists():
        print(f"❌ Digest file not found: {digest_file}")
        print("Run daily_business_digest.py first to generate the digest.")
        sys.exit(1)
        
    # Read digest
    with open(digest_file, 'r', encoding='utf-8') as f:
        message = f.read()
        
    print(f"📤 Sending digest to Slack #ideas...")
    print(f"📊 Message length: {len(message)} characters")
    
    # Split if needed
    parts = split_message_if_needed(message)
    
    if len(parts) > 1:
        print(f"⚠️  Message split into {len(parts)} parts")
        
    # Send each part
    for i, part in enumerate(parts, 1):
        if len(parts) > 1:
            print(f"  Sending part {i}/{len(parts)}...")
        
        success = send_via_openclaw_message(part, channel='ideas')
        
        if not success:
            print(f"❌ Failed to send part {i}")
            sys.exit(1)
            
    print("✅ All parts sent successfully!")
    

if __name__ == '__main__':
    main()
