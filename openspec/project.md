# Project Context

## Purpose
Provide a GitHub CLI extension that delivers an AI assistant with intelligent token management, automated model rotation, and repository-aware responses for developers working from the terminal.

## Tech Stack
- Python 3.10+
- GitHub CLI extension framework (`gh`)
- Core libraries: `requests`, `aiohttp`, `tiktoken`, `keyring`, `sqlite3`, `unittest`

## Project Conventions

### Code Style
Follow PEP 8 styling with descriptive names, dataclasses for structured state, and inline docstrings for public entry points. Keep modules focused on one responsibility and encapsulate external I/O behind helper classes.

### Architecture Patterns
Layered services with clear separation of concerns:
- `AIAssistant` orchestrates CLI flows and coordinates collaborators.
- `TokenManager`, `TokenOptimizer`, and related classes persist usage analytics in SQLite and enforce rotation policies.
- `OpenRouterClient` wraps HTTP calls with retry, attribution headers, and error handling.
- `GitHubContextExtractor` gathers repo metadata to enrich prompts.
Shared utilities live at module top-level; persistent data is stored under `~/.gh-ai-assistant/`.

### Testing Strategy
Unit tests rely on Python's `unittest` framework (`test_gh_ai.py`, `test_memory_transfer.py`). Prefer temp directories or mocks for filesystem/network access. Run suites with `python -m unittest discover` before shipping significant changes.

### Git Workflow
Feature work happens on topic branches branched from `main`. Use descriptive commit messages that explain the behavior change. Submit pull requests for review before merging back to `main`.

## Domain Context
Primary value comes from conserving OpenRouter token allotments while keeping responses accurate. The CLI must feel native to GitHub workflows, automatically understand repository state, and respect user credentials stored in the OS keyring.

## Important Constraints
- No plaintext API keys on disk—always rely on system keyring helpers.
- Maintain compatibility with OpenRouter free-tier limits and model IDs.
- Preserve cross-platform support (macOS, Windows, Linux) for filesystem paths and keyring usage.
- SQLite databases live in user config directory and should handle concurrent access safely.

## External Dependencies
- OpenRouter API for model access and token accounting.
- GitHub CLI (`gh`) for extension lifecycle commands.
- System keyring services (macOS Keychain, Windows Credential Manager, Linux Secret Service).
- Local SQLite database files under `~/.gh-ai-assistant/`.
