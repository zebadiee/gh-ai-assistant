#!/bin/bash
# Quick CLI wrapper for model monitoring commands

# Activate venv if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

case "$1" in
    rankings|rank|r)
        python gh_ai_core.py rankings
        ;;
    recommend|rec|best)
        python gh_ai_core.py recommend
        ;;
    stats|s)
        python gh_ai_core.py stats ${2:---days 7}
        ;;
    models|m|list)
        python gh_ai_core.py models
        ;;
    demo|test)
        echo "Running model monitoring demo..."
        python demo_model_monitoring.py
        ;;
    clear|reset)
        echo "Clearing monitoring data..."
        python model_monitor.py --clear
        ;;
    help|h|--help|-h)
        cat << EOF
🎯 Model Monitoring CLI - Quick Commands

Usage: ./monitor.sh <command>

Commands:
  rankings, rank, r      Show real-time model performance rankings
  recommend, rec, best   Get best model recommendation
  stats, s [days]        Show usage statistics (default: 7 days)
  models, m, list        List all available models
  demo, test             Run monitoring system demo
  clear, reset           Clear all monitoring data
  help, h                Show this help message

Examples:
  ./monitor.sh rankings          # Show model rankings
  ./monitor.sh recommend         # Get best model
  ./monitor.sh stats 30          # Show 30-day stats
  ./monitor.sh demo              # Run demo

Full Documentation:
  See MODEL_MONITORING.md for complete guide
EOF
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run './monitor.sh help' for usage"
        exit 1
        ;;
esac
