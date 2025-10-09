#!/bin/bash
# Quick interactive demo of the monitoring system

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🎯 Intelligent Model Monitoring - Interactive Demo         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This system automatically selects the best model for every request!"
echo ""

source venv/bin/activate 2>/dev/null

echo "1️⃣  Current Model Rankings:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python gh_ai_core.py rankings

echo ""
echo "2️⃣  Best Model Right Now:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python gh_ai_core.py recommend

echo ""
echo "3️⃣  Your Usage Statistics:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python gh_ai_core.py stats

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Try these commands:"
echo ""
echo "   Ask a question:"
echo "   python gh_ai_core.py ask 'Explain quantum computing'"
echo ""
echo "   Start interactive chat:"
echo "   python gh_ai_core.py chat"
echo ""
echo "   Quick rankings:"
echo "   ./monitor.sh rank"
echo ""
echo "   Full demo:"
echo "   ./monitor.sh demo"
echo ""
echo "The system will automatically choose the best model each time!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
