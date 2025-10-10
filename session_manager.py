#!/usr/bin/env python3
"""
Session Persistence & Model Rotation Manager
Ensures persistent user identity and intelligent model selection across sessions.

Features:
- Persistent session storage (no "one-night stand" statelessness)
- Token-aware model rotation
- Usage tracking per model
- Automatic handoff recommendations
- Context-aware greetings
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
SESSION_FILE = CONFIG_DIR / "user_session.json"
USAGE_LOG = CONFIG_DIR / "model_usage.json"

# Top free models registry (updated with latest free models)
TOP_FREE_MODELS = [
    {
        "name": "google/gemini-2.0-flash-exp:free",
        "display_name": "Google Gemini 2.0 Flash",
        "provider": "Google",
        "free": True,
        "context_window": 1000000,
        "daily_limit": 1000,
        "best_for": "general conversation, fast responses, large context"
    },
    {
        "name": "deepseek/deepseek-r1:free",
        "display_name": "DeepSeek R1",
        "provider": "DeepSeek",
        "free": True,
        "context_window": 131072,
        "daily_limit": 1000,
        "best_for": "reasoning, math, code analysis"
    },
    {
        "name": "meta-llama/llama-3.2-3b-instruct:free",
        "display_name": "Meta Llama 3.2 3B",
        "provider": "Meta",
        "free": True,
        "context_window": 131072,
        "daily_limit": 1000,
        "best_for": "general tasks, efficiency, balanced performance"
    },
    {
        "name": "mistralai/mistral-7b-instruct:free",
        "display_name": "Mistral 7B Instruct",
        "provider": "Mistral AI",
        "free": True,
        "context_window": 32768,
        "daily_limit": 1000,
        "best_for": "multilingual, instruction following"
    },
    {
        "name": "nvidia/llama-3.1-nemotron-70b-instruct:free",
        "display_name": "Nemotron 70B",
        "provider": "NVIDIA",
        "free": True,
        "context_window": 131072,
        "daily_limit": 1000,
        "best_for": "complex reasoning, large context tasks"
    }
]


@dataclass
class UserSession:
    """Persistent user session"""
    user_name: str
    assistant_name: str
    preferred_model: str
    created_at: datetime
    last_active: datetime
    total_conversations: int
    favorite_models: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            'user_name': self.user_name,
            'assistant_name': self.assistant_name,
            'preferred_model': self.preferred_model,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat(),
            'total_conversations': self.total_conversations,
            'favorite_models': self.favorite_models
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(
            user_name=data['user_name'],
            assistant_name=data['assistant_name'],
            preferred_model=data['preferred_model'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_active=datetime.fromisoformat(data['last_active']),
            total_conversations=data['total_conversations'],
            favorite_models=data.get('favorite_models', [])
        )


@dataclass
class ModelUsage:
    """Track usage per model"""
    model_name: str
    tokens_used_today: int
    requests_today: int
    total_tokens: int
    total_requests: int
    last_used: datetime
    avg_latency_ms: float
    success_rate: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'model_name': self.model_name,
            'tokens_used_today': self.tokens_used_today,
            'requests_today': self.requests_today,
            'total_tokens': self.total_tokens,
            'total_requests': self.total_requests,
            'last_used': self.last_used.isoformat(),
            'avg_latency_ms': self.avg_latency_ms,
            'success_rate': self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(
            model_name=data['model_name'],
            tokens_used_today=data.get('tokens_used_today', 0),
            requests_today=data.get('requests_today', 0),
            total_tokens=data.get('total_tokens', 0),
            total_requests=data.get('total_requests', 0),
            last_used=datetime.fromisoformat(data['last_used']),
            avg_latency_ms=data.get('avg_latency_ms', 0),
            success_rate=data.get('success_rate', 1.0)
        )


class SessionManager:
    """
    Manages persistent sessions and intelligent model rotation.
    
    No more "one-night stand" statelessness—your assistant remembers you!
    """
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.session_file = SESSION_FILE
        self.usage_log = USAGE_LOG
        self._ensure_config_dir()
        self.session: Optional[UserSession] = None
        self.model_usage: Dict[str, ModelUsage] = {}
        self._load_session()
        self._load_usage()
        
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_session(self):
        """Load existing session or create new"""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                self.session = UserSession.from_dict(data)
                # Update last active
                self.session.last_active = datetime.now()
                self.session.total_conversations += 1
                self._save_session()
        else:
            # No session - will create on first use
            self.session = None
            
    def _save_session(self):
        """Save session to file"""
        if self.session:
            with open(self.session_file, 'w') as f:
                json.dump(self.session.to_dict(), f, indent=2)
                
    def _load_usage(self):
        """Load model usage data"""
        if self.usage_log.exists():
            with open(self.usage_log, 'r') as f:
                data = json.load(f)
                for model_name, usage_data in data.items():
                    self.model_usage[model_name] = ModelUsage.from_dict(usage_data)
                    
                    # Reset daily counters if new day
                    last_used = self.model_usage[model_name].last_used
                    if last_used.date() < datetime.now().date():
                        self.model_usage[model_name].tokens_used_today = 0
                        self.model_usage[model_name].requests_today = 0
        
    def _save_usage(self):
        """Save usage data"""
        data = {name: usage.to_dict() for name, usage in self.model_usage.items()}
        with open(self.usage_log, 'w') as f:
            json.dump(data, f, indent=2)
            
    def create_session_interactive(self):
        """Interactively create new session"""
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║                🎉 WELCOME TO YOUR AI ASSISTANT 🎉                   ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print("Let's get to know each other! This will create a persistent session")
        print("so I'll always remember you across conversations.")
        print()
        
        # Get user name
        user_name = input("👤 What's your name? (e.g., Declan): ").strip()
        if not user_name:
            user_name = "User"
            
        # Get assistant name
        assistant_name = input("🤖 What would you like to call me? (e.g., Brakel): ").strip()
        if not assistant_name:
            assistant_name = "Assistant"
            
        # Show available models
        print()
        print("📋 Available Free Models:")
        for i, model in enumerate(TOP_FREE_MODELS, 1):
            print(f"   {i}. {model['display_name']} ({model['provider']})")
            print(f"      Best for: {model['best_for']}")
            
        print()
        choice = input("🎯 Choose your preferred model (1-5, or press Enter for auto-select): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(TOP_FREE_MODELS):
            preferred_model = TOP_FREE_MODELS[int(choice) - 1]['name']
        else:
            # Auto-select best model
            preferred_model = self.select_optimal_model()
            
        # Create session
        self.session = UserSession(
            user_name=user_name,
            assistant_name=assistant_name,
            preferred_model=preferred_model,
            created_at=datetime.now(),
            last_active=datetime.now(),
            total_conversations=1,
            favorite_models=[preferred_model]
        )
        
        self._save_session()
        
        print()
        print("✅ Session created successfully!")
        print()
        print(f"👋 Hello {user_name}, I'm {assistant_name}—your personal AI assistant!")
        print(f"🤖 Running on: {self._get_model_display_name(preferred_model)}")
        print()
        
    def get_greeting(self) -> str:
        """Get personalized greeting"""
        if not self.session:
            return "👋 Hello! I'm your AI assistant."
            
        # Check if returning user
        days_since_last = (datetime.now() - self.session.last_active).days
        
        if days_since_last == 0:
            greeting = f"👋 Welcome back, {self.session.user_name}!"
        elif days_since_last == 1:
            greeting = f"👋 Good to see you again, {self.session.user_name}!"
        elif days_since_last < 7:
            greeting = f"👋 Hello {self.session.user_name}, it's been {days_since_last} days!"
        else:
            greeting = f"👋 Long time no see, {self.session.user_name}! (Been {days_since_last} days)"
            
        current_model = self._get_model_display_name(self.session.preferred_model)
        
        return (f"{greeting}\n"
                f"🤖 I'm {self.session.assistant_name}, powered by {current_model}.\n"
                f"📊 This is conversation #{self.session.total_conversations} together.")
                
    def _get_model_display_name(self, model_id: str) -> str:
        """Get display name for model"""
        for model in TOP_FREE_MODELS:
            if model['name'] == model_id:
                return model['display_name']
        return model_id
        
    def select_optimal_model(self, 
                            exclude_models: List[str] = None,
                            prefer_large_context: bool = False) -> str:
        """
        Intelligently select best model based on:
        1. Current usage (prefer least-used)
        2. Daily limits (avoid exhausted models)
        3. Success rate (prefer reliable models)
        4. User preferences (favorite models)
        
        Algorithm:
        - Calculate score for each model
        - Higher score = better choice
        - Select highest scoring model
        """
        exclude_models = exclude_models or []
        
        scores = []
        
        for model in TOP_FREE_MODELS:
            model_id = model['name']
            
            # Skip excluded models
            if model_id in exclude_models:
                continue
                
            # Get usage data
            usage = self.model_usage.get(model_id)
            
            # Calculate score components
            score = 100  # Base score
            
            # 1. Usage penalty (prefer least used today)
            if usage:
                usage_ratio = usage.requests_today / model['daily_limit']
                score -= usage_ratio * 40  # Up to -40 points
                
                # Success rate bonus
                score += usage.success_rate * 20  # Up to +20 points
                
                # Latency bonus (faster = better)
                if usage.avg_latency_ms > 0:
                    latency_score = max(0, 10 - (usage.avg_latency_ms / 1000))
                    score += latency_score  # Up to +10 points
            else:
                # Never used - small bonus
                score += 5
                
            # 2. Daily limit buffer (avoid near-limit models)
            if usage and usage.requests_today >= model['daily_limit'] * 0.9:
                score -= 50  # Heavy penalty
                
            # 3. Context window bonus (if preferred)
            if prefer_large_context:
                context_bonus = (model['context_window'] / 1000000) * 10
                score += context_bonus  # Up to +10 points
                
            # 4. Favorite model bonus
            if self.session and model_id in self.session.favorite_models:
                score += 15
                
            scores.append({
                'model': model,
                'score': score,
                'usage': usage
            })
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        if scores:
            return scores[0]['model']['name']
        
        # Fallback to first model
        return TOP_FREE_MODELS[0]['name']
        
    def record_usage(self, 
                    model_id: str,
                    tokens_used: int,
                    latency_ms: float = 0,
                    success: bool = True):
        """Record model usage"""
        if model_id not in self.model_usage:
            self.model_usage[model_id] = ModelUsage(
                model_name=model_id,
                tokens_used_today=0,
                requests_today=0,
                total_tokens=0,
                total_requests=0,
                last_used=datetime.now(),
                avg_latency_ms=0,
                success_rate=1.0
            )
        
        usage = self.model_usage[model_id]
        
        # Update counters
        usage.tokens_used_today += tokens_used
        usage.requests_today += 1
        usage.total_tokens += tokens_used
        usage.total_requests += 1
        usage.last_used = datetime.now()
        
        # Update latency (rolling average)
        if latency_ms > 0:
            total_latency = usage.avg_latency_ms * (usage.total_requests - 1)
            usage.avg_latency_ms = (total_latency + latency_ms) / usage.total_requests
            
        # Update success rate (rolling average)
        success_val = 1.0 if success else 0.0
        total_success = usage.success_rate * (usage.total_requests - 1)
        usage.success_rate = (total_success + success_val) / usage.total_requests
        
        self._save_usage()
        
    def should_rotate_model(self, current_model: str) -> Tuple[bool, Optional[str], str]:
        """
        Check if we should rotate to a different model
        
        Returns:
            (should_rotate, suggested_model, reason)
        """
        usage = self.model_usage.get(current_model)
        
        if not usage:
            return False, None, ""
            
        # Get model info
        model_info = next((m for m in TOP_FREE_MODELS if m['name'] == current_model), None)
        if not model_info:
            return False, None, ""
            
        # Check daily limit
        usage_percent = (usage.requests_today / model_info['daily_limit']) * 100
        
        if usage_percent >= 90:
            # Near limit - suggest rotation
            suggested = self.select_optimal_model(exclude_models=[current_model])
            reason = f"Current model at {usage_percent:.0f}% of daily limit"
            return True, suggested, reason
            
        if usage_percent >= 75:
            # Approaching limit - warn
            suggested = self.select_optimal_model(exclude_models=[current_model])
            reason = f"Current model at {usage_percent:.0f}% of daily limit (approaching threshold)"
            return False, suggested, reason  # Don't force, just suggest
            
        return False, None, ""
        
    def get_usage_stats(self) -> Dict:
        """Get comprehensive usage statistics"""
        total_tokens = sum(u.total_tokens for u in self.model_usage.values())
        total_requests = sum(u.total_requests for u in self.model_usage.values())
        
        models_stats = []
        for model in TOP_FREE_MODELS:
            usage = self.model_usage.get(model['name'])
            
            if usage:
                models_stats.append({
                    'name': model['display_name'],
                    'provider': model['provider'],
                    'requests_today': usage.requests_today,
                    'tokens_today': usage.tokens_used_today,
                    'daily_limit': model['daily_limit'],
                    'usage_percent': (usage.requests_today / model['daily_limit']) * 100,
                    'total_requests': usage.total_requests,
                    'total_tokens': usage.total_tokens,
                    'avg_latency_ms': usage.avg_latency_ms,
                    'success_rate': usage.success_rate * 100
                })
            else:
                models_stats.append({
                    'name': model['display_name'],
                    'provider': model['provider'],
                    'requests_today': 0,
                    'tokens_today': 0,
                    'daily_limit': model['daily_limit'],
                    'usage_percent': 0,
                    'total_requests': 0,
                    'total_tokens': 0,
                    'avg_latency_ms': 0,
                    'success_rate': 100
                })
        
        # Sort by usage percent (descending)
        models_stats.sort(key=lambda x: x['usage_percent'], reverse=True)
        
        return {
            'session': self.session.to_dict() if self.session else None,
            'total_tokens': total_tokens,
            'total_requests': total_requests,
            'models': models_stats
        }
        
    def display_stats(self):
        """Display formatted statistics"""
        stats = self.get_usage_stats()
        
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║              SESSION & MODEL USAGE STATISTICS                        ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        
        if self.session:
            print("👤 SESSION INFO:")
            print(f"   User: {self.session.user_name}")
            print(f"   Assistant: {self.session.assistant_name}")
            print(f"   Created: {self.session.created_at.strftime('%Y-%m-%d')}")
            print(f"   Conversations: {self.session.total_conversations}")
            print()
            
        print("📊 OVERALL USAGE:")
        print(f"   Total Requests: {stats['total_requests']:,}")
        print(f"   Total Tokens: {stats['total_tokens']:,}")
        print()
        
        print("🤖 MODEL USAGE (Sorted by Usage):")
        print()
        print(f"{'Model':<30} {'Today':<15} {'Limit':<10} {'Usage %':<10} {'Success':<10}")
        print("─" * 85)
        
        for model in stats['models']:
            usage_bar = "█" * int(model['usage_percent'] / 10)
            print(f"{model['name']:<30} "
                  f"{model['requests_today']:>6}/{model['tokens_today']:>6} "
                  f"{model['daily_limit']:>10} "
                  f"{model['usage_percent']:>8.1f}% "
                  f"{model['success_rate']:>8.1f}%")
            
        print()
        
    def reset_session(self):
        """Reset session (logout)"""
        if self.session_file.exists():
            self.session_file.unlink()
        self.session = None
        print("✅ Session reset. You'll be prompted to create a new session on next use.")


def main():
    """CLI for session management"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Session Persistence & Model Rotation Manager"
    )
    
    parser.add_argument('--init', action='store_true',
                       help='Initialize new session interactively')
    parser.add_argument('--stats', action='store_true',
                       help='Display usage statistics')
    parser.add_argument('--greeting', action='store_true',
                       help='Show personalized greeting')
    parser.add_argument('--suggest-model', action='store_true',
                       help='Suggest optimal model for next conversation')
    parser.add_argument('--reset', action='store_true',
                       help='Reset session')
    
    args = parser.parse_args()
    
    manager = SessionManager()
    
    if args.init or not manager.session:
        manager.create_session_interactive()
        
    elif args.stats:
        manager.display_stats()
        
    elif args.greeting:
        print()
        print(manager.get_greeting())
        print()
        
    elif args.suggest_model:
        optimal = manager.select_optimal_model()
        display_name = manager._get_model_display_name(optimal)
        print(f"\n🎯 Recommended model: {display_name}\n")
        
    elif args.reset:
        manager.reset_session()
        
    else:
        # Show greeting and stats
        print()
        print(manager.get_greeting())
        print()
        manager.display_stats()


if __name__ == "__main__":
    main()
