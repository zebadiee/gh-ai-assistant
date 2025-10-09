#!/bin/bash
# Quick test of interactive chat mode

cd /Users/dadhoosband/gh-ai-assistant
source venv/bin/activate

echo "Starting interactive chat mode..."
echo ""
echo "Try these commands:"
echo "  - Ask questions naturally"
echo "  - Type 'models' to see available models"
echo "  - Type 'stats' to see usage"
echo "  - Type 'exit' to quit"
echo ""

python gh_ai_core.py chat --no-context
