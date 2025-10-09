# GitHub CLI AI Assistant

**Production-ready GitHub CLI extension** with intelligent token management, automatic model rotation, and free-tier optimization.

## 🎯 Features

### **Intelligent Token Management**
- **Auto-rotation**: Automatically switches between models when approaching 90% usage limits
- **Usage tracking**: SQLite database records all token consumption with detailed analytics
- **Secure storage**: API keys encrypted using system keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- **Real-time monitoring**: Live usage stats and model availability

### **Free Model Prioritization**
Prioritizes these OpenRouter free models:

1. **DeepSeek R1 Free** - 1000 requests/day, 131K context window (reasoning, math, code)
2. **DeepSeek Chat Free** - 1000 requests/day, 32K context window (general conversation)
3. **Mistral 7B Free** - 1000 requests/day, 32K context window (multilingual, efficiency)

### **GitHub Integration**
- **Context-aware responses**: Automatically includes repository info, current branch, recent commits
- **Git integration**: Analyzes uncommitted changes for better code review
- **CLI extension**: Works seamlessly with `gh` GitHub CLI
- **Team sharing**: Easy distribution via GitHub CLI extension system

## 🚀 Quick Start

### Installation

```bash
# Clone or download this repository
cd gh-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Install in development mode
python setup.py develop

# Or install as GitHub CLI extension
gh extension install .
```

### Setup

```bash
# Configure your OpenRouter API key
python gh_ai_core.py setup

# Or if installed as gh extension
gh ai setup
```

**⚠️ CRITICAL: Enable Model Training**

After getting your API key, you **must** enable "Model Training" in OpenRouter settings:

1. Visit: https://openrouter.ai/settings/privacy
2. Enable "Model Training" toggle
3. Save settings

**Without this, you'll get rate limits even with credits!** See [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for details.

Get your free OpenRouter API key at: https://openrouter.ai/keys

### Basic Usage

```bash
# Ask a question with GitHub context
python gh_ai_core.py ask "How can I optimize this code?"

# Ask without context
python gh_ai_core.py ask --no-context "Explain async/await in Python"

# View usage statistics
python gh_ai_core.py stats --days 7

# List available models
python gh_ai_core.py models
```

### GitHub CLI Extension Usage

```bash
# Once installed as gh extension
gh ai ask "Review this repository structure"
gh ai stats --days 30
gh ai models
```

## 📊 Usage Examples

### Context-Aware Code Review

```bash
# The assistant will automatically include:
# - Current repository information
# - Active branch
# - Recent commits
# - Uncommitted changes

gh ai ask "Review my recent changes and suggest improvements"
```

### Model Rotation Example

```bash
# First 900 requests use DeepSeek R1 Free
gh ai ask "Explain this algorithm"
# → Using: deepseek/deepseek-r1:free

# When approaching limit (900+ requests), auto-rotates
gh ai ask "Another question"
# → Using: deepseek/deepseek-chat:free
```

### Usage Analytics

```bash
gh ai stats --days 7
```

Output:
```
📊 Usage statistics for last 7 days:

🤖 deepseek/deepseek-r1:free
   Requests: 45
   Tokens: 12,450
   Cost: $0.0000

🤖 deepseek/deepseek-chat:free
   Requests: 23
   Tokens: 8,230
   Cost: $0.0000

📈 Totals:
   Total Requests: 68
   Total Tokens: 20,680
   Total Cost: $0.0000
```

## 🔧 Architecture

### Core Components

#### **TokenManager**
- SQLite database for usage tracking
- Automatic model rotation based on usage
- Daily limit management (90% threshold)
- Historical usage analytics

#### **OpenRouterClient**
- Full OpenRouter API integration
- Proper headers for attribution
- Error handling and timeout management
- Rate limit detection

#### **GitHubContextExtractor**
- Extracts repository information
- Detects current branch and commits
- Analyzes uncommitted changes
- Builds context-aware prompts

#### **AIAssistant**
- Main orchestration layer
- Secure credential management
- Prompt enhancement with context
- Response formatting

### Data Flow

```
User Input
    ↓
AIAssistant.ask()
    ↓
TokenManager.get_optimal_model() → Selects best available free model
    ↓
GitHubContextExtractor → Adds repository context
    ↓
OpenRouterClient.chat_completion() → API request
    ↓
TokenManager.record_usage() → Track usage
    ↓
Response to User
```

## 🔐 Security

### API Key Storage
- **macOS**: Keychain Access
- **Windows**: Windows Credential Manager
- **Linux**: Secret Service (GNOME Keyring, KWallet)

### No Credentials in Files
- Zero plaintext API keys
- No environment variables required
- Secure system-level storage only

### Network Security
- HTTPS only connections
- Timeout protections
- Error sanitization

## 📈 Free Model Optimization

### OpenRouter Free Tiers

| Model | Daily Limit | Credits | No Credits | Context | Best For |
|-------|-------------|---------|------------|---------|----------|
| DeepSeek R1 Free | 1000 | Yes | 50 | 131K | Reasoning, code |
| DeepSeek Chat Free | 1000 | Yes | 50 | 32K | General chat |
| Mistral 7B Free | 1000 | Yes | 50 | 32K | Multilingual |

### Smart Rotation Strategy

1. **Primary**: DeepSeek R1 Free (best for code/reasoning)
2. **Secondary**: DeepSeek Chat Free (general questions)
3. **Fallback**: Mistral 7B Free (when others exhausted)

The system monitors usage and rotates at 90% capacity to prevent rate limiting.

## 🛠️ Advanced Usage

### Custom Prompts

```bash
# Code review
gh ai ask "Review this commit for security issues"

# Architecture advice
gh ai ask "Should I refactor this module?"

# Documentation help
gh ai ask "Generate docstrings for this file"

# Bug diagnosis
gh ai ask "Why is this test failing?"
```

### Integration with Git Workflows

```bash
# Pre-commit hook integration
git diff | gh ai ask "Check this diff for issues"

# PR review automation
gh ai ask "Summarize changes in this PR"

# Commit message generation
git diff --cached | gh ai ask "Generate a commit message"
```

## 📦 Distribution

### As GitHub CLI Extension

```bash
# Users can install directly from GitHub
gh extension install yourusername/gh-ai-assistant

# Or from local directory
gh extension install .

# Upgrade
gh extension upgrade gh-ai-assistant
```

### As Python Package

```bash
# Install from PyPI (when published)
pip install gh-ai-assistant

# Or from source
pip install git+https://github.com/yourusername/gh-ai-assistant.git
```

## 🧪 Testing

```bash
# Test basic functionality
python gh_ai_core.py models

# Test with actual query (requires API key)
python gh_ai_core.py ask "Hello, world!"

# Check usage tracking
python gh_ai_core.py stats
```

## 🔄 Updates and Maintenance

### Adding New Free Models

Edit `FREE_MODELS` in `gh_ai_core.py`:

```python
FREE_MODELS = [
    {
        "id": "provider/new-model:free",
        "name": "New Model Free",
        "daily_limit": 1000,
        "context_window": 32768,
        "best_for": "specific tasks",
        "cost_per_1k_tokens": 0.0
    }
]
```

### Database Schema

The SQLite database (`~/.gh-ai-assistant/usage.db`) stores:

```sql
CREATE TABLE usage (
    id INTEGER PRIMARY KEY,
    model TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER NOT NULL,
    request_count INTEGER DEFAULT 1,
    cost REAL DEFAULT 0.0
);
```

## 🐛 Troubleshooting

### API Key Issues

```bash
# Reset API key
python gh_ai_core.py setup
```

### Permission Errors

```bash
# Check config directory permissions
ls -la ~/.gh-ai-assistant/

# Fix if needed
chmod 755 ~/.gh-ai-assistant/
```

### Database Locked

```bash
# Check for running processes
ps aux | grep gh_ai_core

# Reset database (WARNING: loses history)
rm ~/.gh-ai-assistant/usage.db
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🔗 Links

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **GitHub CLI Extensions**: https://docs.github.com/en/github-cli/github-cli/using-github-cli-extensions
- **DeepSeek API**: https://api-docs.deepseek.com/

## 🎉 Acknowledgments

- OpenRouter for providing free AI model access
- DeepSeek for powerful free models
- GitHub CLI team for extension framework

---

**Ready for immediate deployment and use!** 🚀

Get started: `python gh_ai_core.py setup`
