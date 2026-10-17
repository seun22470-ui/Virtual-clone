#!/bin/bash

# Basketball Betting Bot Run Script

echo "🏀 Starting Basketball Betting Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    if [ -f ".env" ]; then
        echo "📄 Loading environment from .env file..."
        export $(grep -v '^#' .env | xargs)
    else
        echo "❌ Error: TELEGRAM_BOT_TOKEN not set and .env file not found!"
        echo "Please set up your .env file first:"
        echo "  cp .env.example .env"
        echo "  # Edit .env with your credentials"
        exit 1
    fi
fi

# Run the bot
echo "🚀 Bot is starting..."
python bot.py
