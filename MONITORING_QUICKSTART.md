# 🎯 Model Monitoring - Quick Reference

## TL;DR
The system automatically selects the **most reliable, least congested model** for every request. You don't need to do anything - it just works!

## Quick Commands

```bash
# See which models are performing best right now
python gh_ai_core.py rankings

# Get recommendation for best model
python gh_ai_core.py recommend

# Ask a question (auto-selects best model)
python gh_ai_core.py ask "your question"

# Run the demo
python demo_model_monitoring.py

# Or use the quick CLI
./monitor.sh rankings
./monitor.sh recommend
./monitor.sh demo
```

## How Models Are Scored

**Score Range: 0-100 (lower is better)**

🟢 **0-25: Excellent** - Use this model!  
🟡 **25-50: Good** - Reliable choice  
🟠 **50-75: Fair** - Usable but not optimal  
🔴 **75-100: Poor** - Avoid if possible  

**Score Calculation:**
- 40% Error Rate (how often it fails)
- 30% Consecutive Failures (recent reliability)
- 20% Latency (how fast it responds)
- 10% Daily Usage (how close to limit)

## What It Does Automatically

1. **Tracks Performance**: Every request is monitored for success/failure and speed
2. **Ranks Models**: Continuously updates rankings based on real data
3. **Selects Best**: Always chooses the most reliable, fastest available model
4. **Falls Back**: If a model fails, automatically tries the next-best
5. **Learns**: Avoids models that have failed 3+ times in a row

## Example: Automatic Fallback

```
You: "Explain async Python"
  ↓
System: Try Gemini (score: 12) → Success! ✅
  ↓
Response delivered in 245ms

You: "Explain generators"
  ↓
System: Try Gemini (score: 12) → Rate Limit! ⚠️
  ↓
System: Try Mistral (score: 28) → Success! ✅
  ↓
Response delivered in 312ms
```

## When to Check Rankings

**Before heavy usage:**
```bash
./monitor.sh recommend  # See which model to prioritize
```

**After errors:**
```bash
./monitor.sh rankings   # See what's working now
```

**Daily check:**
```bash
./monitor.sh stats      # Review your usage patterns
```

## In Interactive Chat

```bash
python gh_ai_core.py chat

# In chat, type:
rankings    # Show current rankings
recommend   # Get best model
models      # List all models
stats       # Show usage stats
```

## Troubleshooting

**"All models showing score 100"**
- No usage data yet. Make a few requests first.

**"Model monitoring not available"**
```bash
cd gh-ai-assistant
pip install -e .
```

**Reset everything:**
```bash
./monitor.sh clear
```

## Advanced: Direct API

```python
from model_monitor import ModelMonitor, SmartModelSelector
from gh_ai_core import TokenManager, FREE_MODELS

monitor = ModelMonitor()
token_manager = TokenManager()
selector = SmartModelSelector(monitor, FREE_MODELS, token_manager)

# Get best model ID
best_model = selector.select_model()

# Get fallback sequence
fallback = selector.get_fallback_sequence()

# Record a request
monitor.record_request(
    model_id="google/gemini-2.0-flash-exp:free",
    success=True,
    latency_ms=245,
    tokens_used=150
)
```

## See Also

- **Full Guide**: [MODEL_MONITORING.md](MODEL_MONITORING.md)
- **Setup**: [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md)  
- **Main Docs**: [README.md](README.md)

---

**Remember**: The system is automatic. Just use `ask` and it handles everything! 🚀
