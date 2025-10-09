# 🔑 API Key Setup Guide - BYOK (Bring Your Own Key)

## Quick Start

```bash
# Interactive setup wizard (recommended)
python api_keys.py

# Quick setup for OpenRouter
python api_keys.py quick openrouter

# Quick setup for specific provider
python api_keys.py quick groq
python api_keys.py quick openai
```

## Supported Providers

### 1. OpenRouter (Recommended) ⭐

**Why:** Access to 51+ free models through one API key

- **Signup:** https://openrouter.ai/keys
- **Free Tier:** Many free models (DeepSeek, Gemini, Llama, etc.)
- **Key Format:** `sk-or-...`

**Quick Setup:**
```bash
python api_keys.py quick openrouter
```

**What you get:**
- 51+ free models
- Auto-fallback between providers
- Usage tracking
- Access to GPT-4, Claude, Gemini (paid)

### 2. Groq (Ultra-Fast)

**Why:** Fastest inference (500+ tokens/sec)

- **Signup:** https://console.groq.com/keys
- **Free Tier:** 14,400 requests/day
- **Key Format:** `gsk_...`

**Quick Setup:**
```bash
python api_keys.py quick groq
```

**What you get:**
- Llama 3, Mixtral models
- Ultra-low latency
- Generous free tier

### 3. Hugging Face (Open Source)

**Why:** Thousands of open models

- **Signup:** https://huggingface.co/settings/tokens
- **Free Tier:** Free inference API
- **Key Format:** `hf_...`

**Quick Setup:**
```bash
python api_keys.py quick huggingface
```

**What you get:**
- Access to open source models
- Community models
- Free hosting

### 4. OpenAI (Premium)

**Why:** GPT-4, GPT-3.5 Turbo

- **Signup:** https://platform.openai.com/api-keys
- **Free Tier:** $5 trial credits
- **Key Format:** `sk-...`

**Quick Setup:**
```bash
python api_keys.py quick openai
```

**What you get:**
- GPT-4 Turbo
- GPT-3.5
- Function calling
- High quality

### 5. Anthropic (Claude)

**Why:** Best reasoning, long context (200k tokens)

- **Signup:** https://console.anthropic.com/account/keys
- **Free Tier:** Trial credits
- **Key Format:** `sk-ant-...`

**Quick Setup:**
```bash
python api_keys.py quick anthropic
```

**What you get:**
- Claude 3 Opus/Sonnet/Haiku
- Constitutional AI
- Excellent coding

### 6. Together AI

**Why:** Fast open source models

- **Signup:** https://api.together.xyz/settings/api-keys
- **Free Tier:** Trial credits
- **Key Format:** Various

**Quick Setup:**
```bash
python api_keys.py quick together
```

**What you get:**
- 50+ open source models
- Fast inference
- Fine-tuning support

### 7. Replicate

**Why:** Easy ML model deployment

- **Signup:** https://replicate.com/account/api-tokens
- **Free Tier:** Trial credits
- **Key Format:** `r8_...`

**Quick Setup:**
```bash
python api_keys.py quick replicate
```

**What you get:**
- Image, video, audio models
- Version control
- No GPU setup

### 8. Perplexity AI

**Why:** Search-augmented AI

- **Signup:** https://www.perplexity.ai/settings/api
- **Free Tier:** Limited
- **Key Format:** `pplx-...`

**Quick Setup:**
```bash
python api_keys.py quick perplexity
```

**What you get:**
- Real-time web search
- Citations
- Up-to-date information

## Interactive Wizard Features

Run `python api_keys.py` for full wizard with:

1. **Add New API Key**
   - Browse all providers
   - View detailed info
   - Open signup page automatically
   - Validate key format
   - Save securely

2. **View Provider Information**
   - Detailed descriptions
   - Benefits list
   - Step-by-step instructions
   - Links to signup and docs

3. **List Configured Providers**
   - See which keys you have
   - Status overview
   - Free tier info

4. **Remove API Key**
   - Safely delete keys
   - Confirmation prompts

5. **Test API Keys**
   - Format validation
   - Quick health check

6. **Open Signup Pages**
   - Open all provider pages
   - Sign up for multiple at once

## Recommended Setup

For best experience, set up these providers in order:

1. **OpenRouter** (51+ free models, one key)
2. **Groq** (ultra-fast, generous free tier)
3. **Hugging Face** (open source models)
4. **OpenAI** (premium quality, $5 trial)

With these 4 providers, you'll have:
- 51+ free models (OpenRouter)
- Ultra-fast responses (Groq)
- Open source flexibility (Hugging Face)
- Premium quality when needed (OpenAI)

## Security

All API keys are stored securely using:
- **System keyring** (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- **Never** stored in plain text
- **Never** committed to git
- **Local only** - no cloud sync

Keys are stored with service name: `gh-ai-assistant`

## Manual Setup (Advanced)

If you prefer manual setup:

```python
from api_keys import APIKeyManager

manager = APIKeyManager()

# Save key
manager.save_key("openrouter", "sk-or-your-key-here")

# Get key
key = manager.get_key("openrouter")

# Delete key
manager.delete_key("openrouter")

# List configured
providers = manager.list_configured_providers()
```

## Troubleshooting

### Key not saving?

Try running with sudo or check keyring access:
```bash
pip install --upgrade keyring
python -c "import keyring; print(keyring.get_keyring())"
```

### Wrong key format?

Each provider has specific format:
- OpenRouter: `sk-or-...`
- OpenAI: `sk-...`
- Groq: `gsk_...`
- Hugging Face: `hf_...`
- Anthropic: `sk-ant-...`

### Can't access provider?

Check:
1. Key is valid (not revoked)
2. Account has credits/free tier active
3. Correct permissions set
4. No rate limits exceeded

## Usage After Setup

Once keys are configured, the assistant automatically uses them:

```bash
# Chat mode (uses configured providers)
python gh_ai_core.py chat

# Ask question (auto-selects best provider)
python gh_ai_core.py ask "What are the best practices?"

# Rankings (shows all available models)
python gh_ai_core.py rankings
```

The system will:
1. Try OpenRouter free models first
2. Fall back to other configured providers
3. Use local Ollama if all providers exhausted
4. Track usage and optimize automatically

## Cost Optimization

**Free-First Strategy:**
1. OpenRouter free models (51+ options)
2. Groq free tier (14,400/day)
3. Hugging Face inference (unlimited)
4. Local Ollama (unlimited, offline)

**Paid Providers (when needed):**
5. OpenAI GPT-4 (premium quality)
6. Anthropic Claude (long context)
7. Others as needed

The system automatically uses free tiers first and only uses paid APIs when explicitly requested or when free tiers are exhausted.

## Advanced: Environment Variables

You can also use environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENROUTER_API_KEY="sk-or-..."
export GROQ_API_KEY="gsk_..."
export OPENAI_API_KEY="sk-..."
```

The assistant will check both keyring and environment variables.

## Next Steps

1. Run `python api_keys.py` to start setup
2. Add OpenRouter key (recommended first)
3. Test with `python gh_ai_core.py ask "test"`
4. Add more providers as needed
5. Enjoy 51+ free models!

---

**Need help?** Open an issue on GitHub or check the documentation.
