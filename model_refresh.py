#!/usr/bin/env python3
"""
Model Auto-Refresh System
Automatically updates free model list from OpenRouter on startup
Ensures assistant stays relevant with latest available models
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

CONFIG_DIR = Path.home() / ".gh-ai-assistant"
MODELS_CACHE = CONFIG_DIR / "free_models_cache.json"
REFRESH_INTERVAL_HOURS = 6  # Refresh every 6 hours


def fetch_free_models_from_openrouter() -> List[Dict]:
    """
    Fetch current list of free models from OpenRouter API
    Returns list of free model configurations
    """
    try:
        url = 'https://openrouter.ai/api/v1/models'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = data.get('data', [])
        
        # Filter for free models
        free_models = []
        for model in models:
            pricing = model.get('pricing', {})
            prompt_price = pricing.get('prompt', '999')
            
            # Check if truly free (0 cost)
            if prompt_price == '0' or float(prompt_price) == 0:
                free_models.append({
                    'id': model.get('id'),
                    'name': model.get('name', model.get('id')),
                    'context_length': model.get('context_length', 4096),
                    'architecture': model.get('architecture', {}).get('modality', 'text'),
                    'top_provider': model.get('top_provider', {}),
                    'per_request_limits': model.get('per_request_limits')
                })
        
        return free_models
    
    except Exception as e:
        print(f"⚠️  Failed to fetch models from OpenRouter: {e}")
        return []


def convert_to_assistant_format(openrouter_models: List[Dict]) -> List[Dict]:
    """
    Convert OpenRouter model format to assistant format
    Adds daily limits and categorization
    """
    assistant_models = []
    
    for model in openrouter_models:
        # Estimate daily limit based on context and provider
        # Most free models have ~1000 requests/day limit
        daily_limit = 1000
        
        # Determine best use case based on model name/type
        model_id = model['id'].lower()
        if any(x in model_id for x in ['deepseek', 'r1', 'reason']):
            best_for = "reasoning, math, code"
        elif any(x in model_id for x in ['gemini', 'flash']):
            best_for = "speed, general tasks"
        elif any(x in model_id for x in ['llama', 'meta']):
            best_for = "general tasks, conversation"
        elif any(x in model_id for x in ['mistral', 'mixtral']):
            best_for = "multilingual, efficiency"
        elif any(x in model_id for x in ['qwen', 'coder']):
            best_for = "code, technical tasks"
        else:
            best_for = "general purpose"
        
        assistant_models.append({
            'id': model['id'],
            'name': model['name'],
            'daily_limit': daily_limit,
            'context_window': model['context_length'],
            'best_for': best_for,
            'cost_per_1k_tokens': 0.0
        })
    
    return assistant_models


def should_refresh_cache() -> bool:
    """Check if cache should be refreshed"""
    if not MODELS_CACHE.exists():
        return True
    
    try:
        with open(MODELS_CACHE, 'r') as f:
            cache = json.load(f)
            last_update = datetime.fromisoformat(cache.get('last_update', '2000-01-01'))
            age = datetime.now() - last_update
            return age.total_seconds() / 3600 > REFRESH_INTERVAL_HOURS
    except:
        return True


def load_cached_models() -> List[Dict]:
    """Load models from cache"""
    try:
        if MODELS_CACHE.exists():
            with open(MODELS_CACHE, 'r') as f:
                cache = json.load(f)
                return cache.get('models', [])
    except:
        pass
    return []


def save_models_cache(models: List[Dict]):
    """Save models to cache"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    cache = {
        'last_update': datetime.now().isoformat(),
        'models': models,
        'count': len(models)
    }
    
    with open(MODELS_CACHE, 'w') as f:
        json.dump(cache, f, indent=2)


def refresh_free_models(force: bool = False) -> List[Dict]:
    """
    Refresh free models list
    
    Args:
        force: Force refresh even if cache is recent
        
    Returns:
        List of free model configurations
    """
    # Check if refresh needed
    if not force and not should_refresh_cache():
        print("📋 Using cached free models (still fresh)")
        return load_cached_models()
    
    print("🔄 Refreshing free models from OpenRouter...")
    
    # Fetch from OpenRouter
    openrouter_models = fetch_free_models_from_openrouter()
    
    if not openrouter_models:
        print("⚠️  Failed to fetch new models, using cache")
        return load_cached_models()
    
    # Convert to assistant format
    assistant_models = convert_to_assistant_format(openrouter_models)
    
    # Save to cache
    save_models_cache(assistant_models)
    
    print(f"✅ Refreshed {len(assistant_models)} free models")
    print(f"   Top models:")
    for model in assistant_models[:5]:
        print(f"   • {model['name']}")
    
    return assistant_models


def get_free_models() -> List[Dict]:
    """
    Get current list of free models
    Auto-refreshes if cache is stale
    """
    return refresh_free_models(force=False)


def main():
    """Test the refresh system"""
    print("=" * 60)
    print("FREE MODELS AUTO-REFRESH SYSTEM")
    print("=" * 60)
    print()
    
    # Force refresh to see latest
    models = refresh_free_models(force=True)
    
    print()
    print("=" * 60)
    print(f"Total Free Models: {len(models)}")
    print("=" * 60)
    
    # Show by category
    categories = {}
    for model in models:
        category = model['best_for'].split(',')[0].strip()
        if category not in categories:
            categories[category] = []
        categories[category].append(model)
    
    for category, cat_models in sorted(categories.items()):
        print(f"\n{category.upper()}:")
        for model in cat_models[:3]:  # Top 3 per category
            print(f"  • {model['name']}")
            print(f"    ID: {model['id']}")
            print(f"    Context: {model['context_window']:,} tokens")


if __name__ == "__main__":
    main()
