# 🔐 Session Persistence & Model Rotation System

## No More "One-Night Stand" Statelessness!

Your AI assistant now **remembers you** across sessions and intelligently manages model selection for optimal token efficiency.

## The Problem This Solves

**Before**: Every conversation was a fresh start
- "Who are you again?"
- "What's my name?"
- Manual model selection
- No usage tracking
- Inefficient token spending

**After**: Persistent, personalized AI partnership
- "Welcome back, Declan!"
- "I'm Brakel, your AI assistant"
- Automatic optimal model selection
- Complete usage analytics
- Token-efficient rotation

## Key Features

### ✅ Persistent Session Identity

```bash
# First time
python session_manager.py --init
# Creates: ~/.gh-ai-assistant/user_session.json

# Every subsequent use
python session_manager.py --greeting
# Output: "Welcome back, Declan! I'm Brakel, powered by Google Gemini 2.0 Flash"
```

### ✅ Intelligent Model Rotation

**Algorithm selects best model based on**:
1. **Current usage** (prefer least-used today)
2. **Daily limits** (avoid exhausted models)  
3. **Success rate** (prefer reliable models)
4. **User preferences** (favorite models get bonus)
5. **Context needs** (large context when needed)

**Scoring system**:
```python
Base score: 100 points

Usage penalty: -40 points (high usage = lower score)
Success rate bonus: +20 points (reliable = higher score)
Latency bonus: +10 points (fast = higher score)
Near-limit penalty: -50 points (avoid exhausted models)
Context bonus: +10 points (when large context needed)
Favorite bonus: +15 points (user preferences)

Highest score wins!
```

### ✅ Automatic Usage Tracking

Tracks per model:
- Tokens used today
- Requests today
- Total tokens (all time)
- Total requests (all time)
- Average latency
- Success rate

### ✅ Smart Rotation Recommendations

```python
# System automatically suggests when to rotate
if current_model_usage >= 90%:
    "Current model at 90% of daily limit"
    "Switching to: DeepSeek R1"
```

## Usage

### First Time Setup

```bash
cd gh-ai-assistant
python session_manager.py --init
```

Interactive prompts:
```
👤 What's your name? Declan
🤖 What would you like to call me? Brakel
🎯 Choose your preferred model (1-5): 1

✅ Session created!
👋 Hello Declan, I'm Brakel—your personal AI assistant!
```

### Daily Usage

```bash
# Show personalized greeting
python session_manager.py --greeting
# Output: "Welcome back, Declan! I'm Brakel..."

# View usage statistics
python session_manager.py --stats

# Get model recommendation
python session_manager.py --suggest-model
# Output: "🎯 Recommended model: DeepSeek R1"
```

### View Statistics

```bash
python session_manager.py --stats
```

Output:
```
╔═══════════════════════════════════════════════════╗
║       SESSION & MODEL USAGE STATISTICS            ║
╚═══════════════════════════════════════════════════╝

👤 SESSION INFO:
   User: Declan
   Assistant: Brakel
   Created: 2025-01-15
   Conversations: 42

📊 OVERALL USAGE:
   Total Requests: 156
   Total Tokens: 45,230

🤖 MODEL USAGE (Sorted by Usage):

Model                     Today        Limit    Usage %   Success
─────────────────────────────────────────────────────────────────
Google Gemini 2.0 Flash   45/12500     1000     4.5%     98.2%
DeepSeek R1               32/8900      1000     3.2%     95.1%
Meta Llama 3.2 3B         28/7800      1000     2.8%     99.0%
Mistral 7B Instruct       18/4200      1000     1.8%     97.5%
Nemotron 70B              10/2300      1000     1.0%     100.0%
```

## Top Free Models Registry

```python
TOP_FREE_MODELS = [
    {
        "name": "google/gemini-2.0-flash-exp:free",
        "display_name": "Google Gemini 2.0 Flash",
        "context_window": 1,000,000 tokens,
        "best_for": "general conversation, fast responses, large context"
    },
    {
        "name": "deepseek/deepseek-r1:free",
        "display_name": "DeepSeek R1",
        "context_window": 131,072 tokens,
        "best_for": "reasoning, math, code analysis"
    },
    {
        "name": "meta-llama/llama-3.2-3b-instruct:free",
        "display_name": "Meta Llama 3.2 3B",
        "context_window": 131,072 tokens,
        "best_for": "general tasks, efficiency"
    },
    {
        "name": "mistralai/mistral-7b-instruct:free",
        "display_name": "Mistral 7B Instruct",
        "context_window": 32,768 tokens,
        "best_for": "multilingual, instruction following"
    },
    {
        "name": "nvidia/llama-3.1-nemotron-70b-instruct:free",
        "display_name": "Nemotron 70B",
        "context_window": 131,072 tokens,
        "best_for": "complex reasoning, large context"
    }
]
```

All models have **1000 requests/day limit** (free tier).

## Integration with gh_ai_core.py

```python
from session_manager import SessionManager

# Initialize session
session_mgr = SessionManager()

# If no session, create one
if not session_mgr.session:
    session_mgr.create_session_interactive()

# Get greeting
print(session_mgr.get_greeting())

# Select optimal model
model = session_mgr.select_optimal_model()

# Use the model
response = api.ask(model, prompt)

# Record usage
session_mgr.record_usage(
    model_id=model,
    tokens_used=response_tokens,
    latency_ms=response_time,
    success=True
)

# Check if should rotate
should_rotate, suggested, reason = session_mgr.should_rotate_model(model)
if should_rotate:
    print(f"Rotating: {reason}")
    model = suggested
```

## Rotation Algorithm Details

### Selection Process

```
For each model:
  1. Start with base score: 100
  
  2. Apply usage penalty:
     - requests_today / daily_limit → 0-1
     - Multiply by 40 → 0-40 point penalty
     
  3. Add success rate bonus:
     - success_rate (0-1) × 20 → 0-20 point bonus
     
  4. Add latency bonus:
     - max(0, 10 - latency_seconds) → 0-10 points
     
  5. Check daily limit:
     - If >= 90% used: -50 points penalty
     
  6. Context window bonus (if needed):
     - (context_window / 1M) × 10 → 0-10 points
     
  7. Favorite model bonus:
     - If in favorites: +15 points
     
  Final Score = 100 - usage_penalty + success_bonus + latency_bonus 
                - limit_penalty + context_bonus + favorite_bonus
                
  Select: Highest scoring model
```

### Example Calculation

```
Model: Google Gemini 2.0 Flash

Base: 100
Usage: 45/1000 requests (4.5%) → -1.8 penalty
Success: 98.2% → +19.6 bonus
Latency: 850ms → +9.2 bonus
Limit: 4.5% < 90% → no penalty
Context: 1M tokens, needed → +10 bonus
Favorite: Yes → +15 bonus

Final Score: 100 - 1.8 + 19.6 + 9.2 + 10 + 15 = 152 points ⭐
```

## Session Persistence

### Files Created

```
~/.gh-ai-assistant/
├── user_session.json      # Your identity and preferences
└── model_usage.json       # Usage tracking per model
```

### Session File Format

```json
{
  "user_name": "Declan",
  "assistant_name": "Brakel",
  "preferred_model": "google/gemini-2.0-flash-exp:free",
  "created_at": "2025-01-15T10:30:00",
  "last_active": "2025-01-15T14:22:15",
  "total_conversations": 42,
  "favorite_models": [
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free"
  ]
}
```

### Usage File Format

```json
{
  "google/gemini-2.0-flash-exp:free": {
    "model_name": "google/gemini-2.0-flash-exp:free",
    "tokens_used_today": 12500,
    "requests_today": 45,
    "total_tokens": 345230,
    "total_requests": 1245,
    "last_used": "2025-01-15T14:22:15",
    "avg_latency_ms": 850,
    "success_rate": 0.982
  }
}
```

## Commands Reference

```bash
# Initialize new session (first time)
python session_manager.py --init

# Show personalized greeting
python session_manager.py --greeting

# Display usage statistics
python session_manager.py --stats

# Get model recommendation
python session_manager.py --suggest-model

# Reset session (logout)
python session_manager.py --reset

# Show greeting + stats (default)
python session_manager.py
```

## Programmatic Usage

### Select Optimal Model

```python
from session_manager import SessionManager

mgr = SessionManager()

# Basic selection
model = mgr.select_optimal_model()

# Exclude specific models
model = mgr.select_optimal_model(
    exclude_models=["model1", "model2"]
)

# Prefer large context
model = mgr.select_optimal_model(
    prefer_large_context=True
)
```

### Record Usage

```python
mgr.record_usage(
    model_id="google/gemini-2.0-flash-exp:free",
    tokens_used=1234,
    latency_ms=850,
    success=True
)
```

### Check Rotation Need

```python
should_rotate, suggested, reason = mgr.should_rotate_model(
    current_model="google/gemini-2.0-flash-exp:free"
)

if should_rotate:
    print(f"Rotating because: {reason}")
    print(f"Suggested model: {suggested}")
```

## Benefits

### Personalization

✅ **Persistent identity** - Never "who are you again?"  
✅ **Remembers preferences** - Favorite models prioritized  
✅ **Tracks history** - Conversation count, usage patterns  
✅ **Personalized greetings** - "Welcome back, Declan!"  

### Efficiency

✅ **Token optimization** - Uses least-used models first  
✅ **Avoids exhaustion** - Rotates before hitting limits  
✅ **Performance aware** - Prefers faster, more reliable models  
✅ **Context awareness** - Picks models with needed capacity  

### Intelligence

✅ **Multi-factor scoring** - Holistic model selection  
✅ **Adaptive learning** - Adjusts based on usage patterns  
✅ **Predictive rotation** - Suggests switches proactively  
✅ **Analytics** - Complete visibility into usage  

## Best Practices

### 1. Let It Auto-Select

```python
# Good: Let algorithm choose
model = session_mgr.select_optimal_model()

# Also good: Provide hints
model = session_mgr.select_optimal_model(prefer_large_context=True)

# Avoid: Manually picking without data
model = "some-model"  # Misses optimization opportunities
```

### 2. Always Record Usage

```python
# After every API call
session_mgr.record_usage(
    model_id=model,
    tokens_used=tokens,
    latency_ms=time_taken,
    success=response_success
)
```

### 3. Check Rotation Proactively

```python
# Before starting new conversation
should_rotate, suggested, reason = session_mgr.should_rotate_model(current_model)

if should_rotate:
    current_model = suggested
```

### 4. Monitor Statistics

```bash
# Daily check
python session_manager.py --stats

# Look for:
# - Models near limits
# - Low success rates
# - High latencies
```

## Troubleshooting

### Session Not Persisting

```bash
# Check if file exists
ls -la ~/.gh-ai-assistant/user_session.json

# If missing, reinitialize
python session_manager.py --init
```

### Incorrect Model Selection

```bash
# View usage data
python session_manager.py --stats

# Check which models are available
# Verify daily limits haven't been hit
```

### Reset Everything

```bash
# Clear session
python session_manager.py --reset

# Clear usage data
rm ~/.gh-ai-assistant/model_usage.json

# Start fresh
python session_manager.py --init
```

## Conclusion

The Session Persistence system transforms your AI assistant from a stateless tool into a **persistent AI partner** that:

✅ Remembers you across sessions  
✅ Optimizes model selection automatically  
✅ Tracks usage for efficiency  
✅ Rotates intelligently to maximize free tier  
✅ Provides complete analytics  

**No more "one-night stand" statelessness—your assistant knows you!**

---

**Status**: ✅ Production-ready  
**Testing**: All features validated  
**Integration**: Works with existing systems
