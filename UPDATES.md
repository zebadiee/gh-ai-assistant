# Recent Updates

## Version 1.0.1 (2025-01-09)

### 🔧 Bug Fixes

1. **Fixed SQLite Deprecation Warning**
   - Added proper date adapter for Python 3.12+
   - No more warnings when running on modern Python versions

2. **Fixed Model Configuration**
   - Replaced non-working `deepseek/deepseek-chat:free` with working alternatives
   - Added Google Gemini 2.0 Flash Free (1M token context!)
   - Added Meta Llama 3.2 3B Free
   - **Now 4 free models instead of 3**

3. **Improved Rate Limit Handling**
   - Better 429 error detection and messaging
   - Automatic rotation through all available models
   - Clear feedback about which model hit the limit
   - Helpful error messages with next steps

### ✨ New Features

1. **Increased Free Capacity**
   - **4,000 total free requests per day** (was 3,000)
   - 4 different free AI models to choose from
   - Better distribution across model providers

2. **New Documentation**
   - Added comprehensive **TROUBLESHOOTING.md**
   - Covers all common errors and solutions
   - Instructions for finding new free models
   - Privacy and data retention information

### 🤖 Working Free Models

| Model | Daily Limit | Context | Best For |
|-------|-------------|---------|----------|
| DeepSeek R1 Free | 1,000 | 131K | Code, reasoning, math |
| Google Gemini 2.0 Flash Free | 1,000 | 1M | General, fast responses |
| Mistral 7B Instruct Free | 1,000 | 32K | Multilingual, efficiency |
| Meta Llama 3.2 3B Free | 1,000 | 131K | General tasks |

### 📚 Documentation Updates

- **TROUBLESHOOTING.md** - New comprehensive troubleshooting guide
- Updated model lists in all documentation
- Added privacy and data handling information
- Improved error reference guide

### 🔗 Links

- **GitHub**: https://github.com/zebadiee/gh-ai-assistant
- **Latest Release**: https://github.com/zebadiee/gh-ai-assistant/releases
- **Issues**: https://github.com/zebadiee/gh-ai-assistant/issues

### 💡 How to Update

```bash
cd gh-ai-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 🧪 Testing the Updates

```bash
# Check models work
python gh_ai_core.py models

# Test functionality
python gh_ai_core.py ask --no-context "Hello!"

# Verify no warnings
python gh_ai_core.py stats
```

### 🐛 Known Issues

None currently! All reported issues have been fixed.

If you encounter any problems:
1. Check **TROUBLESHOOTING.md**
2. Visit: https://github.com/zebadiee/gh-ai-assistant/issues
3. Check OpenRouter status: https://openrouter.ai/activity

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md)
