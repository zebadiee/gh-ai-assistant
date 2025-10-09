# Architecture Documentation

## System Overview

The GitHub CLI AI Assistant is built as a modular, production-ready system with clear separation of concerns and enterprise-grade features.

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│  (CLI Commands: ask, setup, stats, models)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      AIAssistant                             │
│  • Main orchestration layer                                 │
│  • Credential management                                    │
│  • Response formatting                                      │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌──────────────┐ ┌────────────────────┐
│ TokenManager│ │OpenRouter    │ │GitHub Context      │
│             │ │Client        │ │Extractor           │
│ • Usage     │ │              │ │                    │
│   Tracking  │ │ • API Calls  │ │ • Repo Info        │
│ • Model     │ │ • Rate Limit │ │ • Branch/Commits   │
│   Rotation  │ │   Handling   │ │ • Diff Analysis    │
│ • Analytics │ │ • Error Mgmt │ │ • Context Building │
└──────┬──────┘ └──────┬───────┘ └──────┬─────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌──────────────┐ ┌────────────────────┐
│  SQLite DB  │ │ OpenRouter   │ │  Git Repository    │
│  (Usage)    │ │   API        │ │                    │
└─────────────┘ └──────────────┘ └────────────────────┘
```

## Component Details

### 1. AIAssistant (Main Controller)

**Responsibilities:**
- User interaction management
- Component coordination
- Secure credential handling via system keyring
- Prompt enhancement with context
- Response formatting and error handling

**Key Methods:**
```python
setup_api_key()              # Interactive API key configuration
ask(prompt, use_context)     # Main query interface
show_stats(days)             # Usage analytics display
list_models()                # Available models with usage
```

**Data Flow:**
```
User Query → Load API Key → Get Optimal Model → 
Enhance with Context → API Request → Record Usage → 
Format Response → Return to User
```

### 2. TokenManager (Usage Intelligence)

**Responsibilities:**
- SQLite-based usage tracking
- Automatic model rotation (90% threshold)
- Daily limit management
- Historical analytics
- Cost tracking (for future premium models)

**Key Methods:**
```python
record_usage(model, tokens, cost)      # Log API usage
get_today_usage(model)                 # Current day stats
get_usage_stats(days)                  # Historical analytics
get_optimal_model(task_type)           # Smart model selection
```

**Database Schema:**
```sql
CREATE TABLE usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER NOT NULL,
    request_count INTEGER DEFAULT 1,
    cost REAL DEFAULT 0.0
);
```

**Model Rotation Logic:**
```python
for model in FREE_MODELS:
    requests, tokens = get_today_usage(model['id'])
    if requests < (model['daily_limit'] * 0.9):  # 90% threshold
        return model['id']
```

### 3. OpenRouterClient (API Interface)

**Responsibilities:**
- OpenRouter API communication
- Request/response handling
- Rate limit detection
- Error handling and retries
- Proper API attribution headers

**Key Methods:**
```python
chat_completion(model, messages, max_tokens)  # Main API call
```

**Request Headers:**
```python
{
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://github.com/gh-ai-assistant",
    "X-Title": "GitHub CLI AI Assistant",
    "Content-Type": "application/json"
}
```

**Error Handling:**
- Network timeouts (60s default)
- Rate limiting detection
- Invalid response format handling
- Connection error recovery

### 4. GitHubContextExtractor (Context Intelligence)

**Responsibilities:**
- Repository information extraction
- Branch and commit detection
- Diff analysis for uncommitted changes
- Context-aware prompt building

**Key Methods:**
```python
get_repo_info()           # Extract repo metadata
get_current_changes()     # Analyze uncommitted changes
```

**Context Structure:**
```python
{
    "repo_url": "https://github.com/user/repo.git",
    "branch": "feature-branch",
    "recent_commits": "abc123 Fix bug\ndef456 Add feature",
    "current_changes": "file.py | 10 +++++-----"
}
```

**Prompt Enhancement:**
```python
# System message with context
"You are a helpful GitHub CLI AI assistant. Current context:
Repository: https://github.com/user/repo.git
Branch: main
Recent commits:
abc123 Fix authentication bug
def456 Add new feature

Current changes:
src/main.py | 15 +++++++++------"

# User message
"Review my changes for security issues"
```

## Data Storage

### Configuration Directory
```
~/.gh-ai-assistant/
├── usage.db          # SQLite usage database
└── config.json       # Optional future config
```

### Secure Credential Storage

**macOS (Keychain):**
```
Service: gh-ai-assistant
Account: openrouter_api_key
Access: Current user only
```

**Windows (Credential Manager):**
```
Target: gh-ai-assistant/openrouter_api_key
Type: Generic credential
```

**Linux (Secret Service):**
```
Collection: Default keyring
Schema: gh-ai-assistant
Attribute: openrouter_api_key
```

## Model Selection Strategy

### Free Model Priority

```python
FREE_MODELS = [
    {
        "id": "deepseek/deepseek-r1:free",
        "priority": 1,              # Highest priority
        "daily_limit": 1000,
        "best_for": "code, reasoning, math"
    },
    {
        "id": "deepseek/deepseek-chat:free",
        "priority": 2,              # Secondary
        "daily_limit": 1000,
        "best_for": "general conversation"
    },
    {
        "id": "mistralai/mistral-7b-instruct:free",
        "priority": 3,              # Fallback
        "daily_limit": 1000,
        "best_for": "multilingual"
    }
]
```

### Selection Algorithm

1. **Check Primary Model** (DeepSeek R1)
   - If < 900 requests today → Use it
   
2. **Check Secondary Model** (DeepSeek Chat)
   - If primary exhausted and secondary < 900 → Use it
   
3. **Check Fallback Model** (Mistral 7B)
   - If both exhausted and fallback < 900 → Use it
   
4. **All Exhausted**
   - Use primary (will hit rate limit)
   - User notified of limit
   - Retry after midnight UTC

### Usage Tracking Flow

```
User Request
    ↓
get_optimal_model()  ← Check today's usage for each model
    ↓
Selected Model: deepseek/deepseek-r1:free
    ↓
API Request (via OpenRouterClient)
    ↓
Response with token count
    ↓
record_usage(model="deepseek/deepseek-r1:free", 
             tokens=125, 
             cost=0.0)
    ↓
SQLite INSERT
    ↓
Return Response to User
```

## Security Architecture

### Threat Model

**Protected Against:**
- ✅ API key exposure in files
- ✅ API key in version control
- ✅ Credential theft from disk
- ✅ Man-in-the-middle (HTTPS only)
- ✅ SQL injection (parameterized queries)

**User Responsibilities:**
- API key should remain secret
- Don't share keyring access
- Revoke compromised keys immediately

### Security Layers

1. **Transport Security**
   - HTTPS only (TLS 1.2+)
   - Certificate validation
   - No plaintext transmission

2. **Storage Security**
   - OS-level credential encryption
   - No filesystem storage
   - Access control via OS

3. **Application Security**
   - SQL parameterization
   - Input validation
   - Error sanitization

## Performance Considerations

### Latency Breakdown

```
Total Request Time: ~2-5 seconds

├─ Context Extraction: ~100ms
│  ├─ Git commands: 50-80ms
│  └─ Processing: 20-50ms
│
├─ Model Selection: ~10ms
│  ├─ DB query: 5ms
│  └─ Logic: 5ms
│
├─ API Request: 1-4s
│  ├─ Network: 100-500ms
│  ├─ Model inference: 500-3000ms
│  └─ Response: 100-500ms
│
└─ Usage Recording: ~5ms
   └─ DB insert: 5ms
```

### Optimization Strategies

1. **Database**
   - Indexed queries on model + timestamp
   - Connection pooling (future)
   - Batch inserts for high volume

2. **API Calls**
   - Request timeout: 60s
   - Connection reuse
   - Future: Response caching

3. **Context Extraction**
   - Git command caching (future)
   - Lazy loading
   - Minimal diff size

## Scalability

### Current Limits

- **Single User**: 3,000 requests/day (free models)
- **Database**: Millions of records (SQLite limit)
- **Concurrent Requests**: 1 (synchronous)

### Future Scaling Options

1. **Team Usage**
   - Shared database (PostgreSQL)
   - API key rotation
   - Usage quotas per user

2. **High Volume**
   - Async request handling
   - Response caching
   - Request queuing

3. **Enterprise**
   - Premium model support
   - Custom model endpoints
   - SLA monitoring

## Extension Points

### Adding New Models

```python
# In gh_ai_core.py
FREE_MODELS.append({
    "id": "provider/new-model:free",
    "name": "New Model",
    "daily_limit": 1000,
    "context_window": 32768,
    "best_for": "specific task",
    "cost_per_1k_tokens": 0.0
})
```

### Custom Context Extractors

```python
class CustomContextExtractor(GitHubContextExtractor):
    def get_custom_info(self):
        # Add your custom logic
        return {"custom_field": "value"}
```

### Alternative Storage Backends

```python
class PostgresTokenManager(TokenManager):
    def __init__(self, connection_string):
        # PostgreSQL implementation
        pass
```

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external dependencies
- Database operations
- API client functionality

### Integration Tests
- Component interaction
- API flow testing
- Context extraction
- Error scenarios

### End-to-End Tests
- Full workflow testing
- Real API calls (with test key)
- Performance benchmarks
- Security validation

## Deployment

### Installation Methods

1. **Development Install**
   ```bash
   python setup.py develop
   ```

2. **Production Install**
   ```bash
   python setup.py install
   ```

3. **GitHub CLI Extension**
   ```bash
   gh extension install .
   ```

### Configuration Management

- User-specific: `~/.gh-ai-assistant/`
- System-wide: Not supported (by design)
- Environment: Optional override

## Monitoring & Observability

### Built-in Analytics

```bash
# View usage patterns
python gh_ai_core.py stats --days 30

# Model health
python gh_ai_core.py models

# Database inspection
sqlite3 ~/.gh-ai-assistant/usage.db "SELECT * FROM usage"
```

### Future Enhancements

- Request latency tracking
- Error rate monitoring
- Model performance comparison
- Cost projection

## Maintenance

### Database Maintenance

```bash
# Vacuum (shrink database)
sqlite3 ~/.gh-ai-assistant/usage.db "VACUUM;"

# Archive old data
sqlite3 ~/.gh-ai-assistant/usage.db \
  "DELETE FROM usage WHERE timestamp < date('now', '-90 days');"
```

### API Key Rotation

```bash
# Update to new key
python gh_ai_core.py setup
```

### Upgrades

```bash
# Pull latest code
git pull

# Reinstall
python setup.py develop
```

## Troubleshooting Architecture

### Debug Mode (Future)

```python
# Enable verbose logging
assistant = AIAssistant(debug=True)
```

### Health Checks

```python
# Verify components
def health_check():
    checks = {
        "api_key": bool(load_api_key()),
        "database": db_path.exists(),
        "git_repo": bool(get_repo_info())
    }
    return all(checks.values())
```

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2025  
**Status**: Production Ready 🚀
