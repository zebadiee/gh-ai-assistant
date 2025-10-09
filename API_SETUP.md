# API Configuration Guide

## OpenRouter Setup

### 1. Create Account

1. Visit https://openrouter.ai/
2. Click "Sign In" (top right)
3. Choose sign-in method:
   - Google
   - GitHub
   - Discord
   - Email

### 2. Get API Key

1. Once signed in, go to https://openrouter.ai/keys
2. Click "Create Key"
3. Give it a name (e.g., "GitHub AI Assistant")
4. Copy the generated key (starts with `sk-or-v1-...`)
5. **Save it securely** - you can't view it again!

### 3. Configure gh-ai-assistant

```bash
python gh_ai_core.py setup
```

When prompted, paste your API key.

### 4. Verify Setup

```bash
# Test connection
python gh_ai_core.py models
```

You should see a list of available models with usage stats.

## Free Credits

### What You Get (Free Tier)

OpenRouter provides **FREE access** to several models:

| Model | Requests/Day | Context Window |
|-------|--------------|----------------|
| DeepSeek R1 | 1000 | 131,072 tokens |
| DeepSeek Chat | 1000 | 32,768 tokens |
| Mistral 7B | 1000 | 32,768 tokens |

**Total: 3,000 free requests per day** 🎉

### Credits System

- **With Credits**: 1000 requests/day per model
- **Without Credits**: 50 requests/day per model

To get credits:
1. Go to https://openrouter.ai/credits
2. You may receive free credits on signup
3. Additional credits can be purchased if needed

**Note**: This tool prioritizes free models, so you can use it extensively without credits!

## Security

### How API Keys Are Stored

The `gh-ai-assistant` uses your system's secure credential storage:

- **macOS**: Keychain Access
- **Windows**: Windows Credential Manager  
- **Linux**: Secret Service (GNOME Keyring, KWallet, etc.)

### Your API key is:
- ✅ Never stored in plain text files
- ✅ Never committed to git
- ✅ Never sent anywhere except OpenRouter API
- ✅ Encrypted by your operating system

### Viewing/Changing API Key

```bash
# Update API key
python gh_ai_core.py setup

# On macOS, view in Keychain Access:
# Application: Keychain Access → Search "gh-ai-assistant"
```

### Revoking API Key

If your key is compromised:

1. Go to https://openrouter.ai/keys
2. Delete the compromised key
3. Create a new key
4. Run `python gh_ai_core.py setup` with new key

## Rate Limits

### Understanding Limits

Each free model has a daily limit:
- **1000 requests/day** (with credits)
- **50 requests/day** (without credits)

The assistant automatically tracks usage and rotates between models.

### Checking Your Usage

```bash
# See today's usage
python gh_ai_core.py models

# See historical usage
python gh_ai_core.py stats --days 7
```

### What Happens at Limit?

When a model approaches its limit (90% threshold):
1. System automatically switches to next available model
2. You get a notification: "🤖 Using model: [new-model]"
3. No interruption to your workflow

### Maximizing Free Usage

**Best Practices:**

1. **Use all three models**: 3,000 total requests/day
2. **Ask specific questions**: More efficient than vague queries
3. **Monitor usage**: Run `stats` command periodically
4. **Batch similar questions**: Reuse context when possible

## Multiple API Keys (Advanced)

### Team Usage

For team environments, each member should:

1. Get their own OpenRouter API key
2. Run `python gh_ai_core.py setup` on their machine
3. Configure independently

### Switching Between Keys

```bash
# Reconfigure with different key
python gh_ai_core.py setup
```

## Troubleshooting

### "Invalid API Key"

```bash
# Verify key format (should start with sk-or-v1-)
python gh_ai_core.py setup

# Test with models command
python gh_ai_core.py models
```

### "Rate Limit Exceeded"

```bash
# Check usage
python gh_ai_core.py models

# Wait for daily reset (midnight UTC)
# Or system will auto-rotate to next model
```

### "No API Key Found"

```bash
# Reconfigure
python gh_ai_core.py setup
```

### Permission Errors (Linux)

```bash
# Install system keyring
sudo apt-get install gnome-keyring  # Ubuntu/Debian
# or
sudo dnf install gnome-keyring      # Fedora

# Or use KWallet on KDE
sudo apt-get install kwalletmanager
```

## Environment Variables (Not Recommended)

While the tool uses secure keyring storage, you *can* use environment variables for testing:

```bash
export OPENROUTER_API_KEY="your-key-here"
```

**Warning**: This is less secure and not recommended for production use.

## API Costs (Premium Models)

While this tool focuses on **free models**, OpenRouter also offers premium models:

- GPT-4: ~$0.03-0.06 per 1K tokens
- Claude: ~$0.008-0.024 per 1K tokens
- Gemini Pro: ~$0.00025 per 1K tokens

To use premium models, you'd need to:
1. Add credits to your OpenRouter account
2. Modify `FREE_MODELS` in `gh_ai_core.py`

**Current setup**: Zero cost, free models only! 💰

## Support

### OpenRouter Support
- Documentation: https://openrouter.ai/docs
- Discord: https://discord.gg/openrouter
- Email: help@openrouter.ai

### Tool Issues
- Check README.md troubleshooting section
- Review test_gh_ai.py for examples
- Open issue on GitHub repository

---

**Ready to start!** Run: `python gh_ai_core.py setup`
