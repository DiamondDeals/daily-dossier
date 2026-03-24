#!/bin/bash
# Install required dependencies for Daily Digest

echo "📦 Installing dependencies for Daily Business Digest..."
echo ""

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

echo ""
echo "Installing required packages..."
echo ""

# Install minimal required packages
pip install praw python-dotenv

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Create Reddit account (see REDDIT_ACCOUNT_SETUP.md)"
echo "2. Configure .env file with credentials"
echo "3. Run: python3 daily_business_digest.py"
