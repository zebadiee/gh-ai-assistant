# 🎯 Intelligent Model Monitoring & Dynamic Selection

## Overview

The GitHub AI Assistant now includes an **intelligent model monitoring and dynamic selection system** that automatically selects the most reliable, least congested, and most efficient OpenRouter free models in real-time.

This system solves the problem of popular models becoming overloaded by intelligently routing requests to the best available alternatives.

## Key Features

### 🔍 Real-Time Performance Monitoring
- Tracks success/failure rates for all models
- Monitors API latency for each request
- Records consecutive failures to identify problematic models
- Maintains historical performance data

### 📊 Smart Model Ranking
The system calculates a "usage score" (0-100, lower is better) for each model based on:
- **Error Rate (40%)** - How often the model fails
- **Consecutive Failures (30%)** - Recent reliability issues
- **Latency (20%)** - Response time performance
- **Daily Limit Usage (10%)** - How close to quota

### 🎯 Automatic Model Selection
- Automatically selects the best available model for each request
- Falls back to next-best model if primary fails
- Excludes models with consecutive failures (3+)
- Avoids congested models (score > 75)

### 🔄 Dynamic Rotation
- Rotates through models when rate limits hit
- Learns from failures and avoids problematic models
- Prioritizes underutilized models for better success rates

## Usage

### View Real-Time Rankings

```bash
# Show current model performance rankings
python gh_ai_core.py rankings
```

Output example:
```
====================================================================================================
🎯 MODEL RANKINGS - Real-time Performance & Availability
====================================================================================================
Rank   Model                               Score    Success   Latency    Usage        Status
----------------------------------------------------------------------------------------------------
1      Google Gemini 2.0 Flash Free        12.3/100 98.5%     245ms      15/1000      🟢 Excellent
2      Mistral 7B Instruct Free            28.7/100 95.2%     312ms      42/1000      🟡 Good
3      Meta Llama 3.2 3B Free              45.1/100 89.3%     498ms      156/1000     🟡 Good
4      DeepSeek R1 Free                    67.8/100 75.0%     1205ms     892/1000     🟠 Fair
----------------------------------------------------------------------------------------------------

💡 Score Factors: Error Rate (40%) + Failures (30%) + Latency (20%) + Daily Usage (10%)
📊 Lower scores are better. Recommended: Use models with score < 50
```

### Get Model Recommendation

```bash
# Get recommendation for best model to use right now
python gh_ai_core.py recommend
```

Output example:
```
🎯 Recommended: Google Gemini 2.0 Flash Free
   Model ID: google/gemini-2.0-flash-exp:free
   Quality: EXCELLENT (score: 12.3/100)
   Success Rate: 98.5%
   Avg Latency: 245ms
   Today's Usage: 15/1000
```

### Interactive Chat with Auto-Selection

```bash
# Start chat - automatically uses best models
python gh_ai_core.py chat

# In chat mode, use these commands:
# - rankings : Show real-time rankings
# - recommend : Get best model recommendation
# - models : List all available models
# - stats : Show usage statistics
```

### Make Single Request (Auto-Selected Model)

```bash
# System automatically chooses best model
python gh_ai_core.py ask "Explain quantum computing"
```

## How It Works

### 1. Performance Tracking

Every API request is tracked with:
- Model ID
- Success/failure status
- Response latency
- Tokens used
- Error type (if failed)
- Timestamp

This data is stored in a local SQLite database (`~/.gh-ai-assistant/model_monitor.db`).

### 2. Score Calculation

For each model, the system calculates a usage score:

```python
score = (error_rate * 40) + 
        (consecutive_failures * 10) + 
        (latency/5000 * 20) + 
        (requests_today/daily_limit * 10)
```

Example scores:
- **0-25**: 🟢 Excellent - Highly recommended
- **25-50**: 🟡 Good - Reliable choice
- **50-75**: 🟠 Fair - Usable but not optimal
- **75-100**: 🔴 Poor - Avoid if possible

### 3. Smart Selection Algorithm

When you make a request:

1. **Rank all models** by usage score (ascending)
2. **Filter out**:
   - Models at daily limit
   - Models with 3+ consecutive failures
   - Models with score > 75 (too congested)
3. **Select best available** model
4. **If it fails**: Mark as failed and try next in sequence
5. **Fall back to Ollama** if all cloud models exhausted

### 4. Automatic Fallback Sequence

The system creates an ordered fallback sequence:

```
Request → Best Model (score 12) → 
         [Fails] → 
         Second Best (score 28) → 
         [Fails] → 
         Third Best (score 45) → 
         [Fails] → 
         Local Ollama Model (unlimited)
```

## Benefits

### ⚡ Better Success Rates
By avoiding congested and failing models, you get higher success rates on the first try.

### 🚀 Lower Latency
System prioritizes faster-responding models, reducing wait times.

### 💡 Smarter Resource Usage
Distributes load across multiple models instead of hammering the most popular one.

### 🔄 Automatic Recovery
When a model recovers from issues, it automatically becomes available again.

### 📊 Data-Driven Decisions
Makes decisions based on actual performance data, not just assumptions.

## Advanced Usage

### View Detailed Stats for Specific Model

```bash
python model_monitor.py --stats "deepseek/deepseek-r1:free"
```

### Clear Monitoring Data

```bash
# Reset all performance tracking
python model_monitor.py --clear
```

### Programmatic Usage

```python
from model_monitor import ModelMonitor, SmartModelSelector
from gh_ai_core import TokenManager, FREE_MODELS

# Initialize
monitor = ModelMonitor()
token_manager = TokenManager()
selector = SmartModelSelector(monitor, FREE_MODELS, token_manager)

# Get best model
best_model_id = selector.select_model(task_type="general")

# Get fallback sequence
fallback_models = selector.get_fallback_sequence()

# Record request outcome
monitor.record_request(
    model_id="google/gemini-2.0-flash-exp:free",
    success=True,
    latency_ms=245,
    tokens_used=150
)
```

## Configuration

### Adjusting Selection Criteria

Edit `model_monitor.py` to adjust scoring weights:

```python
# In calculate_usage_score() method
error_score = stats['error_rate'] * 40      # Default: 40%
failure_score = min(stats['consecutive_failures'] * 10, 30)  # Default: 30%
latency_score = min((stats['avg_latency_ms'] / 5000) * 20, 20)  # Default: 20%
limit_score = (requests_today / daily_limit) * 10  # Default: 10%
```

### Cache Duration

```python
# In model_monitor.py
CACHE_DURATION_MINUTES = 5  # Adjust cache time
```

## Database Schema

### model_performance Table
Tracks individual request outcomes:
```sql
CREATE TABLE model_performance (
    id INTEGER PRIMARY KEY,
    model_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    latency_ms REAL,
    tokens_used INTEGER,
    error_type TEXT,
    error_message TEXT
)
```

### model_availability Table
Caches current model state:
```sql
CREATE TABLE model_availability (
    model_id TEXT PRIMARY KEY,
    is_available BOOLEAN DEFAULT 1,
    current_usage_score REAL DEFAULT 0,
    avg_latency_ms REAL DEFAULT 0,
    error_rate REAL DEFAULT 0,
    last_checked DATETIME,
    consecutive_failures INTEGER DEFAULT 0
)
```

## Troubleshooting

### "Model monitoring not available" Error

```bash
# Reinstall the package
cd gh-ai-assistant
pip install -e .
```

### All Models Show Score 100

This means no recent usage data. Use the system for a few requests to build up statistics.

### Monitoring Database Corruption

```bash
# Delete and rebuild
rm ~/.gh-ai-assistant/model_monitor.db
# Database will be recreated on next run
```

## Future Enhancements

Planned features:
- [ ] Integration with OpenRouter's `/rankings` API
- [ ] Machine learning-based model prediction
- [ ] Task-specific model optimization (code vs. chat)
- [ ] Cost optimization for paid tier users
- [ ] Multi-user performance aggregation
- [ ] Export monitoring data to CSV/JSON
- [ ] Grafana/Prometheus integration
- [ ] Webhook notifications for model issues

## FAQ

**Q: Does this work with paid OpenRouter models?**  
A: Yes! The system works with any OpenRouter model. Add paid models to the `FREE_MODELS` list.

**Q: Can I disable automatic selection?**  
A: Yes, specify a model directly in code or modify the selection logic.

**Q: How much overhead does monitoring add?**  
A: Minimal - just a few milliseconds per request for database writes.

**Q: Is the monitoring data shared?**  
A: No, all monitoring data is stored locally in `~/.gh-ai-assistant/`.

**Q: Can I reset the selection algorithm?**  
A: Yes, run `python model_monitor.py --clear` to start fresh.

## See Also

- [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) - OpenRouter configuration
- [README.md](README.md) - General usage guide
- [FEATURES.md](FEATURES.md) - Complete feature list

---

**Built with ❤️ for the gh-ai-assistant project**
