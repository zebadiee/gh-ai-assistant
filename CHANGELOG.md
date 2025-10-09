# Changelog

All notable changes to the GitHub CLI AI Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-XX

### Added - Intelligent Model Monitoring & Dynamic Selection 🎯
- **Real-time performance monitoring** for all OpenRouter models
- **Smart model ranking** system based on success rate, latency, and availability
- **Automatic model selection** - always uses the most reliable, least congested model
- **Dynamic fallback sequencing** - seamlessly rotates through models when failures occur
- **Performance tracking database** - SQLite-based monitoring of all API requests
- **New CLI commands**:
  - `rankings` - Show real-time model performance rankings
  - `recommend` - Get best model recommendation based on current conditions
- **Interactive chat enhancements** - In-chat access to rankings and recommendations
- **Usage score calculation** - Models scored 0-100 based on error rate, failures, latency, and usage
- **Comprehensive documentation** - New MODEL_MONITORING.md guide
- **Demo script** - `demo_model_monitoring.py` to showcase the system
- **CLI wrapper** - `monitor.sh` for quick access to monitoring commands

### Changed
- Enhanced `ask()` method to use smart model selector
- Improved error handling with automatic model rotation on failures
- Better logging of model performance and selection decisions
- Updated README.md with monitoring features

### Technical Details
- New `model_monitor.py` module with `ModelMonitor` and `SmartModelSelector` classes
- Performance tracking: success/failure rates, latency, consecutive failures
- Scoring algorithm: Error Rate (40%) + Failures (30%) + Latency (20%) + Usage (10%)
- Automatic exclusion of models with 3+ consecutive failures
- Cache-based optimization for reduced database overhead

### Benefits
- ⚡ Higher success rates by avoiding congested models
- 🚀 Lower latency through smart model prioritization  
- 💡 Intelligent resource distribution across multiple models
- 🔄 Automatic recovery when models become available again
- 📊 Data-driven selection based on real performance metrics

## [1.0.0] - 2025-01-09

### Added
- Initial production release
- Core AI assistant with OpenRouter integration
- Intelligent token management with automatic model rotation
- SQLite-based usage tracking and analytics
- Secure API key storage via system keyring
- GitHub context extraction for repository-aware responses
- Three free models with 3,000 total daily requests
- Command-line interface with `ask`, `setup`, `stats`, and `models` commands
- GitHub CLI extension support
- Comprehensive documentation (README, QUICKSTART, API_SETUP, ARCHITECTURE)
- Unit test suite
- MIT license
- Python package setup with setuptools

### Free Models Included
- DeepSeek R1 Free (1000 requests/day, 131K context)
- DeepSeek Chat Free (1000 requests/day, 32K context)
- Mistral 7B Instruct Free (1000 requests/day, 32K context)

### Security Features
- No plaintext API keys stored
- OS-level credential encryption (Keychain/Credential Manager/Secret Service)
- HTTPS-only communication
- SQL injection protection via parameterized queries

### Performance
- Sub-100ms context extraction
- Sub-10ms model selection
- 2-5 second average response time
- Efficient SQLite storage with indexing

## [Unreleased]

### Planned Features
- [ ] Response caching for improved performance
- [ ] Async request handling for concurrent queries
- [ ] PostgreSQL backend option for team usage
- [ ] Debug mode with verbose logging
- [ ] Cost projection and budget alerts
- [ ] Custom model configuration
- [ ] Export usage data to CSV/JSON
- [ ] Integration with git hooks
- [ ] Interactive mode for conversations
- [ ] Local model support (Ollama integration)

### Under Consideration
- Plugin system for custom context extractors
- Multi-language support for CLI
- Web dashboard for usage analytics
- Team collaboration features
- Premium model support
- Request retry logic
- Response streaming for long outputs

---

## Version History

- **1.0.0** (2025-01-09): Initial production release
