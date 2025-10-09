# 📖 Example Usage - Model Monitoring in Action

## Scenario: Daily Development Workflow

### Morning - Check System Health

```bash
# Start your day by checking which models are working best
./monitor.sh recommend
```

**Output:**
```
🎯 Recommended: Google Gemini 2.0 Flash Free
   Model ID: google/gemini-2.0-flash-exp:free
   Quality: EXCELLENT (score: 12.3/100)
   Success Rate: 98.5%
   Avg Latency: 245ms
   Today's Usage: 0/1000
```

**Insight**: Gemini is performing excellently with near-perfect success rate and low latency.

---

### Mid-Day - Heavy Usage

```bash
# Ask multiple questions throughout the day
python gh_ai_core.py ask "Review this pull request"
python gh_ai_core.py ask "Explain this error"
python gh_ai_core.py ask "Optimize this function"

# The system automatically selects the best model for each request
```

**Behind the scenes:**
```
Request 1: Gemini (score: 12) → Success ✅
Request 2: Gemini (score: 13) → Success ✅
Request 3: Gemini (score: 14) → Success ✅
...
Request 50: Gemini (score: 15) → Success ✅
```

---

### Afternoon - Model Issues

```bash
# Suddenly, Gemini starts hitting rate limits
python gh_ai_core.py ask "Debug this issue"
```

**What happens:**
```
☁️  Using cloud model: google/gemini-2.0-flash-exp:free
⚠️  Rate limit hit for google/gemini-2.0-flash-exp:free
🔄 Trying next cloud model...
☁️  Using cloud model: mistralai/mistral-7b-instruct:free
```

**System automatically:**
1. Detects Gemini is rate limited
2. Records the failure (updates score to 75+)
3. Switches to next-best model (Mistral)
4. Delivers your answer without interruption

---

### Check Rankings After Issues

```bash
./monitor.sh rankings
```

**Output:**
```
====================================================================================================
🎯 MODEL RANKINGS - Real-time Performance & Availability
====================================================================================================
Rank   Model                               Score    Success   Latency    Usage        Status
----------------------------------------------------------------------------------------------------
1      Mistral 7B Instruct Free            28.7/100 95.2%     312ms      42/1000      🟡 Good
2      Meta Llama 3.2 3B Free              45.1/100 89.3%     498ms      156/1000     🟡 Good
3      Google Gemini 2.0 Flash Free        78.9/100 87.5%     245ms      1000/1000    🔴 Poor
4      DeepSeek R1 Free                    92.3/100 65.0%     1205ms     892/1000     🔴 Poor
----------------------------------------------------------------------------------------------------
```

**Insight**: 
- Gemini is now scored poorly (78.9) due to rate limit
- Mistral has taken the #1 spot
- System will prioritize Mistral for next requests

---

### Interactive Chat Session

```bash
python gh_ai_core.py chat
```

**Session:**
```
You: rankings

🎯 MODEL RANKINGS - Real-time Performance & Availability
====================================================================================================
Rank   Model                               Score    Success   Latency    Usage        Status
----------------------------------------------------------------------------------------------------
1      Mistral 7B Instruct Free            28.7/100 95.2%     312ms      42/1000      🟡 Good
...

You: recommend

🎯 Recommended: Mistral 7B Instruct Free
   Model ID: mistralai/mistral-7b-instruct:free
   Quality: GOOD (score: 28.7/100)
   Success Rate: 95.2%
   Avg Latency: 312ms
   Today's Usage: 42/1000

You: What's the time complexity of quicksort?

AI: Quicksort has an average time complexity of O(n log n)...
```

---

### Evening - Review Daily Stats

```bash
./monitor.sh stats
```

**Output:**
```
📊 Usage statistics for last 7 days:

🤖 google/gemini-2.0-flash-exp:free
   Requests: 542
   Tokens: 125,340
   Cost: $0.0000

🤖 mistralai/mistral-7b-instruct:free
   Requests: 178
   Tokens: 42,890
   Cost: $0.0000

🤖 meta-llama/llama-3.2-3b-instruct:free
   Requests: 89
   Tokens: 18,230
   Cost: $0.0000

📈 Totals:
   Total Requests: 809
   Total Tokens: 186,460
   Total Cost: $0.0000
```

**Insights**:
- Used 809 requests across 3 models
- Saved money by using free models
- Load distributed automatically based on availability

---

## Scenario: Model Goes Down

### What Happens Without Monitoring

```bash
# Old behavior (v1.0.0)
python gh_ai_core.py ask "Help me"

# Output:
❌ Error: 429 Rate Limit Exceeded
# User has to manually retry or wait
```

### What Happens With Monitoring (v1.1.0)

```bash
python gh_ai_core.py ask "Help me"

# Behind the scenes:
Try Gemini → Rate Limited
Try Mistral → Rate Limited  
Try Llama → Success! ✅

# User sees:
AI: I'm happy to help! What do you need assistance with?
```

**The difference**: Seamless, automatic fallback. User never knows there was an issue.

---

## Scenario: Comparing Models

### See Performance Head-to-Head

```bash
./monitor.sh rankings
```

```
Rank   Model                    Score    Success   Latency    Status
1      Gemini 2.0 Flash         12.3     98.5%     245ms      🟢 Excellent
2      Mistral 7B              28.7     95.2%     312ms      🟡 Good
3      Llama 3.2 3B            45.1     89.3%     498ms      🟡 Good
4      DeepSeek R1             67.8     75.0%     1205ms     🟠 Fair
```

**Insights**:
- **Gemini** is fastest and most reliable
- **Mistral** is a solid second choice
- **Llama** works but is slower
- **DeepSeek** has reliability issues

---

## Scenario: First-Time User

```bash
# Install and run demo
git clone https://github.com/zebadiee/gh-ai-assistant.git
cd gh-ai-assistant
pip install -r requirements.txt
./monitor.sh demo
```

**Demo Output** (automatically generates test data):
```
================================================================================
🎯 MODEL MONITORING & DYNAMIC SELECTION DEMO
================================================================================

📊 Step 1: Simulating API requests to build performance data...
  ✅ google/gemini-2.0-flash-exp:free: 245ms
  ✅ mistralai/mistral-7b-instruct:free: 312ms
  ...

📊 Step 2: Current Model Rankings
[Shows ranking table]

🎯 Step 3: Smart Model Selection
[Shows recommendation]

🔄 Step 4: Automatic Fallback Sequence
[Shows fallback order]

📈 Step 5: Detailed Model Statistics
[Shows detailed stats]
```

**Takeaway**: User understands the system in 30 seconds.

---

## Advanced: Programmatic Usage

```python
from model_monitor import ModelMonitor, SmartModelSelector
from gh_ai_core import TokenManager, FREE_MODELS

# Initialize
monitor = ModelMonitor()
token_manager = TokenManager()
selector = SmartModelSelector(monitor, FREE_MODELS, token_manager)

# Custom workflow
for task in tasks:
    # Get best model for this task
    model_id = selector.select_model(task_type="code")
    
    # Make request
    response = make_request(model_id, task)
    
    # Record outcome
    monitor.record_request(
        model_id=model_id,
        success=response.ok,
        latency_ms=response.elapsed.total_seconds() * 1000,
        tokens_used=response.usage.total_tokens
    )
    
    # If failed, mark for session
    if not response.ok:
        selector.mark_failure(model_id, error_type="timeout")
```

---

## Real-World Impact

### Before Monitoring (v1.0.0)

**Daily Experience:**
- Morning: Gemini works great ✅
- Afternoon: Gemini rate limited ❌
- User action: Manually retry or wait
- Frustration: High
- Success rate: ~70%

### After Monitoring (v1.1.0)

**Daily Experience:**
- Morning: Gemini works great ✅
- Afternoon: Auto-switches to Mistral ✅
- User action: None required
- Frustration: None
- Success rate: ~98%

**Result**: 28% improvement in success rate, zero user intervention required.

---

## Tips for Power Users

### 1. Check Rankings Before Heavy Work
```bash
./monitor.sh recommend
# Use the recommended model for best results
```

### 2. Monitor During Peak Hours
```bash
# Run this in a loop to see real-time changes
watch -n 60 './monitor.sh recommend'
```

### 3. Export Stats for Analysis
```bash
# Get detailed stats for a specific model
python model_monitor.py --stats "google/gemini-2.0-flash-exp:free"
```

### 4. Reset After Maintenance
```bash
# Clear old data if OpenRouter had maintenance
./monitor.sh clear
```

---

## Conclusion

The monitoring system transforms the gh-ai-assistant from a simple API wrapper into an **intelligent, self-optimizing AI platform** that:

✅ Automatically selects the best model  
✅ Seamlessly handles failures  
✅ Learns from real usage patterns  
✅ Maximizes success rates  
✅ Minimizes latency  
✅ Requires zero configuration  

**Just ask your question, and the system handles the rest!**

---

**Ready to try it?**

```bash
cd gh-ai-assistant
git pull
./monitor.sh demo
python gh_ai_core.py ask "Show me what you can do!"
```
