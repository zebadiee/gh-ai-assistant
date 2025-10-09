#!/bin/bash
# Quick script to refresh API key and test

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Regenerate API Key & Test Script                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Step 1: Get New API Key"
echo "   1. Visit: https://openrouter.ai/keys"
echo "   2. Create a new key"
echo "   3. Copy it"
echo ""
echo "📍 Step 2: Update gh-ai-assistant"

cd /Users/dadhoosband/gh-ai-assistant
source venv/bin/activate
python gh_ai_core.py setup

echo ""
echo "📍 Step 3: Test with 3 quick questions"
echo ""

echo "Test 1:"
python gh_ai_core.py ask --no-context "What is 2+2? Just answer the number."
echo ""

echo "Test 2:"
python gh_ai_core.py ask --no-context "What is the capital of France? One word."
echo ""

echo "Test 3:"
python gh_ai_core.py ask --no-context "Is Python a programming language? Yes or no."
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "If all 3 tests worked without constant rate limits, you're good!"
echo "If still seeing 429s, wait 5 minutes and try again."
echo ""
