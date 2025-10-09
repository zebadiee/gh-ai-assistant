#!/bin/bash
# Installation script for GitHub CLI AI Assistant

set -e  # Exit on error

echo "🚀 GitHub CLI AI Assistant - Installation Script"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not found"
    echo "   Please install Python 3.8 or higher"
    exit 1
}

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run validation
echo ""
echo "🔍 Running validation tests..."
python validate.py

# Make scripts executable
echo ""
echo "🔐 Setting script permissions..."
chmod +x gh-ai
chmod +x gh_ai_core.py
chmod +x validate.py

echo ""
echo "=" * 60
echo ""
echo "✅ Installation complete!"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure your OpenRouter API key:"
echo "   python gh_ai_core.py setup"
echo ""
echo "3. Start using the assistant:"
echo "   python gh_ai_core.py ask 'Hello!'"
echo ""
echo "📖 Documentation:"
echo "   - README.md         - Full documentation"
echo "   - QUICKSTART.md     - 5-minute quick start"
echo "   - API_SETUP.md      - API configuration guide"
echo "   - ARCHITECTURE.md   - System architecture"
echo "   - examples/         - Usage examples"
echo ""
echo "🆘 Need help? Run: python gh_ai_core.py --help"
echo ""
