# Contributing to GitHub CLI AI Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- OpenRouter API key (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/gh-ai-assistant.git
   cd gh-ai-assistant
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python setup.py develop
   ```

4. **Configure for Testing**
   ```bash
   python gh_ai_core.py setup
   # Enter your test API key
   ```

## How to Contribute

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Verify the bug with the latest version
- Collect relevant information (OS, Python version, error messages)

**Bug Report Template:**
```markdown
**Description**: Brief description of the bug

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- OS: macOS/Windows/Linux
- Python Version: 3.x.x
- gh-ai-assistant Version: x.x.x

**Error Messages**: Paste any error messages
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
- Use a clear and descriptive title
- Provide detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include examples if applicable

### Pull Requests

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make Your Changes**
   - Follow the code style (see below)
   - Add tests if applicable
   - Update documentation
   - Keep commits focused and atomic

3. **Test Your Changes**
   ```bash
   # Run tests
   python test_gh_ai.py
   
   # Manual testing
   python gh_ai_core.py ask "Test question"
   python gh_ai_core.py stats
   python gh_ai_core.py models
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Commit message format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/modifications
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues (if any)
   - Screenshots (if UI changes)

## Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

```python
# Imports
import os
import sys
from typing import Dict, List, Optional

# Constants (uppercase)
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 60

# Classes (PascalCase)
class TokenManager:
    """Class docstring"""
    
    def __init__(self):
        self.variable_name = value  # snake_case

# Functions (snake_case)
def get_optimal_model(task_type: str) -> str:
    """
    Function docstring with description.
    
    Args:
        task_type: Type of task to optimize for
        
    Returns:
        Model ID as string
    """
    pass

# Type hints
def process_data(data: Dict[str, Any]) -> List[str]:
    pass
```

### Documentation

- All public functions/classes must have docstrings
- Use type hints for function parameters and returns
- Update README.md for user-facing changes
- Update ARCHITECTURE.md for system changes

### Testing

Add tests for new features:

```python
import unittest

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass
        
    def test_feature_works(self):
        """Test description"""
        result = new_feature()
        self.assertEqual(result, expected_value)
        
    def tearDown(self):
        """Clean up after tests"""
        pass
```

## Project Structure

```
gh-ai-assistant/
├── gh_ai_core.py          # Main application code
├── setup.py               # Package configuration
├── requirements.txt       # Dependencies
├── gh-ai                  # CLI extension entry point
├── test_gh_ai.py         # Test suite
├── README.md              # User documentation
├── QUICKSTART.md          # Quick start guide
├── API_SETUP.md          # API configuration guide
├── ARCHITECTURE.md        # System architecture
├── CONTRIBUTING.md        # This file
├── CHANGELOG.md          # Version history
├── LICENSE               # MIT license
└── .gitignore            # Git ignore patterns
```

## Areas for Contribution

### High Priority
- [ ] Additional test coverage
- [ ] Performance optimizations
- [ ] Error handling improvements
- [ ] Documentation enhancements

### Medium Priority
- [ ] Response caching
- [ ] Async request handling
- [ ] Export functionality
- [ ] Additional context extractors

### Advanced Features
- [ ] Local model support (Ollama)
- [ ] Team collaboration features
- [ ] Web dashboard
- [ ] Plugin system

## Development Workflow

### Adding a New Model

1. **Update FREE_MODELS** in `gh_ai_core.py`:
   ```python
   FREE_MODELS.append({
       "id": "provider/model:free",
       "name": "Model Name",
       "daily_limit": 1000,
       "context_window": 32768,
       "best_for": "use case",
       "cost_per_1k_tokens": 0.0
   })
   ```

2. **Add tests** in `test_gh_ai.py`

3. **Update documentation** (README.md, API_SETUP.md)

4. **Test thoroughly**

### Adding a New Command

1. **Add subparser** in `main()`:
   ```python
   new_parser = subparsers.add_parser("newcmd", help="Description")
   new_parser.add_argument("--option", help="Option help")
   ```

2. **Add handler** in `main()`:
   ```python
   elif args.command == "newcmd":
       assistant.new_command_method()
   ```

3. **Implement method** in `AIAssistant` class

4. **Add tests**

5. **Update documentation**

## Code Review Process

Pull requests will be reviewed for:

1. **Functionality**: Does it work as intended?
2. **Tests**: Are there adequate tests?
3. **Documentation**: Is it properly documented?
4. **Code Quality**: Does it follow style guidelines?
5. **Performance**: Does it introduce bottlenecks?
6. **Security**: Are there security concerns?

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

- [ ] Update version in `setup.py`
- [ ] Update CHANGELOG.md
- [ ] Run all tests
- [ ] Update documentation
- [ ] Create git tag
- [ ] Build and test package
- [ ] Publish to PyPI (if applicable)

## Questions?

- Open an issue for discussion
- Check existing documentation
- Review closed issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🎉
