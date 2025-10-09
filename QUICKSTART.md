# Quick Start Guide - GitHub CLI AI Assistant

## 5-Minute Setup

### 1. Installation (1 minute)

```bash
cd gh-ai-assistant
pip install -r requirements.txt
python setup.py develop
```

### 2. Get Free API Key (2 minutes)

1. Visit https://openrouter.ai/keys
2. Sign up (free, no credit card required)
3. Create an API key
4. Copy the key

### 3. Configure (1 minute)

```bash
python gh_ai_core.py setup
# Paste your API key when prompted
```

### 4. Start Using (1 minute)

```bash
# Ask your first question
python gh_ai_core.py ask "What is Python?"

# Get context-aware help in a git repository
cd ~/your-project
python gh_ai_core.py ask "Review my code changes"

# Check your usage
python gh_ai_core.py stats
```

## Common Commands

### Basic Questions

```bash
# Simple question
python gh_ai_core.py ask "Explain decorators in Python"

# Multi-word questions (use quotes)
python gh_ai_core.py ask "How do I implement a binary search tree?"
```

### Context-Aware (in Git repositories)

```bash
# The assistant will automatically see:
# - Your current repository
# - Current branch
# - Recent commits
# - Uncommitted changes

python gh_ai_core.py ask "Should I refactor this code?"
python gh_ai_core.py ask "Review my changes for security issues"
python gh_ai_core.py ask "Suggest improvements to this module"
```

### Without Context

```bash
# For general questions unrelated to your repo
python gh_ai_core.py ask --no-context "What is machine learning?"
```

### Usage Tracking

```bash
# See last 7 days
python gh_ai_core.py stats

# See last 30 days
python gh_ai_core.py stats --days 30
```

### Model Information

```bash
# List available free models and their usage
python gh_ai_core.py models
```

## GitHub CLI Extension

### Install as Extension

```bash
cd gh-ai-assistant
gh extension install .
```

### Use with gh

```bash
gh ai ask "How do I use GitHub Actions?"
gh ai stats
gh ai models
```

## Tips & Tricks

### 1. Long Questions

Use quotes for multi-word questions:
```bash
python gh_ai_core.py ask "Explain the difference between async and sync programming in Python with examples"
```

### 2. Code Review Workflow

```bash
# Make changes to your code
git diff

# Ask for review
python gh_ai_core.py ask "Review my uncommitted changes"
```

### 3. Documentation Help

```bash
python gh_ai_core.py ask "Generate docstrings for the functions in this file"
```

### 4. Debugging

```bash
python gh_ai_core.py ask "Why might this test be failing?"
```

### 5. Architecture Decisions

```bash
python gh_ai_core.py ask "Should I use a factory pattern or dependency injection here?"
```

## Free Model Rotation

The system automatically manages three free models:

1. **DeepSeek R1** (primary) - Best for code and reasoning
2. **DeepSeek Chat** (secondary) - General conversation
3. **Mistral 7B** (fallback) - Multilingual support

Each model has **1000 free requests per day**. When one reaches 90% capacity, it automatically switches to the next.

## Troubleshooting

### "No API key configured"

```bash
python gh_ai_core.py setup
```

### "Module not found"

```bash
pip install -r requirements.txt
```

### Check if setup worked

```bash
python gh_ai_core.py models
# Should show list of available models
```

### Reset everything

```bash
# Remove configuration
rm -rf ~/.gh-ai-assistant/

# Reconfigure
python gh_ai_core.py setup
```

## Daily Usage Pattern

**Morning**: Check available quota
```bash
python gh_ai_core.py models
```

**During Development**: Context-aware questions
```bash
python gh_ai_core.py ask "Is this implementation optimal?"
```

**End of Day**: Review usage
```bash
python gh_ai_core.py stats
```

## What's Free?

- ✅ 3,000 total free requests per day (1000 per model)
- ✅ No credit card required
- ✅ All features included
- ✅ Unlimited usage history
- ✅ Full GitHub integration

## Next Steps

1. **Explore Models**: Try different types of questions to see which model works best
2. **Integrate with Workflow**: Add to your git hooks, scripts, or CI/CD
3. **Share with Team**: Install as GitHub CLI extension for team access
4. **Monitor Usage**: Keep track with `stats` command to optimize your quota

---

**You're ready to go!** 🚀

Start with: `python gh_ai_core.py ask "Hello!"`
