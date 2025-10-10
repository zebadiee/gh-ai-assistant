# 🚀 Memory Transfer Quick Start

**Get intelligent model handoffs working in 2 minutes**

## What Is It?

Automatically preserves conversation context when switching AI models due to token limits. No more "I don't remember what we discussed" after model rotation.

## Installation

```bash
cd gh-ai-assistant
pip install -e .
```

## Instant Usage

It works automatically! Just use the assistant normally:

```bash
# Chat mode - handoffs happen transparently
python gh_ai_core.py chat

# Ask mode - context preserved across multiple calls
python gh_ai_core.py ask "Help me with authentication"
python gh_ai_core.py ask "Now add JWT support"
python gh_ai_core.py ask "Add refresh tokens"  # May trigger handoff
```

## How It Works (Simplified)

```
Your conversation uses 1600 tokens → System predicts next response will add 150 tokens
→ Total would be 1750/2048 (85%) → Triggers handoff at 80% threshold
→ Compresses last 6 messages + code context to 145 tokens
→ Switches to model with larger context window
→ Injects compressed context → You get seamless response
```

## View Statistics

```bash
# See handoff history
python gh_ai_core.py memory
```

Output:
```json
{
  "total_handoffs": 5,
  "avg_tokens_saved": 1250,
  "models_used": ["llama-3.2-3b", "deepseek-r1", "gemini-flash"]
}
```

## Real Example

```
You: I'm building a FastAPI authentication system
AI: [llama-3.2-3b] Great! Here's how to start...

You: Show me JWT implementation
AI: [llama-3.2-3b] Here's a complete example...

You: Add refresh tokens with rotation and blacklisting
🔄 Intelligent Handoff Triggered
   Reason: Predicted 85% usage (1750/2048 tokens)
   Transferring to: deepseek-r1:free
   Memory compressed: 145 tokens

AI: [deepseek-r1] Continuing from our FastAPI auth discussion...
[Provides complete implementation with full context]
```

## When Does It Handoff?

Handoffs trigger when predicted token usage hits **80%**:

| Current | Predicted | Action |
|---------|-----------|--------|
| 1000 | 1100 (55%) | ✅ Continue same model |
| 1600 | 1750 (85%) | 🔄 Handoff to larger model |
| 3500 | 3800 (92%) | 🔄 Handoff immediately |

## What Gets Preserved?

**Priority allocation (300 tokens max):**
- 45% Technical context (code, APIs, errors)
- 30% Project state (goals, features, status)
- 20% Conversation flow (recent messages)
- 5% Metadata (timestamps, counts)

## Configuration

### Change Handoff Threshold

Edit `memory_transfer.py`:
```python
HANDOFF_THRESHOLD = 0.80  # Default: 80%

# Lower = more handoffs, better context preservation
HANDOFF_THRESHOLD = 0.70  # Conservative

# Higher = fewer handoffs, more efficient
HANDOFF_THRESHOLD = 0.90  # Aggressive
```

### Adjust Memory Budget

```python
MEMORY_BUDGET_PERCENT = 0.15  # 15% of context window
MAX_MEMORY_TOKENS = 300       # Cap at 300 tokens
MIN_MEMORY_TOKENS = 40        # Minimum for small models
```

## Testing

```bash
# Run comprehensive tests
cd gh-ai-assistant
source venv/bin/activate
python test_memory_transfer.py
```

## Programmatic Usage

```python
from memory_transfer import MemoryTransferManager

manager = MemoryTransferManager()

# Check if handoff needed
should_handoff, predicted, reason = manager.should_handoff(
    current_model="llama-3.2-3b",
    current_tokens=1600,
    next_prompt="Your question here"
)

if should_handoff:
    # Execute handoff
    transfer_prompt, context = manager.execute_handoff(
        from_model="llama-3.2-3b",
        to_model="deepseek-r1:free",
        current_tokens=1600,
        predicted_tokens=predicted,
        conversation_history=your_history,
        new_prompt="Your question here"
    )
    
    # Use transfer_prompt with new model
    response = new_model.ask(transfer_prompt)
```

## Benefits

✅ **Zero user interruption** - Handoffs are transparent  
✅ **Context preservation** - AI remembers discussion  
✅ **Token efficiency** - 40-300 token memory overhead  
✅ **Smart selection** - Picks best model for handoff  
✅ **Predictive** - Prevents mid-response cutoffs  

## Troubleshooting

**Memory transfer not working?**
```bash
# Check availability
python -c "from memory_transfer import MemoryTransferManager; print('✅ OK')"

# If error, install dependencies
pip install tiktoken
```

**Too many handoffs?**
- Increase threshold to 0.85 or 0.90
- Use models with larger context windows

**Not enough handoffs?**
- Decrease threshold to 0.70 or 0.75
- Check memory statistics for patterns

## Full Documentation

See [MEMORY_TRANSFER_GUIDE.md](MEMORY_TRANSFER_GUIDE.md) for:
- Architecture details
- Advanced configuration
- Performance optimization
- Integration examples
- Best practices

## Support

Questions? Check:
1. [MEMORY_TRANSFER_GUIDE.md](MEMORY_TRANSFER_GUIDE.md) - Complete guide
2. `python test_memory_transfer.py` - Run tests
3. `python gh_ai_core.py memory` - View stats
4. [README.md](README.md) - Main documentation

---

**Quick Tip**: The system works automatically. Just use your assistant normally and it handles everything behind the scenes!
