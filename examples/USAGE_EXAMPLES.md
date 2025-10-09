# Usage Examples

This directory contains practical examples of using the GitHub CLI AI Assistant.

## Basic Examples

### 1. Simple Question

```bash
python gh_ai_core.py ask "What is the difference between a list and a tuple in Python?"
```

**Expected Output:**
```
🤖 Using model: deepseek/deepseek-r1:free

Lists and tuples are both sequence types in Python, but they have key differences:

1. **Mutability**: Lists are mutable (can be changed), tuples are immutable
2. **Syntax**: Lists use [], tuples use ()
3. **Performance**: Tuples are slightly faster
4. **Use cases**: Lists for collections that change, tuples for fixed data

Example:
my_list = [1, 2, 3]  # Can modify
my_list[0] = 10

my_tuple = (1, 2, 3)  # Cannot modify
# my_tuple[0] = 10  # This raises an error
```

### 2. Code Review

```bash
# In a git repository with changes
python gh_ai_core.py ask "Review my uncommitted changes for potential bugs"
```

**Expected Output:**
```
🤖 Using model: deepseek/deepseek-r1:free

Based on your current changes in src/main.py:

1. **Potential Issue**: Line 45 - Missing error handling around file operations
   Recommendation: Add try-except block

2. **Good Practice**: Line 52 - Using context manager for file handling
   
3. **Suggestion**: Line 78 - Consider adding type hints for better clarity

Overall: Code quality is good, just add error handling for production readiness.
```

### 3. Architecture Advice

```bash
python gh_ai_core.py ask "Should I use a singleton or dependency injection for my database connection?"
```

### 4. Usage Statistics

```bash
python gh_ai_core.py stats --days 7
```

**Expected Output:**
```
📊 Usage statistics for last 7 days:

🤖 deepseep/deepseek-r1:free
   Requests: 45
   Tokens: 12,450
   Cost: $0.0000

📈 Totals:
   Total Requests: 45
   Total Tokens: 12,450
   Total Cost: $0.0000
```

### 5. Model Information

```bash
python gh_ai_core.py models
```

**Expected Output:**
```
🤖 Available Free Models:

1. DeepSeek R1 Free
   ID: deepseek/deepseek-r1:free
   Daily Limit: 1000 requests
   Context Window: 131,072 tokens
   Best For: reasoning, math, code
   Today's Usage: 45/1000 (4.5%)

2. DeepSeek Chat Free
   ID: deepseek/deepseek-chat:free
   Daily Limit: 1000 requests
   Context Window: 32,768 tokens
   Best For: general conversation
   Today's Usage: 0/1000 (0.0%)

3. Mistral 7B Free
   ID: mistralai/mistral-7b-instruct:free
   Daily Limit: 1000 requests
   Context Window: 32,768 tokens
   Best For: multilingual, efficiency
   Today's Usage: 0/1000 (0.0%)
```

## Advanced Examples

### 6. Context-Free Questions

```bash
# For general knowledge questions not related to your repository
python gh_ai_core.py ask --no-context "Explain quantum computing in simple terms"
```

### 7. Code Generation

```bash
python gh_ai_core.py ask "Generate a Python function to implement binary search"
```

### 8. Debugging Help

```bash
python gh_ai_core.py ask "Why might I get a 'list index out of range' error in a for loop?"
```

### 9. Git Workflow Integration

```bash
# Generate commit message
git diff --cached | python gh_ai_core.py ask "Suggest a good commit message for these changes"

# Pre-commit review
git diff --cached | python gh_ai_core.py ask "Check these changes for security issues"
```

### 10. Documentation Generation

```bash
python gh_ai_core.py ask "Generate docstrings for the main functions in this file"
```

## GitHub CLI Extension Examples

### Install as Extension

```bash
gh extension install .
```

### Use with gh

```bash
# Simple question
gh ai ask "How do I squash commits in git?"

# Context-aware
gh ai ask "Review this repository structure"

# Statistics
gh ai stats --days 30

# Models
gh ai models
```

## Scripting Examples

### Example 1: Automated Code Review Script

```bash
#!/bin/bash
# review_changes.sh - Review uncommitted changes before commit

if [ -z "$(git diff)" ]; then
    echo "No changes to review"
    exit 0
fi

echo "Reviewing changes..."
python gh_ai_core.py ask "Review my uncommitted changes. List any issues found."

read -p "Continue with commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit
fi
```

### Example 2: Daily Usage Report

```bash
#!/bin/bash
# daily_report.sh - Check daily AI usage

echo "=== Daily AI Assistant Report ==="
echo ""
python gh_ai_core.py models
echo ""
echo "=== Last 7 Days Usage ==="
python gh_ai_core.py stats --days 7
```

### Example 3: Batch Questions

```bash
#!/bin/bash
# batch_questions.sh - Ask multiple questions

questions=(
    "What are Python best practices for error handling?"
    "How do I optimize database queries?"
    "Explain the SOLID principles"
)

for q in "${questions[@]}"; do
    echo "Q: $q"
    python gh_ai_core.py ask --no-context "$q"
    echo "---"
done
```

## Integration Examples

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running AI code review..."
python gh_ai_core.py ask "Quick review: any obvious issues in these changes?" > /tmp/ai_review.txt

if grep -i "error\|warning\|issue" /tmp/ai_review.txt; then
    cat /tmp/ai_review.txt
    read -p "Issues found. Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### CI/CD Integration

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install gh-ai-assistant
        run: |
          pip install -r requirements.txt
          python setup.py install
          
      - name: Configure API Key
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          echo "$OPENROUTER_API_KEY" | python gh_ai_core.py setup
          
      - name: Review Changes
        run: |
          python gh_ai_core.py ask "Review this PR for issues"
```

## Performance Examples

### Measuring Response Time

```bash
time python gh_ai_core.py ask "Quick test question"
```

### Analyzing Token Usage

```python
# analyze_usage.py
import sqlite3
from pathlib import Path

db_path = Path.home() / ".gh-ai-assistant" / "usage.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Average tokens per request
cursor.execute("""
    SELECT model, 
           AVG(tokens_used) as avg_tokens,
           MIN(tokens_used) as min_tokens,
           MAX(tokens_used) as max_tokens
    FROM usage
    GROUP BY model
""")

for row in cursor.fetchall():
    print(f"Model: {row[0]}")
    print(f"  Avg: {row[1]:.0f} tokens")
    print(f"  Min: {row[2]} tokens")
    print(f"  Max: {row[3]} tokens")
    print()

conn.close()
```

## Troubleshooting Examples

### Test API Connection

```bash
python gh_ai_core.py ask "Hello" --no-context
```

### Check Configuration

```bash
# Verify API key is set
python -c "import keyring; print('API Key set:', bool(keyring.get_password('gh-ai-assistant', 'openrouter_api_key')))"

# Verify database
ls -lh ~/.gh-ai-assistant/usage.db

# Check database contents
sqlite3 ~/.gh-ai-assistant/usage.db "SELECT COUNT(*) FROM usage"
```

### Reset Everything

```bash
# Remove configuration
rm -rf ~/.gh-ai-assistant/

# Reconfigure
python gh_ai_core.py setup
```

---

## Tips for Best Results

1. **Be Specific**: "Review this function for memory leaks" vs "Review this"
2. **Use Context**: Let it see your repository for better answers
3. **Monitor Usage**: Check `stats` regularly to avoid hitting limits
4. **Rotate Models**: System auto-rotates, but you can manually select if needed
5. **Save Responses**: Redirect output to files for reference

---

More examples at: https://github.com/yourusername/gh-ai-assistant/wiki
