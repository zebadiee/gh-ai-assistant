# Ollama Local AI Setup Guide

## 🏠 Unlimited Local AI - Zero Rate Limits!

Your gh-ai-assistant now supports **Ollama** for unlimited local AI with automatic cloud fallback!

## ✅ What You Already Have

Your Ollama installation is ready with these models:

| Model | Size | Best For |
|-------|------|----------|
| llama3.2:latest | 2.0 GB | General tasks, fast |
| llama3:latest | 4.7 GB | Advanced reasoning |
| deepseek-coder:6.7b | 3.8 GB | Code generation |
| gemma:2b | 1.7 GB | Lightweight, fast |
| gemma:7b | 5.0 GB | Better quality |

**You're ready to use local AI right now!** 🎉

## 🚀 How It Works

The assistant now uses a **smart fallback system**:

```
User Question
    ↓
Try OpenRouter (Cloud) ☁️
    ↓ (if rate limited)
Try Ollama (Local) 🏠
    ↓
Get Answer! ✅
```

### Automatic Behavior:
1. **Tries cloud first** - Fast, uses OpenRouter free tier
2. **Falls back to local** - When cloud hits rate limits
3. **Seamless experience** - You don't have to do anything!

## 💡 Recommended: Add DeepSeek R1

For best code/reasoning results, add this model:

```bash
# Download DeepSeek R1 (smaller, optimized version)
ollama pull deepseek-r1:1.5b

# Or the full version (larger, better)
ollama pull deepseek-r1:latest
```

This model is specifically optimized for:
- Code generation and review
- Technical reasoning
- Math and logic problems

## 🧪 Test Local Models

```bash
# Test Ollama directly
ollama run llama3.2 "What is 2+2?"

# Test through gh-ai-assistant (will use local if cloud is limited)
python gh_ai_core.py chat --no-context
```

## 📊 Benefits Breakdown

### Cloud Models (OpenRouter):
- ✅ Fast responses
- ✅ Latest models
- ✅ 4,000 requests/day (with proper settings)
- ⚠️ Requires internet
- ⚠️ Rate limits exist

### Local Models (Ollama):
- ✅ **UNLIMITED** requests (no rate limits!)
- ✅ Works offline
- ✅ 100% private (stays on your Mac)
- ✅ Free forever
- ⚠️ Uses your Mac's resources
- ⚠️ Slightly slower than cloud

### Both Together:
- ✅ Best of both worlds!
- ✅ Automatic failover
- ✅ Never stuck without AI
- ✅ Maximum availability

## 🎯 Usage Examples

### Interactive Chat (Auto-fallback)
```bash
python gh_ai_core.py chat --no-context
```

The assistant will:
1. Try cloud models first
2. Show: `☁️  Using cloud model: deepseek/deepseek-r1:free`
3. If rate limited, show: `🏠 Using local model: llama3.2`
4. You get your answer either way!

### Single Questions
```bash
# Auto-fallback works here too
python gh_ai_core.py ask "Explain Python decorators"
```

### Check What's Available
```bash
# See both cloud and local models
python gh_ai_core.py models
```

## 🔧 Ollama Management

### Check Running Models
```bash
ollama list
```

### Download New Models
```bash
# Recommended for coding
ollama pull deepseek-r1:1.5b

# Good all-around model
ollama pull llama3.2

# Lightweight and fast
ollama pull gemma:2b
```

### Remove Unused Models
```bash
ollama rm <model-name>
```

### Check Ollama Status
```bash
# See if Ollama is running
ollama ps

# View logs
ollama logs
```

## 🎨 Model Indicators

The assistant shows you which type of model is being used:

- `☁️  Using cloud model: ...` - OpenRouter API
- `🏠 Using local model: ...` - Ollama local model

## 📈 Performance Tips

### For Faster Local Responses:
1. Use smaller models (llama3.2, gemma:2b)
2. Close other heavy apps
3. M-series Macs perform better with Ollama

### For Better Quality:
1. Use larger models (llama3, gemma:7b)
2. Use cloud models when available
3. DeepSeek models excel at code/reasoning

## 🔍 Troubleshooting

### "Ollama not available"
```bash
# Start Ollama service
ollama serve

# Or in background
ollama serve &
```

### "No local models available"
```bash
# Download at least one model
ollama pull llama3.2
```

### Ollama Not Installed?
```bash
# Install via Homebrew
brew install ollama

# Download a model
ollama pull llama3.2

# Start service
ollama serve
```

## 💰 Cost Comparison

| Solution | Cost | Rate Limits | Privacy |
|----------|------|-------------|---------|
| **OpenRouter Only** | Free | 4K/day | Cloud |
| **Ollama Only** | Free | Unlimited | Local |
| **Both (Current Setup)** | Free | Unlimited* | Hybrid |

*Effectively unlimited with automatic fallback!

## 🎯 Best Practices

1. **Let Auto-Fallback Work**
   - Don't worry about which model is used
   - System picks the best available option

2. **Keep Ollama Running**
   ```bash
   ollama serve &
   ```

3. **Download Recommended Models**
   ```bash
   ollama pull deepseek-r1:1.5b
   ollama pull llama3.2
   ```

4. **Monitor Usage**
   ```bash
   python gh_ai_core.py stats
   ```
   See both cloud and local usage!

## 🔄 Switching Between Modes

The system automatically handles fallback, but you can also:

### Force Cloud Only
(Future feature - not implemented yet)

### Force Local Only  
(Future feature - not implemented yet)

### Current: Automatic (Recommended)
- Tries cloud first (fast)
- Falls back to local (reliable)
- Best user experience!

## 📚 Model Recommendations

### For Coding:
- ✅ deepseek-coder:6.7b (you have this!)
- ✅ deepseek-r1:1.5b (download recommended)
- ✅ Cloud: deepseek/deepseek-r1:free

### For General Chat:
- ✅ llama3.2 (you have this!)
- ✅ gemma:2b (you have this!)
- ✅ Cloud: google/gemini-2.0-flash-exp:free

### For Reasoning:
- ✅ llama3:latest (you have this!)
- ✅ deepseek-r1 (download recommended)
- ✅ Cloud: deepseek/deepseek-r1:free

## 🎊 You're All Set!

With Ollama integration, you now have:
- ✅ Cloud models (fast, 4K/day)
- ✅ Local models (unlimited, private)
- ✅ Automatic fallback
- ✅ Never stuck without AI!

**Start using it:**
```bash
python gh_ai_core.py chat
```

Watch it seamlessly switch between cloud and local models! 🚀

---

**Questions?** Check the main README.md or run `python gh_ai_core.py --help`
