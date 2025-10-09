#!/usr/bin/env python3
"""
OpenRouter Model Monitoring & Dynamic Selection
Intelligently selects the most reliable, least congested, and most efficient free models.
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3

# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
MONITOR_DB_PATH = CONFIG_DIR / "model_monitor.db"
CACHE_DURATION_MINUTES = 5  # How long to cache model stats


@dataclass
class ModelStats:
    """Statistics for a specific model"""
    model_id: str
    name: str
    current_usage_score: float  # 0-100, lower is better
    avg_latency_ms: float
    error_rate: float  # 0-1
    success_rate: float  # 0-1
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    consecutive_failures: int
    total_requests: int
    total_successes: int
    total_failures: int
    is_free: bool
    context_window: int
    daily_limit: int
    requests_today: int
    tokens_today: int


class ModelMonitor:
    """Monitor and track model performance and availability"""
    
    def __init__(self):
        self.db_path = MONITOR_DB_PATH
        self._ensure_config_dir()
        self._init_database()
        self._cache = {}
        self._cache_time = None
        
    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    def _init_database(self):
        """Initialize SQLite database for model monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Model performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL,
                latency_ms REAL,
                tokens_used INTEGER,
                error_type TEXT,
                error_message TEXT
            )
        ''')
        
        # Model availability cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_availability (
                model_id TEXT PRIMARY KEY,
                is_available BOOLEAN DEFAULT 1,
                current_usage_score REAL DEFAULT 0,
                avg_latency_ms REAL DEFAULT 0,
                error_rate REAL DEFAULT 0,
                last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
                consecutive_failures INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model_timestamp 
            ON model_performance(model_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
    def record_request(self, model_id: str, success: bool, latency_ms: float = 0,
                      tokens_used: int = 0, error_type: str = None, 
                      error_message: str = None):
        """Record a model request outcome"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_performance 
            (model_id, success, latency_ms, tokens_used, error_type, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (model_id, success, latency_ms, tokens_used, error_type, error_message))
        
        # Update availability cache
        if success:
            cursor.execute('''
                INSERT INTO model_availability (model_id, consecutive_failures)
                VALUES (?, 0)
                ON CONFLICT(model_id) DO UPDATE SET
                    consecutive_failures = 0,
                    last_checked = CURRENT_TIMESTAMP
            ''', (model_id,))
        else:
            cursor.execute('''
                INSERT INTO model_availability (model_id, consecutive_failures)
                VALUES (?, 1)
                ON CONFLICT(model_id) DO UPDATE SET
                    consecutive_failures = consecutive_failures + 1,
                    is_available = CASE WHEN consecutive_failures >= 3 THEN 0 ELSE 1 END,
                    last_checked = CURRENT_TIMESTAMP
            ''', (model_id,))
        
        conn.commit()
        conn.close()
        
    def get_model_stats(self, model_id: str, hours: int = 24) -> Dict:
        """Get performance statistics for a specific model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures,
                AVG(CASE WHEN success = 1 THEN latency_ms ELSE NULL END) as avg_latency,
                MAX(CASE WHEN success = 1 THEN timestamp ELSE NULL END) as last_success,
                MAX(CASE WHEN success = 0 THEN timestamp ELSE NULL END) as last_failure
            FROM model_performance
            WHERE model_id = ? AND timestamp >= ?
        ''', (model_id, cutoff))
        
        result = cursor.fetchone()
        
        # Get consecutive failures
        cursor.execute('''
            SELECT consecutive_failures, is_available
            FROM model_availability
            WHERE model_id = ?
        ''', (model_id,))
        
        availability = cursor.fetchone()
        
        conn.close()
        
        total = result[0] or 0
        successes = result[1] or 0
        failures = result[2] or 0
        
        return {
            'total_requests': total,
            'successes': successes,
            'failures': failures,
            'success_rate': successes / total if total > 0 else 0.0,
            'error_rate': failures / total if total > 0 else 0.0,
            'avg_latency_ms': result[3] or 0,
            'last_success': result[4],
            'last_failure': result[5],
            'consecutive_failures': availability[0] if availability else 0,
            'is_available': availability[1] if availability else True
        }
        
    def calculate_usage_score(self, model_id: str, model_info: Dict) -> float:
        """
        Calculate usage score (0-100, lower is better)
        Based on: error rate, latency, daily limit usage
        """
        stats = self.get_model_stats(model_id)
        
        # Error rate component (0-40 points)
        error_score = stats['error_rate'] * 40
        
        # Consecutive failures penalty (0-30 points)
        failure_score = min(stats['consecutive_failures'] * 10, 30)
        
        # Latency component (0-20 points)
        # Normalize latency to 0-20 range (assuming 0-5000ms range)
        latency_score = min((stats['avg_latency_ms'] / 5000) * 20, 20)
        
        # Daily limit usage (0-10 points)
        daily_limit = model_info.get('daily_limit', 1000)
        requests_today = model_info.get('requests_today', 0)
        limit_score = (requests_today / daily_limit) * 10 if daily_limit > 0 else 0
        
        total_score = error_score + failure_score + latency_score + limit_score
        
        # Unavailable models get max score
        if not stats['is_available']:
            total_score = 100
            
        return min(total_score, 100)
        
    def fetch_openrouter_rankings(self) -> Optional[Dict]:
        """
        Fetch model rankings from OpenRouter (if available)
        Note: This is based on publicly available data
        """
        try:
            # Try to get model list and stats
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception as e:
            print(f"⚠️  Could not fetch OpenRouter rankings: {e}")
        
        return None
        
    def get_ranked_models(self, free_models: List[Dict], 
                         today_usage: Dict[str, Tuple[int, int]]) -> List[Dict]:
        """
        Rank models by reliability and availability
        Returns sorted list of models (best first)
        """
        ranked = []
        
        for model in free_models:
            model_id = model['id']
            requests_today, tokens_today = today_usage.get(model_id, (0, 0))
            
            # Add today's usage to model info
            model_with_usage = model.copy()
            model_with_usage['requests_today'] = requests_today
            model_with_usage['tokens_today'] = tokens_today
            
            # Calculate usage score
            usage_score = self.calculate_usage_score(model_id, model_with_usage)
            stats = self.get_model_stats(model_id)
            
            ranked.append({
                'model': model,
                'usage_score': usage_score,
                'stats': stats,
                'requests_today': requests_today,
                'tokens_today': tokens_today
            })
        
        # Sort by usage score (lower is better)
        ranked.sort(key=lambda x: (x['usage_score'], x['stats']['error_rate']))
        
        return ranked
        
    def get_best_model(self, free_models: List[Dict], 
                      today_usage: Dict[str, Tuple[int, int]],
                      exclude_models: List[str] = None) -> Optional[Dict]:
        """
        Select the best available model based on current conditions
        """
        exclude_models = exclude_models or []
        ranked = self.get_ranked_models(free_models, today_usage)
        
        for entry in ranked:
            model = entry['model']
            model_id = model['id']
            
            # Skip excluded models
            if model_id in exclude_models:
                continue
                
            # Skip if at daily limit
            if entry['requests_today'] >= model['daily_limit']:
                continue
                
            # Skip if too many consecutive failures
            if entry['stats']['consecutive_failures'] >= 3:
                continue
                
            # Skip if usage score too high (congested/unreliable)
            if entry['usage_score'] > 75:
                continue
                
            return entry
            
        return None
        
    def print_model_rankings(self, free_models: List[Dict], 
                           today_usage: Dict[str, Tuple[int, int]]):
        """Print a nice table of model rankings"""
        ranked = self.get_ranked_models(free_models, today_usage)
        
        print("\n" + "="*100)
        print("🎯 MODEL RANKINGS - Real-time Performance & Availability")
        print("="*100)
        print(f"{'Rank':<6} {'Model':<35} {'Score':<8} {'Success':<9} {'Latency':<10} {'Usage':<12} {'Status'}")
        print("-"*100)
        
        for i, entry in enumerate(ranked, 1):
            model = entry['model']
            stats = entry['stats']
            usage_score = entry['usage_score']
            
            # Format values
            model_name = model['name'][:33]
            score_str = f"{usage_score:.1f}/100"
            success_str = f"{stats['success_rate']*100:.1f}%"
            latency_str = f"{stats['avg_latency_ms']:.0f}ms" if stats['avg_latency_ms'] > 0 else "N/A"
            usage_str = f"{entry['requests_today']}/{model['daily_limit']}"
            
            # Status indicator
            if usage_score < 25:
                status = "🟢 Excellent"
            elif usage_score < 50:
                status = "🟡 Good"
            elif usage_score < 75:
                status = "🟠 Fair"
            else:
                status = "🔴 Poor"
                
            if entry['requests_today'] >= model['daily_limit']:
                status = "🚫 Limit Hit"
            elif stats['consecutive_failures'] >= 3:
                status = "❌ Unavailable"
                
            print(f"{i:<6} {model_name:<35} {score_str:<8} {success_str:<9} {latency_str:<10} {usage_str:<12} {status}")
        
        print("-"*100)
        print("\n💡 Score Factors: Error Rate (40%) + Failures (30%) + Latency (20%) + Daily Usage (10%)")
        print("📊 Lower scores are better. Recommended: Use models with score < 50")
        print()
        
    def get_recommendation(self, free_models: List[Dict], 
                          today_usage: Dict[str, Tuple[int, int]]) -> str:
        """Get a recommendation message for the best model to use"""
        best = self.get_best_model(free_models, today_usage)
        
        if best:
            model = best['model']
            score = best['usage_score']
            stats = best['stats']
            
            quality = "excellent" if score < 25 else "good" if score < 50 else "fair"
            
            return (f"🎯 Recommended: {model['name']}\n"
                   f"   Model ID: {model['id']}\n"
                   f"   Quality: {quality.upper()} (score: {score:.1f}/100)\n"
                   f"   Success Rate: {stats['success_rate']*100:.1f}%\n"
                   f"   Avg Latency: {stats['avg_latency_ms']:.0f}ms\n"
                   f"   Today's Usage: {best['requests_today']}/{model['daily_limit']}")
        else:
            return "⚠️  No optimal models available. All models may be at capacity or experiencing issues."


class SmartModelSelector:
    """
    Smart model selection with automatic fallback and rotation
    """
    
    def __init__(self, monitor: ModelMonitor, free_models: List[Dict], 
                 token_manager):
        self.monitor = monitor
        self.free_models = free_models
        self.token_manager = token_manager
        self.failed_models = []  # Track failed models in current session
        
    def select_model(self, task_type: str = "general", 
                    auto_rotate: bool = True) -> Optional[str]:
        """
        Intelligently select the best model for the current task
        
        Args:
            task_type: Type of task (for future optimization)
            auto_rotate: Automatically rotate to next best if current fails
            
        Returns:
            Model ID to use, or None if no models available
        """
        # Get today's usage for all models
        today_usage = {}
        for model in self.free_models:
            model_id = model['id']
            requests, tokens = self.token_manager.get_today_usage(model_id)
            today_usage[model_id] = (requests, tokens)
        
        # Get best model excluding recently failed ones
        best = self.monitor.get_best_model(
            self.free_models, 
            today_usage, 
            exclude_models=self.failed_models
        )
        
        if best:
            return best['model']['id']
        
        # If no good models, try any available model not at limit
        for model in self.free_models:
            model_id = model['id']
            if model_id in self.failed_models:
                continue
            requests, _ = today_usage.get(model_id, (0, 0))
            if requests < model['daily_limit']:
                return model_id
                
        return None
        
    def mark_failure(self, model_id: str, error_type: str = None):
        """Mark a model as failed for this session"""
        if model_id not in self.failed_models:
            self.failed_models.append(model_id)
            
    def clear_failures(self):
        """Clear the failed models list"""
        self.failed_models = []
        
    def get_fallback_sequence(self) -> List[str]:
        """
        Get an ordered sequence of models to try (best to worst)
        """
        today_usage = {}
        for model in self.free_models:
            model_id = model['id']
            requests, tokens = self.token_manager.get_today_usage(model_id)
            today_usage[model_id] = (requests, tokens)
        
        ranked = self.monitor.get_ranked_models(self.free_models, today_usage)
        
        # Return model IDs in order of preference
        return [entry['model']['id'] for entry in ranked 
                if entry['requests_today'] < entry['model']['daily_limit']]


def main():
    """CLI for model monitoring"""
    import argparse
    from gh_ai_core import TokenManager, FREE_MODELS
    
    parser = argparse.ArgumentParser(description="OpenRouter Model Monitor")
    parser.add_argument("--rankings", action="store_true", 
                       help="Show current model rankings")
    parser.add_argument("--recommend", action="store_true",
                       help="Get model recommendation")
    parser.add_argument("--stats", metavar="MODEL_ID",
                       help="Show stats for specific model")
    parser.add_argument("--clear", action="store_true",
                       help="Clear monitoring data")
    
    args = parser.parse_args()
    
    monitor = ModelMonitor()
    token_manager = TokenManager()
    
    # Get today's usage
    today_usage = {}
    for model in FREE_MODELS:
        model_id = model['id']
        requests, tokens = token_manager.get_today_usage(model_id)
        today_usage[model_id] = (requests, tokens)
    
    if args.rankings:
        monitor.print_model_rankings(FREE_MODELS, today_usage)
    elif args.recommend:
        print(monitor.get_recommendation(FREE_MODELS, today_usage))
    elif args.stats:
        stats = monitor.get_model_stats(args.stats)
        print(f"\n📊 Statistics for {args.stats}:")
        print(json.dumps(stats, indent=2, default=str))
    elif args.clear:
        import os
        if MONITOR_DB_PATH.exists():
            os.remove(MONITOR_DB_PATH)
            print("✅ Monitoring data cleared")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
