#!/usr/bin/env python3
"""
GitHub CLI AI Assistant Core Module
Production-ready AI assistant with intelligent token management and free model optimization.
Supports both cloud (OpenRouter) and local (Ollama) AI models.
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
import time

# Import model monitoring and conversation storage
try:
    from model_monitor import ModelMonitor, SmartModelSelector
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

try:
    from model_refresh import refresh_free_models, get_free_models
    MODEL_REFRESH_AVAILABLE = True
except ImportError:
    MODEL_REFRESH_AVAILABLE = False

try:
    from conversation_store import ConversationStore, Message
    CONVERSATION_STORE_AVAILABLE = True
except ImportError:
    CONVERSATION_STORE_AVAILABLE = False

try:
    from startup_init import quick_init
    STARTUP_INIT_AVAILABLE = True
except ImportError:
    STARTUP_INIT_AVAILABLE = False

try:
    from memory_transfer import MemoryTransferManager, ConversationMemory
    MEMORY_TRANSFER_AVAILABLE = True
except ImportError:
    MEMORY_TRANSFER_AVAILABLE = False

try:
    from memory_bridge import MemoryBridge, BridgeState
    MEMORY_BRIDGE_AVAILABLE = True
except ImportError:
    MEMORY_BRIDGE_AVAILABLE = False

# Disable SQLite date adapter deprecation warning for Python 3.12+
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("TIMESTAMP", lambda val: datetime.fromisoformat(val.decode()))

# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
DB_PATH = CONFIG_DIR / "usage.db"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYRING_SERVICE = "gh-ai-assistant"

# Free model prioritization based on OpenRouter
# Note: Free models have daily limits. Check https://openrouter.ai/models for current availability
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
        "id": "google/gemini-2.0-flash-exp:free",
        "name": "Google Gemini 2.0 Flash Free",
        "daily_limit": 1000,
        "context_window": 1000000,
        "best_for": "general conversation, fast responses",
        "cost_per_1k_tokens": 0.0
    },
    {
        "id": "mistralai/mistral-7b-instruct:free",
        "name": "Mistral 7B Instruct Free",
        "daily_limit": 1000,
        "context_window": 32768,
        "best_for": "multilingual, efficiency",
        "cost_per_1k_tokens": 0.0
    },
    {
        "id": "meta-llama/llama-3.2-3b-instruct:free",
        "name": "Meta Llama 3.2 3B Free",
        "daily_limit": 1000,
        "context_window": 131072,
        "best_for": "general tasks, efficiency",
        "cost_per_1k_tokens": 0.0
    }
]

# Local Ollama models (unlimited usage!)
OLLAMA_MODELS = [
    {
        "id": "deepseek-r1:1.5b",
        "name": "DeepSeek R1 1.5B (Local)",
        "daily_limit": float('inf'),  # Unlimited!
        "context_window": 131072,
        "best_for": "reasoning, code (runs locally)",
        "cost_per_1k_tokens": 0.0,
        "local": True
    },
    {
        "id": "llama3.2",
        "name": "Llama 3.2 3B (Local)",
        "daily_limit": float('inf'),  # Unlimited!
        "context_window": 131072,
        "best_for": "general tasks (runs locally)",
        "cost_per_1k_tokens": 0.0,
        "local": True
    }
]


class OllamaClient:
    """Client for local Ollama models"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def list_models(self) -> List[str]:
        """List available local models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
            
    def chat_completion(self, model: str, messages: List[Dict]) -> Dict:
        """Send chat completion to Ollama"""
        try:
            # Convert messages to Ollama format (just the last message for now)
            prompt = messages[-1]['content'] if messages else ""
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "choices": [{
                        "message": {
                            "content": data.get('response', '')
                        }
                    }],
                    "usage": {
                        "total_tokens": len(data.get('response', '').split())  # Rough estimate
                    }
                }
            else:
                return {"error": f"Ollama error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


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
        today = datetime.now().date().isoformat()
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
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                # Rate limit exceeded
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('error', {}).get('message', '')
                except:
                    pass
                return {
                    "error": "rate_limit",
                    "status_code": 429,
                    "message": "Rate limit exceeded for this model",
                    "detail": error_detail,
                    "model": model
                }
            return {"error": str(e), "status_code": response.status_code}
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
        self.ollama_client = OllamaClient()
        self.github_context = GitHubContextExtractor()
        self.use_ollama_fallback = True  # Enable local fallback by default
        
        # Initialize model monitoring
        if MONITORING_AVAILABLE:
            self.monitor = ModelMonitor()
            self.model_selector = SmartModelSelector(
                self.monitor, FREE_MODELS, self.token_manager
            )
        else:
            self.monitor = None
            self.model_selector = None
        
        # Initialize conversation storage
        if CONVERSATION_STORE_AVAILABLE:
            self.conversation_store = ConversationStore()
            self.current_session_id = self.conversation_store.get_active_session()
            if not self.current_session_id:
                self.current_session_id = self.conversation_store.create_session()
        else:
            self.conversation_store = None
            self.current_session_id = None
        
        # Initialize memory transfer system
        if MEMORY_TRANSFER_AVAILABLE:
            self.memory_manager = MemoryTransferManager()
        else:
            self.memory_manager = None
        
        # Initialize memory bridge (ultimate failsafe)
        if MEMORY_BRIDGE_AVAILABLE:
            self.memory_bridge = MemoryBridge()
        else:
            self.memory_bridge = None
        
        # Track conversation for handoffs
        self.conversation_history = []
        self.current_model = None
        self.current_token_count = 0
        self.exhausted_models = []  # Track which models hit limits
        
    def _load_api_key(self) -> Optional[str]:
        """Load API key from system keyring"""
        return keyring.get_password(KEYRING_SERVICE, "openrouter_api_key")
        
    def _save_api_key(self, api_key: str):
        """Save API key to system keyring"""
        keyring.set_password(KEYRING_SERVICE, "openrouter_api_key", api_key)
        
    def setup_api_key(self):
        """Interactive API key setup"""
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║          🔐 GitHub CLI AI Assistant - Setup                         ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print("\nTo use this assistant, you need an OpenRouter API key.")
        print("\n📍 Step 1: Get API Key")
        print("   Visit: https://openrouter.ai/keys")
        print("\n📍 Step 2: ⚠️  CRITICAL - Enable Model Training (Required for Free Models)")
        print("   Visit: https://openrouter.ai/settings/privacy")
        print("   Turn ON 'Model Training'")
        print("   → Without this, you'll get rate limits even with credits!")
        print("\n📍 Step 3: (Optional) Add Credits for Higher Limits")
        print("   Visit: https://openrouter.ai/credits")
        print("\nOpenRouter provides FREE access to:")
        for model in FREE_MODELS:
            print(f"  • {model['name']} ({model['daily_limit']} requests/day)")
        print("\n⚠️  Important: Free models require 'Model Training' to be enabled!")
        print("   See OPENROUTER_SETUP.md for complete instructions.")
        
        api_key = input("\nEnter your OpenRouter API key: ").strip()
        
        if api_key:
            self._save_api_key(api_key)
            self.api_key = api_key
            self.client = OpenRouterClient(api_key)
            print("\n✅ API key saved successfully!")
            print("\n⚠️  NEXT STEPS:")
            print("   1. Enable 'Model Training': https://openrouter.ai/settings/privacy")
            print("   2. Verify it's ON (required for free models)")
            print("   3. Test with: python gh_ai_core.py ask 'Hello!'")
            print("\n📖 Full setup guide: See OPENROUTER_SETUP.md")
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
        """Ask the AI assistant a question with cloud and local fallback"""
        
        # Check if bridge is active (recovering from total exhaustion)
        if self.memory_bridge and self.memory_bridge.active_bridge:
            status = self.memory_bridge.get_bridge_status()
            
            if status and status['state'] == BridgeState.ACTIVATED.value:
                # Try to recover
                all_models = [m['id'] for m in FREE_MODELS]
                available_models = self._get_available_models()
                
                if self.memory_bridge.check_recovery_possible(available_models):
                    print("🔄 Memory Bridge Recovery Detected!")
                    
                    # Attempt recovery with first available model
                    success, recovery_prompt = self.memory_bridge.attempt_recovery(available_models[0])
                    
                    if success:
                        # Use recovery prompt instead of original
                        prompt = recovery_prompt
                        print(f"   Using model: {available_models[0]}")
                        print()
                else:
                    # Still in bridge state
                    print(self.memory_bridge.format_bridge_message())
                    return "⏳ Waiting for model recovery. Your conversation is preserved and will resume automatically."
        
        # Check if we need to handoff to a different model
        if self.memory_manager and self.current_model and self.current_token_count > 0:
            should_handoff, predicted_total, reason = self.memory_manager.should_handoff(
                self.current_model, self.current_token_count, prompt
            )
            
            if should_handoff:
                print(f"\n🔄 Intelligent Handoff Triggered")
                print(f"   Reason: {reason}")
                
                # Determine best next model
                next_model = self._select_next_model_for_handoff()
                
                if next_model and next_model != self.current_model:
                    # Execute handoff with memory transfer
                    transfer_prompt, handoff_context = self.memory_manager.execute_handoff(
                        from_model=self.current_model,
                        to_model=next_model,
                        current_tokens=self.current_token_count,
                        predicted_tokens=predicted_total,
                        conversation_history=self.conversation_history,
                        new_prompt=prompt
                    )
                    
                    print(f"   Transferring to: {next_model}")
                    print(f"   Memory compressed: {self.memory_manager.count_tokens(transfer_prompt.split('[CONTEXT:')[1].split(']')[0]) if '[CONTEXT:' in transfer_prompt else 0} tokens")
                    print()
                    
                    # Use transfer prompt instead of original
                    prompt = transfer_prompt
                    
                    # Reset token count for new model
                    self.current_token_count = self.memory_manager.count_tokens(prompt)
                    self.current_model = next_model
        
        # Try cloud models first (if configured)
        if self.client:
            # Get optimal model sequence using smart selector
            if self.model_selector:
                models_to_try = self.model_selector.get_fallback_sequence()
                if not models_to_try:
                    # Fall back to default order
                    models_to_try = [model['id'] for model in FREE_MODELS]
            else:
                # Use default order if monitoring not available
                models_to_try = [model['id'] for model in FREE_MODELS]
            
            for attempt, model in enumerate(models_to_try):
                # Check if this model is already at limit
                requests, tokens = self.token_manager.get_today_usage(model)
                model_info = next((m for m in FREE_MODELS if m['id'] == model), None)
                
                if model_info and requests >= model_info['daily_limit']:
                    if attempt == 0:
                        print(f"⚠️  {model} is at daily limit ({requests}/{model_info['daily_limit']})")
                    continue
                
                # Prepare messages
                if use_context:
                    messages = self.enhance_prompt_with_context(prompt)
                else:
                    messages = [{"role": "user", "content": prompt}]
                    
                # Make API request with timing
                start_time = time.time()
                print(f"☁️  Using cloud model: {model}")
                response = self.client.chat_completion(model, messages)
                latency_ms = (time.time() - start_time) * 1000
                
                # Track current model
                self.current_model = model
                
                # Handle rate limit - try next model
                if "error" in response:
                    error_type = response.get("error")
                    
                    # Record failure in monitor
                    if self.monitor:
                        self.monitor.record_request(
                            model, 
                            success=False, 
                            latency_ms=latency_ms,
                            error_type=error_type,
                            error_message=response.get("message", "")
                        )
                    
                    if error_type == "rate_limit" or response.get("status_code") == 429:
                        print(f"⚠️  Rate limit hit for {model}")
                        
                        # Track exhausted model
                        if model not in self.exhausted_models:
                            self.exhausted_models.append(model)
                        
                        if self.model_selector:
                            self.model_selector.mark_failure(model, "rate_limit")
                        
                        if attempt < len(models_to_try) - 1:
                            print(f"🔄 Trying next cloud model...")
                            time.sleep(1)
                            continue
                        else:
                            # All cloud models exhausted
                            print(f"☁️  All cloud models exhausted")
                            
                            # Check if bridge should activate
                            all_model_ids = [m['id'] for m in FREE_MODELS]
                            
                            if self.memory_bridge and self.memory_bridge.should_activate_bridge(
                                self.exhausted_models, all_model_ids
                            ):
                                print()
                                print("🌉 ACTIVATING MEMORY BRIDGE (Ultimate Failsafe)")
                                print()
                                
                                # Activate bridge to preserve context
                                bridge_context = self.memory_bridge.activate_bridge(
                                    user_prompt=prompt,
                                    conversation_history=self.conversation_history,
                                    exhausted_models=self.exhausted_models,
                                    technical_context=self._extract_technical_context(),
                                    project_state=self._extract_project_state()
                                )
                                
                                # Show bridge status to user
                                print(self.memory_bridge.format_bridge_message())
                                
                                return ("🌉 Memory Bridge Activated\n\n"
                                       "All AI models are temporarily at rate limits.\n"
                                       "Your conversation is preserved and will automatically\n"
                                       "resume when any provider becomes available.\n\n"
                                       "This ensures zero context loss with 100% uptime.")
                            
                            # Try local as last resort
                            if self.use_ollama_fallback:
                                print(f"☁️  Trying local models as last resort...")
                                break
                            else:
                                return self._rate_limit_error_message()
                    else:
                        return f"❌ Error: {response.get('error', 'Unknown error')}"
                    
                # Extract response
                try:
                    content = response['choices'][0]['message']['content']
                    tokens_used = response.get('usage', {}).get('total_tokens', 0)
                    
                    # Check for empty content
                    if not content or not content.strip():
                        print(f"⚠️  Empty response from {model}, trying next...")
                        if self.monitor:
                            self.monitor.record_request(
                                model, 
                                success=False, 
                                latency_ms=latency_ms,
                                error_type="empty_response",
                                error_message="Model returned empty content"
                            )
                        if attempt < len(models_to_try) - 1:
                            continue
                        else:
                            return "❌ All models returned empty responses"
                    
                    # Record success in monitor
                    if self.monitor:
                        self.monitor.record_request(
                            model, 
                            success=True, 
                            latency_ms=latency_ms,
                            tokens_used=tokens_used
                        )
                    
                    # Record usage
                    self.token_manager.record_usage(model, tokens_used, 0.0)
                    
                    # Update token count for handoff tracking
                    self.current_token_count += tokens_used
                    
                    # Track conversation for memory transfer
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": content})
                    
                    # Keep only last 20 messages to prevent memory bloat
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                    
                    # Save to conversation history
                    if self.conversation_store and self.current_session_id:
                        try:
                            # Save user message
                            self.conversation_store.add_message(
                                self.current_session_id,
                                Message(
                                    role="user",
                                    content=prompt,
                                    timestamp=datetime.now(),
                                    model_used=None,
                                    tokens_used=0
                                )
                            )
                            # Save assistant response
                            self.conversation_store.add_message(
                                self.current_session_id,
                                Message(
                                    role="assistant",
                                    content=content,
                                    timestamp=datetime.now(),
                                    model_used=model,
                                    tokens_used=tokens_used
                                )
                            )
                        except Exception as e:
                            # Don't fail the request if conversation storage fails
                            if self.monitor:
                                print(f"⚠️  Failed to save conversation: {e}")
                    
                    return content
                except (KeyError, IndexError) as e:
                    # Record parsing failure
                    print(f"⚠️  Failed to parse response from {model}: {e}")
                    if self.monitor:
                        self.monitor.record_request(
                            model, 
                            success=False, 
                            latency_ms=latency_ms,
                            error_type="parsing_error",
                            error_message=str(e)
                        )
                    
                    # Try next model
                    if attempt < len(models_to_try) - 1:
                        print(f"🔄 Trying next cloud model...")
                        continue
                    else:
                        return f"❌ Failed to get valid response from any model. Last error: {e}"
        
        # Try Ollama (local models) as fallback
        if self.use_ollama_fallback and self.ollama_client.is_available():
            return self._try_ollama(prompt, use_context)
        elif self.use_ollama_fallback:
            return (f"❌ All cloud models rate limited and Ollama not available.\n\n"
                   f"💡 Install Ollama for unlimited local AI:\n"
                   f"   brew install ollama\n"
                   f"   ollama pull deepseek-r1:1.5b\n"
                   f"   ollama serve\n\n"
                   f"Or fix OpenRouter - see OPENROUTER_SETUP.md")
        else:
            return self._rate_limit_error_message()
    
    def _try_ollama(self, prompt: str, use_context: bool) -> str:
        """Try local Ollama models"""
        available_models = self.ollama_client.list_models()
        
        # Prefer models we know about
        preferred_models = ["deepseek-r1:1.5b", "llama3.2", "llama3.2:latest"]
        
        # Try preferred models first
        for model_id in preferred_models:
            if any(model_id in m for m in available_models):
                actual_model = next((m for m in available_models if model_id in m), model_id)
                print(f"🏠 Using local model: {actual_model}")
                
                messages = [{"role": "user", "content": prompt}]
                if use_context:
                    messages = self.enhance_prompt_with_context(prompt)
                else:
                    messages = [{"role": "user", "content": prompt}]
                    
                response = self.ollama_client.chat_completion(actual_model, messages)
                
                if "error" not in response:
                    try:
                        content = response['choices'][0]['message']['content']
                        tokens_used = response['usage']['total_tokens']
                        self.token_manager.record_usage(f"ollama:{actual_model}", tokens_used, 0.0)
                        
                        # Save to conversation history
                        if self.conversation_store and self.current_session_id:
                            try:
                                self.conversation_store.add_message(
                                    self.current_session_id,
                                    Message(role="user", content=prompt, timestamp=datetime.now())
                                )
                                self.conversation_store.add_message(
                                    self.current_session_id,
                                    Message(
                                        role="assistant",
                                        content=content,
                                        timestamp=datetime.now(),
                                        model_used=f"ollama:{actual_model}",
                                        tokens_used=tokens_used
                                    )
                                )
                            except:
                                pass  # Don't fail on storage error
                        
                        return content
                    except (KeyError, IndexError):
                        continue
        
        # Try any available model
        if available_models:
            model = available_models[0]
            print(f"🏠 Using local model: {model}")
            messages = [{"role": "user", "content": prompt}]
            response = self.ollama_client.chat_completion(model, messages)
            
            if "error" not in response:
                try:
                    content = response['choices'][0]['message']['content']
                    return content
                except (KeyError, IndexError):
                    pass
        
        return (f"❌ No local models available.\n\n"
               f"Install Ollama models:\n"
               f"   ollama pull deepseek-r1:1.5b\n"
               f"   ollama pull llama3.2")
    
    def _rate_limit_error_message(self) -> str:
        """Return formatted rate limit error message"""
        return (f"❌ All models have hit their rate limits.\n\n"
               f"🔍 Common Cause: OpenRouter 'Model Training' setting\n"
               f"   ⚠️  Even with credits, free models require this setting!\n\n"
               f"✅ Fix (takes 30 seconds):\n"
               f"   1. Visit: https://openrouter.ai/settings/privacy\n"
               f"   2. Enable 'Model Training'\n"
               f"   3. Save settings\n\n"
               f"📊 Your usage today: Run 'python gh_ai_core.py models'\n"
               f"📖 Full guide: See OPENROUTER_SETUP.md\n\n"
               f"Other options:\n"
               f"   • Add credits: https://openrouter.ai/credits\n"
               f"   • Wait for daily reset (midnight UTC)\n"
               f"   • Use local models (Ollama) - unlimited & free!")
    
    def _select_next_model_for_handoff(self) -> Optional[str]:
        """Select the best model for handoff based on context window and availability"""
        if not self.memory_manager:
            return None
        
        # Prefer models with larger context windows for handoffs
        # Sort by context window size (largest first)
        available_models = []
        
        for model in FREE_MODELS:
            model_id = model['id']
            requests, tokens = self.token_manager.get_today_usage(model_id)
            
            # Skip if at limit
            if requests >= model['daily_limit']:
                continue
            
            # Get context window
            context_window = self.memory_manager.get_context_window(model_id)
            
            available_models.append({
                'id': model_id,
                'context_window': context_window,
                'requests': requests
            })
        
        # Sort by context window (largest first), then by usage (least used first)
        available_models.sort(key=lambda x: (-x['context_window'], x['requests']))
        
        if available_models:
            return available_models[0]['id']
        
        return None
    
    def _get_available_models(self) -> List[str]:
        """Get list of currently available models (not exhausted)"""
        available = []
        
        for model in FREE_MODELS:
            model_id = model['id']
            
            # Skip if in exhausted list
            if model_id in self.exhausted_models:
                continue
            
            # Check usage
            requests, _ = self.token_manager.get_today_usage(model_id)
            if requests < model['daily_limit']:
                available.append(model_id)
        
        return available
    
    def _extract_technical_context(self) -> str:
        """Extract technical context from conversation for bridge"""
        technical_terms = []
        
        for msg in self.conversation_history[-10:]:
            content = msg.get('content', '')
            
            # Look for technical indicators
            if any(term in content.lower() for term in [
                'api', 'function', 'class', 'code', 'implementation',
                'fastapi', 'python', 'jwt', 'authentication', 'database'
            ]):
                # Extract key phrases
                words = content.split()[:50]  # First 50 words
                technical_terms.append(' '.join(words))
        
        return ' | '.join(technical_terms[:3]) if technical_terms else "General development"
    
    def _extract_project_state(self) -> str:
        """Extract project state from conversation for bridge"""
        # Look for project-related keywords
        project_keywords = []
        
        for msg in self.conversation_history:
            content = msg.get('content', '')
            
            if any(keyword in content.lower() for keyword in [
                'building', 'implementing', 'creating', 'developing',
                'project', 'system', 'application'
            ]):
                # This might describe the project
                project_keywords.append(content[:100])
        
        if project_keywords:
            return project_keywords[0]  # First project mention
        
        return "Software development project"
            
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
    
    def show_rankings(self):
        """Show model rankings based on performance monitoring"""
        if not self.monitor:
            print("❌ Model monitoring not available. Run: pip install -e .")
            return
            
        # Get today's usage
        today_usage = {}
        for model in FREE_MODELS:
            model_id = model['id']
            requests, tokens = self.token_manager.get_today_usage(model_id)
            today_usage[model_id] = (requests, tokens)
        
        self.monitor.print_model_rankings(FREE_MODELS, today_usage)
    
    def show_recommendation(self):
        """Show recommended model based on current conditions"""
        if not self.monitor:
            print("❌ Model monitoring not available. Run: pip install -e .")
            return
            
        # Get today's usage
        today_usage = {}
        for model in FREE_MODELS:
            model_id = model['id']
            requests, tokens = self.token_manager.get_today_usage(model_id)
            today_usage[model_id] = (requests, tokens)
        
        print()
        print(self.monitor.get_recommendation(FREE_MODELS, today_usage))
        print()
            
    def interactive_chat(self, use_context: bool = True):
        """Start an interactive chat session"""
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║              🤖 GitHub CLI AI Assistant - Chat Mode                 ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print("💬 Interactive chat mode started!")
        print(f"📍 Context: {'GitHub repo context included' if use_context else 'No context (general questions)'}")
        print()
        print("Commands:")
        print("  • Type your question and press Enter")
        print("  • Type 'exit', 'quit', or 'bye' to exit")
        print("  • Type 'context on' or 'context off' to toggle GitHub context")
        print("  • Type 'models' to see available models")
        print("  • Type 'stats' to see usage statistics")
        print()
        print("─" * 70)
        print()
        
        conversation_history = []
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\n👋 Thanks for chatting! Goodbye!")
                    break
                    
                # Check for special commands
                if user_input.lower() == 'context on':
                    use_context = True
                    print("✅ GitHub context enabled")
                    continue
                elif user_input.lower() == 'context off':
                    use_context = False
                    print("✅ GitHub context disabled")
                    continue
                elif user_input.lower() == 'models':
                    self.list_models()
                    continue
                elif user_input.lower() == 'rankings':
                    self.show_rankings()
                    continue
                elif user_input.lower() == 'recommend':
                    self.show_recommendation()
                    continue
                elif user_input.lower() == 'stats':
                    self.show_stats()
                    continue
                elif user_input.lower() in ['help', '?']:
                    print("\n💡 Available commands:")
                    print("  • exit, quit, bye - Exit chat mode")
                    print("  • context on/off - Toggle GitHub context")
                    print("  • models - Show available models")
                    print("  • rankings - Show real-time model performance rankings")
                    print("  • recommend - Get current best model recommendation")
                    print("  • stats - Show usage statistics")
                    print("  • help - Show this help message")
                    print()
                    continue
                
                # Get AI response
                print("AI: ", end="", flush=True)
                response = self.ask(user_input, use_context)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 End of input. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Continuing chat...\n")


def main():
    """Main CLI entry point"""
    # Run startup initialization (quick mode - no verbose output by default)
    if STARTUP_INIT_AVAILABLE:
        quick_init(verbose=False)
    
    parser = argparse.ArgumentParser(
        description="GitHub CLI AI Assistant with intelligent token management"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Configure API keys")
    
    # Chat command (interactive mode)
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat mode")
    chat_parser.add_argument("--no-context", action="store_true", 
                           help="Don't include GitHub context")
    
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
    
    # Rankings command
    subparsers.add_parser("rankings", help="Show real-time model performance rankings")
    
    # Recommend command
    subparsers.add_parser("recommend", help="Get best model recommendation")
    
    # Memory stats command
    subparsers.add_parser("memory", help="Show memory transfer statistics")
    
    # Bridge stats command
    subparsers.add_parser("bridge", help="Show memory bridge statistics")
    
    args = parser.parse_args()
    
    assistant = AIAssistant()
    
    if args.command == "setup":
        assistant.setup_api_key()
    elif args.command == "chat":
        use_context = not args.no_context
        assistant.interactive_chat(use_context)
    elif args.command == "ask":
        prompt = " ".join(args.prompt)
        use_context = not args.no_context
        response = assistant.ask(prompt, use_context)
        print(f"\n{response}\n")
    elif args.command == "stats":
        assistant.show_stats(args.days)
    elif args.command == "models":
        assistant.list_models()
    elif args.command == "rankings":
        assistant.show_rankings()
    elif args.command == "recommend":
        assistant.show_recommendation()
    elif args.command == "memory":
        if assistant.memory_manager:
            stats = assistant.memory_manager.get_handoff_stats()
            print("\n" + "="*70)
            print("🧠 MEMORY TRANSFER STATISTICS")
            print("="*70)
            print(json.dumps(stats, indent=2, default=str))
            print()
        else:
            print("\n❌ Memory transfer system not available")
            print("   Run: cd gh-ai-assistant && pip install -e .")
    elif args.command == "bridge":
        if assistant.memory_bridge:
            stats = assistant.memory_bridge.get_statistics()
            print("\n" + "="*70)
            print("🌉 MEMORY BRIDGE STATISTICS (Ultimate Failsafe)")
            print("="*70)
            print(json.dumps(stats, indent=2, default=str))
            
            # Show current bridge status if active
            status = assistant.memory_bridge.get_bridge_status()
            if status:
                print()
                print("⚠️  ACTIVE BRIDGE:")
                print(assistant.memory_bridge.format_bridge_message())
            print()
        else:
            print("\n❌ Memory bridge system not available")
            print("   Run: cd gh-ai-assistant && pip install -e .")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
