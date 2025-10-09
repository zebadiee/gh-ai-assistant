#!/usr/bin/env python3
"""
GitHub CLI AI Assistant Core Module
Production-ready AI assistant with intelligent token management and free model optimization.
"""

import os
import sys
import json
import sqlite3
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess
import keyring
import requests
from pathlib import Path

# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
DB_PATH = CONFIG_DIR / "usage.db"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYRING_SERVICE = "gh-ai-assistant"

# Free model prioritization based on OpenRouter
FREE_MODELS = [
    {
        "id": "deepseek/deepseek-r1:free",
        "name": "DeepSeek R1 Free",
        "daily_limit": 1000,
        "context_window": 131072,
        "best_for": "reasoning, math, code",
        "cost_per_1k_tokens": 0.0
    },
    {
        "id": "deepseek/deepseek-chat:free",
        "name": "DeepSeek Chat Free",
        "daily_limit": 1000,
        "context_window": 32768,
        "best_for": "general conversation",
        "cost_per_1k_tokens": 0.0
    },
    {
        "id": "mistralai/mistral-7b-instruct:free",
        "name": "Mistral 7B Free",
        "daily_limit": 1000,
        "context_window": 32768,
        "best_for": "multilingual, efficiency",
        "cost_per_1k_tokens": 0.0
    }
]


@dataclass
class UsageRecord:
    """Track API usage for a specific model"""
    model: str
    timestamp: datetime
    tokens_used: int
    request_count: int
    cost: float


class TokenManager:
    """Intelligent token management with auto-rotation and usage tracking"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_config_dir()
        self._init_database()
        
    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    def _init_database(self):
        """Initialize SQLite database for usage tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER NOT NULL,
                request_count INTEGER DEFAULT 1,
                cost REAL DEFAULT 0.0
            )
        ''')
        conn.commit()
        conn.close()
        
    def record_usage(self, model: str, tokens_used: int, cost: float = 0.0):
        """Record API usage in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usage (model, tokens_used, cost)
            VALUES (?, ?, ?)
        ''', (model, tokens_used, cost))
        conn.commit()
        conn.close()
        
    def get_today_usage(self, model: str) -> Tuple[int, int]:
        """Get today's usage for a specific model (requests, tokens)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(tokens_used), 0)
            FROM usage
            WHERE model = ? AND DATE(timestamp) = ?
        ''', (model, today))
        result = cursor.fetchone()
        conn.close()
        return (result[0] or 0, result[1] or 0)
        
    def get_usage_stats(self, days: int = 7) -> Dict[str, Dict]:
        """Get usage statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT model, 
                   COUNT(*) as request_count,
                   SUM(tokens_used) as total_tokens,
                   SUM(cost) as total_cost
            FROM usage
            WHERE timestamp >= ?
            GROUP BY model
        ''', (cutoff_date,))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'requests': row[1],
                'tokens': row[2],
                'cost': row[3]
            }
        
        conn.close()
        return stats
        
    def get_optimal_model(self, task_type: str = "general") -> str:
        """Select optimal free model based on current usage"""
        for model in FREE_MODELS:
            model_id = model['id']
            requests, tokens = self.get_today_usage(model_id)
            
            # Check if we're under 90% of daily limit
            if requests < (model['daily_limit'] * 0.9):
                return model_id
                
        # If all models are near limit, return the first one (will handle rate limiting)
        return FREE_MODELS[0]['id']


class OpenRouterClient:
    """OpenRouter API client with free model support"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/gh-ai-assistant",
            "X-Title": "GitHub CLI AI Assistant",
            "Content-Type": "application/json"
        }
        
    def chat_completion(self, model: str, messages: List[Dict], 
                       max_tokens: int = 2048) -> Dict:
        """Send chat completion request to OpenRouter"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


class GitHubContextExtractor:
    """Extract context from GitHub repository and current state"""
    
    @staticmethod
    def get_repo_info() -> Dict:
        """Get current repository information"""
        try:
            # Get repo name
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True, text=True, check=True
            )
            repo_url = result.stdout.strip()
            
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            branch = result.stdout.strip()
            
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "-5", "--oneline"],
                capture_output=True, text=True, check=True
            )
            recent_commits = result.stdout.strip()
            
            return {
                "repo_url": repo_url,
                "branch": branch,
                "recent_commits": recent_commits
            }
        except subprocess.CalledProcessError:
            return {}
            
    @staticmethod
    def get_current_changes() -> str:
        """Get current uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""


class AIAssistant:
    """Main AI Assistant with intelligent model routing"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.api_key = self._load_api_key()
        self.client = OpenRouterClient(self.api_key) if self.api_key else None
        self.github_context = GitHubContextExtractor()
        
    def _load_api_key(self) -> Optional[str]:
        """Load API key from system keyring"""
        return keyring.get_password(KEYRING_SERVICE, "openrouter_api_key")
        
    def _save_api_key(self, api_key: str):
        """Save API key to system keyring"""
        keyring.set_password(KEYRING_SERVICE, "openrouter_api_key", api_key)
        
    def setup_api_key(self):
        """Interactive API key setup"""
        print("🔐 GitHub CLI AI Assistant Setup")
        print("\nTo use this assistant, you need an OpenRouter API key.")
        print("Get your free API key at: https://openrouter.ai/keys")
        print("\nOpenRouter provides FREE access to:")
        for model in FREE_MODELS:
            print(f"  • {model['name']} ({model['daily_limit']} requests/day)")
        
        api_key = input("\nEnter your OpenRouter API key: ").strip()
        
        if api_key:
            self._save_api_key(api_key)
            self.api_key = api_key
            self.client = OpenRouterClient(api_key)
            print("\n✅ API key saved successfully!")
        else:
            print("\n❌ No API key provided.")
            
    def enhance_prompt_with_context(self, user_prompt: str) -> List[Dict]:
        """Enhance user prompt with GitHub repository context"""
        messages = []
        
        # Add system message with context
        repo_info = self.github_context.get_repo_info()
        changes = self.github_context.get_current_changes()
        
        context_parts = []
        if repo_info:
            context_parts.append(f"Repository: {repo_info.get('repo_url', 'N/A')}")
            context_parts.append(f"Branch: {repo_info.get('branch', 'N/A')}")
            if repo_info.get('recent_commits'):
                context_parts.append(f"Recent commits:\n{repo_info['recent_commits']}")
                
        if changes:
            context_parts.append(f"Current changes:\n{changes}")
            
        if context_parts:
            system_message = "You are a helpful GitHub CLI AI assistant. " + \
                           "Current context:\n" + "\n".join(context_parts)
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": user_prompt})
        return messages
        
    def ask(self, prompt: str, use_context: bool = True) -> str:
        """Ask the AI assistant a question"""
        if not self.client:
            return "❌ No API key configured. Run 'setup' first."
            
        # Get optimal model
        model = self.token_manager.get_optimal_model()
        
        # Prepare messages
        if use_context:
            messages = self.enhance_prompt_with_context(prompt)
        else:
            messages = [{"role": "user", "content": prompt}]
            
        # Make API request
        print(f"🤖 Using model: {model}")
        response = self.client.chat_completion(model, messages)
        
        if "error" in response:
            return f"❌ Error: {response['error']}"
            
        # Extract response
        try:
            content = response['choices'][0]['message']['content']
            tokens_used = response['usage']['total_tokens']
            
            # Record usage
            self.token_manager.record_usage(model, tokens_used, 0.0)
            
            return content
        except (KeyError, IndexError) as e:
            return f"❌ Unexpected response format: {e}"
            
    def show_stats(self, days: int = 7):
        """Display usage statistics"""
        stats = self.token_manager.get_usage_stats(days)
        
        print(f"\n📊 Usage statistics for last {days} days:\n")
        
        total_requests = 0
        total_tokens = 0
        total_cost = 0.0
        
        for model, data in stats.items():
            print(f"🤖 {model}")
            print(f"   Requests: {data['requests']}")
            print(f"   Tokens: {data['tokens']:,}")
            print(f"   Cost: ${data['cost']:.4f}")
            print()
            
            total_requests += data['requests']
            total_tokens += data['tokens']
            total_cost += data['cost']
            
        if stats:
            print("📈 Totals:")
            print(f"   Total Requests: {total_requests}")
            print(f"   Total Tokens: {total_tokens:,}")
            print(f"   Total Cost: ${total_cost:.4f}")
        else:
            print("No usage data found for this period.")
            
    def list_models(self):
        """List available free models"""
        print("\n🤖 Available Free Models:\n")
        
        for i, model in enumerate(FREE_MODELS, 1):
            requests, tokens = self.token_manager.get_today_usage(model['id'])
            usage_pct = (requests / model['daily_limit']) * 100
            
            print(f"{i}. {model['name']}")
            print(f"   ID: {model['id']}")
            print(f"   Daily Limit: {model['daily_limit']} requests")
            print(f"   Context Window: {model['context_window']:,} tokens")
            print(f"   Best For: {model['best_for']}")
            print(f"   Today's Usage: {requests}/{model['daily_limit']} ({usage_pct:.1f}%)")
            print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub CLI AI Assistant with intelligent token management"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Configure API keys")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask the AI assistant a question")
    ask_parser.add_argument("prompt", nargs="+", help="Your question or prompt")
    ask_parser.add_argument("--no-context", action="store_true", 
                           help="Don't include GitHub context")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show usage statistics")
    stats_parser.add_argument("--days", type=int, default=7, 
                             help="Number of days to show (default: 7)")
    
    # Models command
    subparsers.add_parser("models", help="List available models")
    
    args = parser.parse_args()
    
    assistant = AIAssistant()
    
    if args.command == "setup":
        assistant.setup_api_key()
    elif args.command == "ask":
        prompt = " ".join(args.prompt)
        use_context = not args.no_context
        response = assistant.ask(prompt, use_context)
        print(f"\n{response}\n")
    elif args.command == "stats":
        assistant.show_stats(args.days)
    elif args.command == "models":
        assistant.list_models()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
