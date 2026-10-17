#!/bin/bash

# Basketball Betting Bot Installation Script

echo "🏀 Basketball Betting Bot Installation"
echo "======================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Error: Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "📥 Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your API keys:"
    echo "   1. TELEGRAM_BOT_TOKEN - Get from @BotFather"
    echo "   2. API_BASKETBALL_KEY - Get from https://www.api-basketball.com/"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Create data directory
echo ""
echo "📁 Creating data directories..."
mkdir -p data logs

echo "✅ Installation complete!"
echo ""
echo "🚀 To start the bot:"
echo "   1. Edit .env file with your API keys"
echo "   2. Run: ./run.sh"
echo ""
echo "📖 For more information, see README.md"
