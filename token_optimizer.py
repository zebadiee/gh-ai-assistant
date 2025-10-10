#!/usr/bin/env python3
"""
Token Usage & Efficiency Optimizer
Implements advanced caching, parallel processing, and metric-based optimization
for the gh-ai-assistant system using OpenRouter API best practices.
"""

import json
import hashlib
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import sqlite3
import tiktoken

# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
CACHE_DB = CONFIG_DIR / "token_cache.db"
METRICS_DB = CONFIG_DIR / "token_metrics.db"
MAX_CACHE_AGE_HOURS = 24
MAX_WORKERS = 10


@dataclass
class TokenMetrics:
    """Token usage and efficiency metrics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    latency_ms: float
    cache_hit: bool
    model: str
    timestamp: datetime
    
    def efficiency_score(self) -> float:
        """Calculate efficiency score (tokens per second per dollar)"""
        if self.cost == 0:
            return float('inf')  # Free models have infinite efficiency
        tokens_per_second = self.total_tokens / (self.latency_ms / 1000)
        return tokens_per_second / self.cost


@dataclass
class CachedResponse:
    """Cached API response"""
    prompt_hash: str
    response: str
    tokens: int
    model: str
    timestamp: datetime
    hit_count: int = 0
    
    def is_valid(self, max_age_hours: int = MAX_CACHE_AGE_HOURS) -> bool:
        """Check if cache entry is still valid"""
        age = datetime.now() - self.timestamp
        return age < timedelta(hours=max_age_hours)


class TokenCache:
    """Semantic caching system for API responses"""
    
    def __init__(self, db_path: Path = CACHE_DB):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database for caching"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_cache (
                prompt_hash TEXT PRIMARY KEY,
                response TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                model TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                hit_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON response_cache(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
    def _hash_prompt(self, prompt: str, model: str) -> str:
        """Create semantic hash of prompt"""
        # Normalize prompt (remove extra whitespace, lowercase for semantic matching)
        normalized = ' '.join(prompt.lower().split())
        content = f"{model}:{normalized}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def get(self, prompt: str, model: str) -> Optional[CachedResponse]:
        """Retrieve cached response"""
        prompt_hash = self._hash_prompt(prompt, model)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prompt_hash, response, tokens, model, timestamp, hit_count
            FROM response_cache
            WHERE prompt_hash = ?
        ''', (prompt_hash,))
        
        row = cursor.fetchone()
        
        if row:
            cached = CachedResponse(
                prompt_hash=row[0],
                response=row[1],
                tokens=row[2],
                model=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                hit_count=row[5]
            )
            
            if cached.is_valid():
                # Increment hit count
                cursor.execute('''
                    UPDATE response_cache 
                    SET hit_count = hit_count + 1
                    WHERE prompt_hash = ?
                ''', (prompt_hash,))
                conn.commit()
                conn.close()
                return cached
        
        conn.close()
        return None
        
    def set(self, prompt: str, model: str, response: str, tokens: int):
        """Cache a response"""
        prompt_hash = self._hash_prompt(prompt, model)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO response_cache 
            (prompt_hash, response, tokens, model, timestamp, hit_count)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (prompt_hash, response, tokens, model, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    def clear_old(self, max_age_hours: int = MAX_CACHE_AGE_HOURS):
        """Clear old cache entries"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM response_cache
            WHERE timestamp < ?
        ''', (cutoff.isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), SUM(hit_count), SUM(tokens) FROM response_cache')
        total_entries, total_hits, total_tokens_saved = cursor.fetchone()
        
        cursor.execute('''
            SELECT model, COUNT(*), SUM(hit_count), AVG(tokens)
            FROM response_cache
            GROUP BY model
        ''')
        by_model = {row[0]: {
            'entries': row[1],
            'hits': row[2],
            'avg_tokens': row[3]
        } for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_entries': total_entries or 0,
            'total_hits': total_hits or 0,
            'total_tokens_saved': total_tokens_saved or 0,
            'by_model': by_model
        }


class TokenMetricsTracker:
    """Track and analyze token usage metrics"""
    
    def __init__(self, db_path: Path = METRICS_DB):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize metrics database"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                cost REAL NOT NULL,
                latency_ms REAL NOT NULL,
                cache_hit BOOLEAN NOT NULL,
                model TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model_timestamp 
            ON token_metrics(model, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
    def record(self, metrics: TokenMetrics):
        """Record token usage metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO token_metrics 
            (prompt_tokens, completion_tokens, total_tokens, cost, latency_ms, 
             cache_hit, model, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.prompt_tokens,
            metrics.completion_tokens,
            metrics.total_tokens,
            metrics.cost,
            metrics.latency_ms,
            metrics.cache_hit,
            metrics.model,
            metrics.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(total_tokens) as total_tokens,
                SUM(cost) as total_cost,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits
            FROM token_metrics
            WHERE timestamp > ?
        ''', (cutoff.isoformat(),))
        
        overall = cursor.fetchone()
        
        # Per-model stats
        cursor.execute('''
            SELECT 
                model,
                COUNT(*) as requests,
                SUM(total_tokens) as tokens,
                SUM(cost) as cost,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits
            FROM token_metrics
            WHERE timestamp > ?
            GROUP BY model
            ORDER BY tokens DESC
        ''', (cutoff.isoformat(),))
        
        by_model = {}
        for row in cursor.fetchall():
            by_model[row[0]] = {
                'requests': row[1],
                'tokens': row[2],
                'cost': row[3],
                'avg_latency_ms': row[4],
                'cache_hits': row[5],
                'cache_hit_rate': row[5] / row[1] if row[1] > 0 else 0
            }
        
        conn.close()
        
        total_requests = overall[0] or 0
        cache_hits = overall[4] or 0
        
        return {
            'period_hours': hours,
            'total_requests': total_requests,
            'total_tokens': overall[1] or 0,
            'total_cost': overall[2] or 0,
            'avg_latency_ms': overall[3] or 0,
            'cache_hit_rate': cache_hits / total_requests if total_requests > 0 else 0,
            'by_model': by_model
        }
        
    def get_efficiency_rankings(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get models ranked by efficiency score"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                model,
                AVG(total_tokens / (latency_ms / 1000.0)) as tokens_per_second,
                AVG(cost) as avg_cost,
                COUNT(*) as requests
            FROM token_metrics
            WHERE timestamp > ? AND cost > 0
            GROUP BY model
        ''', (cutoff.isoformat(),))
        
        rankings = []
        for row in cursor.fetchall():
            efficiency = row[1] / row[2] if row[2] > 0 else float('inf')
            rankings.append({
                'model': row[0],
                'tokens_per_second': row[1],
                'avg_cost': row[2],
                'efficiency_score': efficiency,
                'requests': row[3]
            })
        
        conn.close()
        
        # Sort by efficiency score
        rankings.sort(key=lambda x: x['efficiency_score'], reverse=True)
        return rankings


class ParallelTokenizer:
    """Parallel processing for tokenization and API requests"""
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.encoder_cache = {}
        
    @lru_cache(maxsize=10)
    def get_encoder(self, model: str):
        """Get tiktoken encoder for model (cached)"""
        try:
            # Map model names to tiktoken encodings
            if 'gpt-4' in model or 'gpt-3.5' in model:
                return tiktoken.encoding_for_model(model)
            else:
                # Use cl100k_base for most modern models
                return tiktoken.get_encoding("cl100k_base")
        except:
            # Fallback to cl100k_base
            return tiktoken.get_encoding("cl100k_base")
            
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text"""
        encoder = self.get_encoder(model)
        return len(encoder.encode(text))
        
    def batch_count_tokens(self, texts: List[str], model: str = "gpt-3.5-turbo") -> List[int]:
        """Count tokens for multiple texts in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.count_tokens, text, model): i 
                      for i, text in enumerate(texts)}
            
            results = [0] * len(texts)
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                
        return results
        
    def optimize_prompt(self, prompt: str, max_tokens: int = 2000, model: str = "gpt-3.5-turbo") -> str:
        """Optimize prompt to fit within token limit"""
        current_tokens = self.count_tokens(prompt, model)
        
        if current_tokens <= max_tokens:
            return prompt
            
        # Truncate prompt intelligently
        encoder = self.get_encoder(model)
        tokens = encoder.encode(prompt)
        truncated = tokens[:max_tokens]
        
        return encoder.decode(truncated)


class TokenOptimizer:
    """Main token optimization orchestrator"""
    
    def __init__(self):
        self.cache = TokenCache()
        self.metrics = TokenMetricsTracker()
        self.tokenizer = ParallelTokenizer()
        
    def process_request(self, prompt: str, model: str, 
                       use_cache: bool = True) -> Tuple[str, TokenMetrics]:
        """Process a request with caching and metrics tracking"""
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cached = self.cache.get(prompt, model)
            if cached:
                latency_ms = (time.time() - start_time) * 1000
                
                metrics = TokenMetrics(
                    prompt_tokens=self.tokenizer.count_tokens(prompt, model),
                    completion_tokens=cached.tokens,
                    total_tokens=self.tokenizer.count_tokens(prompt, model) + cached.tokens,
                    cost=0.0,  # Cache hits are free
                    latency_ms=latency_ms,
                    cache_hit=True,
                    model=model,
                    timestamp=datetime.now()
                )
                
                self.metrics.record(metrics)
                return cached.response, metrics
        
        # If not in cache, would make actual API call here
        # For now, return placeholder
        response = "[Would make actual API call here]"
        prompt_tokens = self.tokenizer.count_tokens(prompt, model)
        completion_tokens = self.tokenizer.count_tokens(response, model)
        
        latency_ms = (time.time() - start_time) * 1000
        
        metrics = TokenMetrics(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=0.0,  # Calculate based on model pricing
            latency_ms=latency_ms,
            cache_hit=False,
            model=model,
            timestamp=datetime.now()
        )
        
        # Cache the response
        if use_cache:
            self.cache.set(prompt, model, response, completion_tokens)
        
        self.metrics.record(metrics)
        return response, metrics
        
    def batch_process(self, prompts: List[str], model: str, 
                     use_cache: bool = True) -> List[Tuple[str, TokenMetrics]]:
        """Process multiple requests in parallel"""
        with ThreadPoolExecutor(max_workers=self.tokenizer.max_workers) as executor:
            futures = {executor.submit(self.process_request, prompt, model, use_cache): i 
                      for i, prompt in enumerate(prompts)}
            
            results = [None] * len(prompts)
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                
        return results
        
    def get_optimization_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        cache_stats = self.cache.get_stats()
        metrics_summary = self.metrics.get_summary(hours)
        efficiency_rankings = self.metrics.get_efficiency_rankings(hours)
        
        # Calculate savings
        total_requests = metrics_summary['total_requests']
        cache_hits = cache_stats['total_hits']
        cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        
        tokens_saved = cache_stats['total_tokens_saved']
        cost_saved = tokens_saved * 0.00001  # Rough estimate
        
        return {
            'period_hours': hours,
            'cache': {
                'total_entries': cache_stats['total_entries'],
                'total_hits': cache_hits,
                'hit_rate': cache_hit_rate,
                'tokens_saved': tokens_saved,
                'estimated_cost_saved': cost_saved,
                'by_model': cache_stats['by_model']
            },
            'metrics': metrics_summary,
            'efficiency_rankings': efficiency_rankings,
            'recommendations': self._generate_recommendations(
                cache_stats, metrics_summary, efficiency_rankings
            )
        }
        
    def _generate_recommendations(self, cache_stats, metrics_summary, 
                                 efficiency_rankings) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Cache recommendations
        if cache_stats['total_entries'] > 0:
            hit_rate = cache_stats['total_hits'] / metrics_summary['total_requests']
            if hit_rate < 0.2:
                recommendations.append(
                    "Low cache hit rate. Consider increasing cache duration or "
                    "reviewing prompt patterns for better caching."
                )
        
        # Efficiency recommendations
        if efficiency_rankings:
            best_model = efficiency_rankings[0]['model']
            recommendations.append(
                f"Most efficient model: {best_model}. "
                f"Consider prioritizing this model for cost optimization."
            )
        
        # Cost recommendations
        total_cost = metrics_summary['total_cost']
        if total_cost > 1.0:  # Over $1
            recommendations.append(
                f"High API costs detected (${total_cost:.2f}). "
                f"Review model selection and implement prompt optimization."
            )
        
        return recommendations
        
    def cleanup(self):
        """Clean up old cache entries"""
        deleted = self.cache.clear_old()
        return {'deleted_entries': deleted}


def main():
    """CLI for token optimizer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Token Usage & Efficiency Optimizer')
    parser.add_argument('command', choices=['stats', 'report', 'cleanup', 'test'],
                       help='Command to execute')
    parser.add_argument('--hours', type=int, default=24,
                       help='Time period for stats/report (hours)')
    
    args = parser.parse_args()
    
    optimizer = TokenOptimizer()
    
    if args.command == 'stats':
        stats = optimizer.metrics.get_summary(args.hours)
        print(json.dumps(stats, indent=2))
        
    elif args.command == 'report':
        report = optimizer.get_optimization_report(args.hours)
        print(json.dumps(report, indent=2, default=str))
        
    elif args.command == 'cleanup':
        result = optimizer.cleanup()
        print(f"Cleaned up {result['deleted_entries']} old cache entries")
        
    elif args.command == 'test':
        # Test the optimizer
        test_prompts = [
            "What is Python?",
            "Explain machine learning",
            "What is Python?",  # Duplicate for cache test
        ]
        
        print("Testing token optimizer with sample prompts...")
        results = optimizer.batch_process(test_prompts, "gpt-3.5-turbo")
        
        for i, (response, metrics) in enumerate(results):
            print(f"\nPrompt {i+1}: {test_prompts[i]}")
            print(f"Tokens: {metrics.total_tokens}")
            print(f"Cache hit: {metrics.cache_hit}")
            print(f"Latency: {metrics.latency_ms:.2f}ms")


if __name__ == "__main__":
    main()
