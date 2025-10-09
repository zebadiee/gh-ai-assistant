# Troubleshooting Guide

## Common Issues and Solutions

### 429 Rate Limit Errors

**Error Message:**
```
⚠️  Rate limit hit for [model-name]
```

**Causes:**
1. **Daily limit reached** - Free models have 1,000 requests/day per model
2. **Account without credits** - New OpenRouter accounts may have lower limits (50 req/day)
3. **API key rate limiting** - OpenRouter may temporarily throttle requests

**Solutions:**

1. **Check Your OpenRouter Account**
   - Visit: https://openrouter.ai/activity
   - Check your credit balance: https://openrouter.ai/credits
   - New accounts may need to wait for free credits to activate

2. **Use Model Rotation** (Automatic)
   - The tool automatically tries all available free models
   - You have 4 models = 4,000 total free requests per day

3. **Wait for Reset**
   - Rate limits reset at midnight UTC
   - Check current usage: `python gh_ai_core.py models`

4. **Get Free Credits**
   - Some OpenRouter promotions offer free credits
   - Check: https://openrouter.ai/credits

### 404 Not Found Errors

**Error Message:**
```
❌ Error: 404 Client Error: Not Found
```

**Causes:**
- Model ID is incorrect or model has been removed
- OpenRouter changed their free model offerings

**Solution:**
- Check current free models at: https://openrouter.ai/models?free=true
- Update FREE_MODELS in `gh_ai_core.py` if needed

**Current Working Free Models (as of 2025):**
- `deepseek/deepseek-r1:free`
- `google/gemini-2.0-flash-exp:free`
- `mistralai/mistral-7b-instruct:free`
- `meta-llama/llama-3.2-3b-instruct:free`

### SQLite Warnings (Python 3.12+)

**Warning Message:**
```
DeprecationWarning: The default date adapter is deprecated
```

**Solution:**
- This has been fixed in the latest version
- Update your code: `git pull origin main`
- The warning is harmless and doesn't affect functionality

### No API Key Configured

**Error Message:**
```
❌ No API key configured. Run 'setup' first.
```

**Solution:**
```bash
python gh_ai_core.py setup
# Enter your OpenRouter API key when prompted
```

Get a free API key at: https://openrouter.ai/keys

### Import Errors

**Error Message:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Permission Errors

**Error on macOS/Linux:**
```
Permission denied: ./gh-ai
```

**Solution:**
```bash
chmod +x gh-ai
chmod +x gh_ai_core.py
```

### Database Locked

**Error Message:**
```
database is locked
```

**Causes:**
- Multiple instances running simultaneously
- Database file permissions issue

**Solution:**
```bash
# Check for running instances
ps aux | grep gh_ai_core

# Kill any stuck processes
killall python

# If still locked, backup and recreate database
mv ~/.gh-ai-assistant/usage.db ~/.gh-ai-assistant/usage.db.backup
# Database will be recreated on next run
```

## Checking System Status

### Verify Installation

```bash
# Run validation script
python validate.py

# Should show 11/11 tests passing
```

### Check Model Availability

```bash
# See current usage for all models
python gh_ai_core.py models

# Check stats
python gh_ai_core.py stats --days 7
```

### Test API Connection

```bash
# Simple test without context
python gh_ai_core.py ask --no-context "test"

# Test with GitHub context
python gh_ai_core.py ask "Hello"
```

## Finding Working Free Models

OpenRouter's free model offerings change over time. To find current free models:

1. **Visit OpenRouter Models Page**
   - URL: https://openrouter.ai/models
   - Filter by "Free" toggle
   - Look for models with `:free` suffix

2. **Check Model Details**
   - Click on a model to see rate limits
   - Note the model ID (e.g., `mistralai/mistral-7b-instruct:free`)

3. **Update FREE_MODELS List**
   - Edit `gh_ai_core.py`
   - Update the FREE_MODELS list with working model IDs
   - Test with: `python gh_ai_core.py ask "test"`

### Example Model Entry

```python
{
    "id": "provider/model-name:free",
    "name": "Human Readable Name",
    "daily_limit": 1000,
    "context_window": 32768,
    "best_for": "description of use case",
    "cost_per_1k_tokens": 0.0
}
```

## Performance Issues

### Slow Response Times

**Normal Response Times:**
- First request: 3-8 seconds (includes context extraction)
- Subsequent requests: 2-5 seconds

**If Slower:**
1. Check internet connection
2. Try different model: may be slower/faster
3. Use `--no-context` flag to skip Git operations

### High Token Usage

**Check Token Consumption:**
```bash
python gh_ai_core.py stats
```

**Reduce Token Usage:**
1. Use shorter, more specific prompts
2. Use `--no-context` when you don't need repo context
3. Avoid very long conversations

## Getting Help

### Debug Information to Collect

When reporting issues, include:

1. **System Info**
   ```bash
   python --version
   uname -a  # macOS/Linux
   ```

2. **Validation Results**
   ```bash
   python validate.py
   ```

3. **Model Status**
   ```bash
   python gh_ai_core.py models
   ```

4. **Error Messages**
   - Full error output
   - Command that caused the error

### Resources

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **GitHub Issues**: https://github.com/zebadiee/gh-ai-assistant/issues
- **OpenRouter Support**: https://discord.gg/openrouter

### Common Quick Fixes

```bash
# Reset everything
rm -rf ~/.gh-ai-assistant/
python gh_ai_core.py setup

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Check for updates
git pull origin main

# Verify installation
python validate.py
```

## Privacy and Data

### What Data is Stored Locally?

- **API Key**: Encrypted in system keyring (secure)
- **Usage Stats**: SQLite database (`~/.gh-ai-assistant/usage.db`)
- **No Prompts**: Your questions/answers are NOT stored locally

### What Data Goes to OpenRouter?

According to OpenRouter's privacy policy:
- Your prompts and API requests
- Model responses
- Usage metadata

**Privacy Options:**
- Check OpenRouter's data retention policy: https://openrouter.ai/docs/features/privacy-and-logging
- Some models may have different privacy guarantees

### Delete Your Data

```bash
# Remove all local data
rm -rf ~/.gh-ai-assistant/

# Remove from system keyring (macOS)
# Open Keychain Access app → search "gh-ai-assistant" → delete

# Remove from system keyring (command line)
python -c "import keyring; keyring.delete_password('gh-ai-assistant', 'openrouter_api_key')"
```

## Rate Limit Strategy

To maximize free usage:

1. **Spread across models** - 4 models = 4,000 requests/day
2. **Check usage regularly** - `python gh_ai_core.py models`
3. **Plan your queries** - Batch similar questions
4. **Use at optimal times** - After midnight UTC for reset
5. **Monitor stats** - Track which models are available

## Still Having Issues?

If none of these solutions work:

1. **Open an issue**: https://github.com/zebadiee/gh-ai-assistant/issues
2. **Check OpenRouter status**: May be temporary API issues
3. **Try again later**: Rate limits reset daily
4. **Verify API key**: Make sure it's valid and active

---

**Last Updated**: 2025-01-09  
**Version**: 1.0.1
