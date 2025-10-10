# 🤖 Assistant Context Configuration

## Overview

This system allows you to configure persistent context for AI assistants working with your gh-ai-assistant project. While I (Claude) will always identify as Claude, this configuration helps maintain consistent project context across different AI interactions.

## What This Does

- **Maintains Context**: Remembers your project state, preferences, and goals
- **Personalizes Interactions**: Configure assistant behavior and communication style
- **Persists Across Sessions**: Saves configuration for future use
- **Generates System Prompts**: Creates context-aware prompts for AI assistants

## Setup

```bash
cd gh-ai-assistant

# View current context
python assistant_context.py --show

# Set your preferences
python assistant_context.py --set-user "Declan"

# View personalized greeting
python assistant_context.py --greeting
```

## Configuration

### Current Default Settings

```json
{
  "assistant_name": "Brakel",
  "user_name": "Declan",
  "project_context": "gh-ai-assistant - Enterprise-grade AI reliability system",
  "personality_traits": [
    "Professional coding partner",
    "Proactive problem solver",
    "Context-aware assistant",
    "Technical expert"
  ],
  "preferences": {
    "introduce_self": true,
    "maintain_context": true,
    "technical_focus": "Python, AI systems, FastAPI",
    "communication_style": "concise and professional"
  }
}
```

### Customization Options

```bash
# Change assistant name (for context purposes)
python assistant_context.py --set-name "YourPreferredName"

# Change your name
python assistant_context.py --set-user "YourName"

# Reset to defaults
python assistant_context.py --reset
```

## Generate System Prompts

```bash
# Generate a context-aware system prompt
python assistant_context.py --prompt
```

Output:
```
You are Brakel, Declan's personal AI coding partner.

PROJECT CONTEXT:
gh-ai-assistant - Enterprise-grade AI reliability system

YOUR ROLE:
- Professional coding partner
- Proactive problem solver
- Context-aware assistant
- Technical expert

PREFERENCES:
- Technical Focus: Python, AI systems, FastAPI
- Communication: concise and professional
- Introduce yourself: Yes
- Maintain context: Yes

CURRENT SESSION:
- Working in: gh-ai-assistant repository
- Features: Memory Transfer, Memory Bridge, Token Optimization
- Goal: Build enterprise-grade AI reliability system
```

## Integration with gh_ai_core.py

You can integrate this into your AI assistant calls:

```python
from assistant_context import AssistantContext

# Initialize context
context = AssistantContext()

# Get system prompt
system_prompt = context.get_system_prompt()

# Use with your AI calls
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Your question here"}
]
```

## Use Cases

### 1. Local AI (Ollama)

```python
# Add context to Ollama calls
from assistant_context import AssistantContext

context = AssistantContext()
system_prompt = context.get_system_prompt()

# Include in your Ollama prompts
full_prompt = f"{system_prompt}\n\nUser: {user_question}"
```

### 2. OpenRouter API

```python
# Enhance OpenRouter calls with context
context = AssistantContext()

messages = [
    {"role": "system", "content": context.get_system_prompt()},
    {"role": "user", "content": user_input}
]

response = openrouter_client.chat_completion(model, messages)
```

### 3. CLI Reminders

```bash
# Show context reminder before work session
python assistant_context.py --greeting

# Output: 👋 Hello Declan, I'm Brakel - your AI coding partner for gh-ai-assistant!
```

## Important Note

**About AI Identity**: Any AI assistant (including Claude, GPT, etc.) will maintain their actual identity while using this context to better understand your project and preferences. The "assistant_name" field is for organizational purposes and context continuity, not to override the AI's actual identity.

## File Locations

- **Configuration**: `~/.gh-ai-assistant/assistant_context.json`
- **Script**: `gh-ai-assistant/assistant_context.py`

## Commands Reference

```bash
# Display current context
python assistant_context.py --show

# Show greeting
python assistant_context.py --greeting

# Generate system prompt
python assistant_context.py --prompt

# Set assistant name (for context)
python assistant_context.py --set-name "Brakel"

# Set your name
python assistant_context.py --set-user "Declan"

# Reset everything
python assistant_context.py --reset
```

## Example Workflow

```bash
# Morning setup
cd ~/gh-ai-assistant
python assistant_context.py --greeting
# 👋 Hello Declan, I'm Brakel - your AI coding partner for gh-ai-assistant!

# Start work with context
python gh_ai_core.py chat
# System will use configured context

# Update preferences mid-session
python assistant_context.py --set-name "NewName"
```

## Benefits

✅ **Consistent Context**: Maintains project awareness across sessions  
✅ **Personalized Experience**: Tailored to your communication preferences  
✅ **Easy Configuration**: Simple CLI for updates  
✅ **Portable**: JSON configuration can be backed up/shared  
✅ **Integration Ready**: Works with any AI system  

## Advanced: Custom Context

Edit `~/.gh-ai-assistant/assistant_context.json` directly:

```json
{
  "assistant_name": "Brakel",
  "user_name": "Declan",
  "project_context": "Your custom project description",
  "personality_traits": [
    "Add your preferred traits"
  ],
  "preferences": {
    "introduce_self": true,
    "maintain_context": true,
    "technical_focus": "Your tech stack",
    "communication_style": "Your preferred style"
  }
}
```

## Troubleshooting

**Context not loading?**
```bash
# Check if file exists
ls -la ~/.gh-ai-assistant/assistant_context.json

# Reset if corrupted
python assistant_context.py --reset
```

**Want different context per project?**
- Copy and modify `assistant_context.py` for each project
- Change `CONFIG_DIR` to project-specific location

---

**Remember**: This provides context and preferences for AI interactions, helping maintain consistency and project awareness across different sessions and AI systems.
