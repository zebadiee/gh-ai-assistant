# 🧭 Conversation Navigator - Never Feel Lost

## The Problem

With a multi-layer AI system (rotation, transfer, bridge, integrity, persistence), you can lose track of "where you are" in complex conversations:

- **Bridge activated?** Not sure if waiting or active
- **What was I asking?** Forgot the context
- **Where did we leave off?** Long session, lost track
- **Is anything pending?** Uncertainty about state

## The Solution

**Instant clarity commands** that tell you exactly where you are at any moment.

## Quick Commands

### Where Am I? (Complete Orientation)

```bash
python conversation_navigator.py --where-am-i
```

Shows everything:
- Current session state
- Last 5 exchanges
- Bridge status (if active)
- Quick resume info

### Current Status

```bash
python conversation_navigator.py --status
```

Output:
```
╔══════════════════════════════════════════════════════════════════════╗
║                    CONVERSATION STATE SNAPSHOT                       ║
╚══════════════════════════════════════════════════════════════════════╝

👤 USER: Declan
🤖 ASSISTANT: Brakel
📊 CONVERSATION: #42
⏰ LAST ACTIVE: 2025-01-15 14:30:15

✅ STATUS: ACTIVE on google/gemini-2.0-flash-exp:free

💬 LAST EXCHANGE:
   You: Help me implement authentication...
   AI: Here's how to build FastAPI auth...

📝 CONTEXT:
   Working on: Auth system, FastAPI, JWT tokens
```

### Conversation Recap

```bash
# Last 10 exchanges (default)
python conversation_navigator.py --recap 10

# Last 5 exchanges
python conversation_navigator.py --recap 5
```

Output:
```
╔══════════════════════════════════════════════════════════════════════╗
║                      CONVERSATION RECAP                              ║
╚══════════════════════════════════════════════════════════════════════╝

1. [14:25:30] 👤 YOU:
   Help me implement authentication

2. [14:25:35] 🤖 AI:
   Here's how to build FastAPI authentication...

3. [14:26:10] 👤 YOU:
   Add JWT token support

4. [14:26:15] 🤖 AI:
   For JWT tokens, you'll need python-jose...
```

### Session Timeline

```bash
# Last 24 hours (default)
python conversation_navigator.py --timeline 24

# Last 2 hours
python conversation_navigator.py --timeline 2
```

Output:
```
╔══════════════════════════════════════════════════════════════════════╗
║                      SESSION TIMELINE                                ║
╚══════════════════════════════════════════════════════════════════════╝

📅 Period: Last 24 hours
💬 Total Messages: 28
🔄 Total Exchanges: 14

1. [09:15:00]
   👤 Start new authentication project...
   🤖 Let's build a FastAPI auth system...

2. [10:30:00]
   👤 Implement JWT tokens...
   🤖 Here's the JWT implementation...
```

### Bridge Status Check

```bash
python conversation_navigator.py --bridge
```

Output (if bridge active):
```
🌉 MEMORY BRIDGE ACTIVE
   Pending: Implement token blacklisting with audit logging...
   Expected recovery: 300 seconds
```

Output (if normal):
```
✅ No bridge active - session running normally
```

### Quick Resume Info

```bash
python conversation_navigator.py --resume
```

Output (if bridge):
```
🌉 MEMORY BRIDGE ACTIVE

Your conversation is safely preserved.

WHAT WAS I DOING?
  You asked: "Implement token blacklisting with audit logging..."

WHEN WILL IT RESUME?
  Waiting for any cloud model to become available
  Typically: 2-5 minutes

WHAT SHOULD I DO?
  Option 1: Wait - conversation will resume automatically
  Option 2: Check model status: python gh_ai_core.py models
  Option 3: Use local model: python gh_ai_core.py ask --ollama "your question"

YOUR CONTEXT IS SAFE. Nothing is lost.
```

Output (if active):
```
✅ ACTIVE SESSION

WHAT WAS I DOING?
  Last exchange: "Help me implement authentication..."
  AI responded: "Here's how to build FastAPI authentication..."

CURRENT STATE:
  Model: google/gemini-2.0-flash-exp:free
  Conversation: #42
  Time: 14:30:15

READY TO CONTINUE!
  Use: python gh_ai_core.py chat
  Or: python gh_ai_core.py ask "your question"
```

## Use Cases

### Morning Catch-Up

```bash
# What was I working on yesterday?
python conversation_navigator.py --timeline 24

# Show me the conversation
python conversation_navigator.py --recap 10
```

### Mid-Session Orientation

```bash
# Wait, where was I?
python conversation_navigator.py --where-am-i
```

### Bridge Confusion

```bash
# Am I waiting or active?
python conversation_navigator.py --bridge

# What was my pending question?
python conversation_navigator.py --resume
```

### Long Session Recovery

```bash
# Remind me what we covered
python conversation_navigator.py --recap 20

# Full context please
python conversation_navigator.py --status
```

## Integration with gh_ai_core.py

Add to your workflow:

```bash
# Before starting work
python conversation_navigator.py --where-am-i

# Work session
python gh_ai_core.py chat

# After interruption
python conversation_navigator.py --resume
```

## Programmatic Usage

```python
from conversation_navigator import ConversationNavigator

nav = ConversationNavigator()

# Get current state
state = nav.get_current_state()
print(f"Active: {not state.bridge_active}")
print(f"Model: {state.current_model}")

# Get recap
recap = nav.get_conversation_recap(10)
for msg in recap:
    print(f"{msg['role']}: {msg['content'][:50]}...")

# Check bridge
active, prompt, eta = nav.check_bridge_status()
if active:
    print(f"Waiting on: {prompt}")

# Quick resume
resume_info = nav.get_quick_resume_info()
print(resume_info)
```

## Commands Reference

```bash
# Complete orientation (recommended for confusion)
python conversation_navigator.py --where-am-i

# Current state snapshot
python conversation_navigator.py --status

# Conversation recap (last N exchanges)
python conversation_navigator.py --recap 10

# Session timeline (last N hours)
python conversation_navigator.py --timeline 24

# Bridge status check
python conversation_navigator.py --bridge

# Quick resume information
python conversation_navigator.py --resume

# Help
python conversation_navigator.py --help
```

## What Gets Tracked

### Conversation State
- User name, assistant name
- Current model in use
- Conversation count
- Last activity timestamp
- Bridge status
- Pending prompts

### Exchange History
- All user messages
- All assistant responses
- Timestamps for everything
- Chronological ordering

### Context Analysis
- Extracted topics/keywords
- Technical terms detected
- Project focus areas
- Working context summary

## Benefits

### Never Feel Lost

✅ **Instant orientation** - Know where you are in seconds  
✅ **Context preservation** - Never forget what you were doing  
✅ **Bridge clarity** - Understand wait states  
✅ **Timeline view** - See conversation flow  

### Productive Recovery

✅ **Quick resume** - Get back to work fast  
✅ **Session recap** - Remember previous discussions  
✅ **Status awareness** - Know if active or waiting  
✅ **Smart summaries** - Auto-generated context  

### Advanced Sessions

✅ **Multi-day continuity** - Pick up days later  
✅ **Long conversations** - Navigate hours of chat  
✅ **Bridge recovery** - Resume after exhaustion  
✅ **Pattern recognition** - See conversation evolution  

## Best Practices

### Start Each Session

```bash
# Morning routine
python conversation_navigator.py --where-am-i
python gh_ai_core.py chat
```

### After Interruptions

```bash
# Just got back, what was I doing?
python conversation_navigator.py --resume
```

### When Confused

```bash
# Complete re-orientation
python conversation_navigator.py --where-am-i

# Or specific checks
python conversation_navigator.py --bridge  # Am I waiting?
python conversation_navigator.py --status  # Where am I?
python conversation_navigator.py --recap 5 # What happened?
```

### End of Day

```bash
# Review what was accomplished
python conversation_navigator.py --timeline 8

# Save mental note of context
python conversation_navigator.py --status
```

## Troubleshooting

### "No active session"

```bash
# Start a session first
python session_manager.py --init
```

### "No conversation history"

```bash
# Have a conversation first
python gh_ai_core.py chat
```

### Stale timestamps

```bash
# Check if database needs reset
ls -la ~/.gh-ai-assistant/conversations.db

# If corrupted, backup and start fresh
mv ~/.gh-ai-assistant/conversations.db ~/.gh-ai-assistant/conversations.db.bak
```

## Conclusion

The Conversation Navigator ensures you **never feel lost** in complex AI sessions.

Whether you're:
- Resuming after a bridge
- Picking up days later
- Mid-long-conversation
- Just plain confused

**One command gives you complete clarity.**

Your advanced AI system is powerful—now you have the navigation tools to match.

---

**Quick Tip**: Add an alias to your shell:

```bash
# In ~/.bashrc or ~/.zshrc
alias whereami="python ~/gh-ai-assistant/conversation_navigator.py --where-am-i"
alias airecap="python ~/gh-ai-assistant/conversation_navigator.py --recap 10"
alias aistatus="python ~/gh-ai-assistant/conversation_navigator.py --status"
```

Then just type: `whereami` anytime you're lost! 🧭
