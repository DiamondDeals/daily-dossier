#!/bin/bash
# Daily Business Digest Runner
# Run by cron at 5 AM PT daily

set -e

# Change to script directory
cd "$(dirname "$0")"

# Log file
LOG_FILE="logs/digest_$(date +%Y%m%d).log"
mkdir -p logs

echo "======================================" | tee -a "$LOG_FILE"
echo "Daily Digest Run: $(date)" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run digest generation
echo "Generating digest..." | tee -a "$LOG_FILE"
python3 daily_business_digest.py >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Digest generation failed!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "✅ Digest generation complete" | tee -a "$LOG_FILE"

# The actual sending will be done by Bishop via OpenClaw
# This script just generates the digest file
# Bishop will read it and send it via the message tool

echo "✅ Digest ready for delivery" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"
