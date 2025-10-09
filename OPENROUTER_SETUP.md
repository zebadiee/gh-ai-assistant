# OpenRouter Setup Guide - REQUIRED for Free Models

## ⚠️ CRITICAL: Enable Model Training to Use Free Models

Even if you have credits, OpenRouter's free models (`:free` suffix) **require** you to opt-in to model training.

### 🚀 Quick Fix (Takes 30 seconds)

1. **Go to OpenRouter Privacy Settings:**
   - Visit: https://openrouter.ai/settings/privacy

2. **Enable "Model Training"**
   - Find the "Model Training" toggle
   - Turn it **ON**

3. **Save Settings**

**That's it!** Your free models will now work with the full 1,000 requests/day limit.

---

## 📊 What This Does

### Without "Model Training" Enabled:
- ❌ 10-50 requests/day per model (even with credits!)
- ❌ Constant 429 rate limit errors
- ❌ Can't use `:free` models effectively

### With "Model Training" Enabled:
- ✅ **1,000 requests/day per model**
- ✅ 20 requests/minute per model
- ✅ Full access to all free models
- ✅ Works as intended

---

## 🔒 Privacy Information

- Your data is used **anonymously** for model training
- Not linked to your personal account
- You can disable it anytime (but lose free model access)
- Required by model providers for free tier access

---

## 🧪 Test It's Working

After enabling "Model Training":

```bash
cd gh-ai-assistant
source venv/bin/activate
python gh_ai_core.py chat --no-context
```

Try a few questions - you should no longer get rate limit errors!

---

## 🎯 Complete Setup Checklist

- [ ] Create OpenRouter account: https://openrouter.ai
- [ ] Generate API key: https://openrouter.ai/keys
- [ ] **Enable "Model Training"**: https://openrouter.ai/settings/privacy ⚠️ CRITICAL
- [ ] Optional: Add credits for higher limits: https://openrouter.ai/credits
- [ ] Configure gh-ai-assistant: `python gh_ai_core.py setup`

---

## 📈 Rate Limit Tiers

| Account Status | Model Training | Requests/Day | Requests/Min |
|----------------|----------------|--------------|--------------|
| No Credits | OFF | ~10-50 | 2-5 |
| No Credits | ON | ~10-50 | 2-5 |
| **With Credits** | **OFF** | **~10-50** ⚠️ | **2-5** ⚠️ |
| **With Credits** | **ON** | **1,000** ✅ | **20** ✅ |

**The key takeaway:** Having credits isn't enough - you MUST enable "Model Training"!

---

## 🔍 Verify Your Setup

Check your OpenRouter account status:

1. **Credits**: https://openrouter.ai/credits
   - Should show credit balance

2. **Privacy Settings**: https://openrouter.ai/settings/privacy
   - "Model Training" should be ON

3. **Activity Log**: https://openrouter.ai/activity
   - Shows recent requests and rate limit status

---

## 🆘 Still Getting Rate Limits?

If you've enabled "Model Training" and still have issues:

1. **Wait 5 minutes** - Settings may take a moment to propagate

2. **Check credits** - Ensure you have a positive balance

3. **Try a test request**:
   ```bash
   python gh_ai_core.py ask --no-context "test"
   ```

4. **Check activity log** - See what OpenRouter is reporting

5. **Contact OpenRouter Support** - May be an account issue

---

## 💡 Alternative: Local Models (No Limits Ever)

If you want truly unlimited access with zero rate limits:

```bash
# Install Ollama (free, runs locally)
brew install ollama

# Download a model
ollama pull deepseek-r1:1.5b

# Run it
ollama run deepseek-r1:1.5b
```

Benefits:
- ✅ Unlimited requests
- ✅ No rate limits
- ✅ Complete privacy (stays on your Mac)
- ✅ No internet required
- ✅ Free forever

We can integrate Ollama into gh-ai-assistant for automatic fallback!

---

## 📚 Additional Resources

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Privacy Policy**: https://openrouter.ai/privacy
- **Model Training FAQ**: https://openrouter.ai/docs/features/privacy-and-logging
- **Rate Limits Info**: https://openrouter.ai/docs/limits

---

**Remember:** Enable "Model Training" in Privacy Settings - it's the #1 fix for free model rate limits! 🎯
