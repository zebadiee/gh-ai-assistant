#!/bin/bash
# Quick demo of GitHub CLI AI Assistant features

echo "🎬 GitHub CLI AI Assistant - Feature Demo"
echo "=========================================="
echo ""

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating virtual environment..."
    source venv/bin/activate
fi

echo "1️⃣  Testing Help Command"
echo "------------------------"
python gh_ai_core.py --help
echo ""

echo "2️⃣  Listing Available Models"
echo "----------------------------"
python gh_ai_core.py models
echo ""

echo "3️⃣  Checking Usage Statistics"
echo "-----------------------------"
python gh_ai_core.py stats --days 7
echo ""

echo "4️⃣  Testing Validation"
echo "----------------------"
python validate.py | head -20
echo ""

echo "✅ Demo complete!"
echo ""
echo "To use the assistant:"
echo "1. Run: python gh_ai_core.py setup"
echo "2. Get free API key: https://openrouter.ai/keys"
echo "3. Start asking: python gh_ai_core.py ask 'Your question'"
echo ""
