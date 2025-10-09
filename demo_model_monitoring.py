#!/usr/bin/env python3
"""
Test script for model monitoring and dynamic selection
Demonstrates the intelligent model selection system
"""

import time
from model_monitor import ModelMonitor, SmartModelSelector
from gh_ai_core import TokenManager, FREE_MODELS

def demo_monitoring():
    """Demonstrate the model monitoring system"""
    
    print("="*80)
    print("🎯 MODEL MONITORING & DYNAMIC SELECTION DEMO")
    print("="*80)
    print()
    
    # Initialize components
    monitor = ModelMonitor()
    token_manager = TokenManager()
    selector = SmartModelSelector(monitor, FREE_MODELS, token_manager)
    
    print("📊 Step 1: Simulating API requests to build performance data...")
    print()
    
    # Simulate some successful requests
    models_to_test = [
        ("google/gemini-2.0-flash-exp:free", True, 245, 150),
        ("google/gemini-2.0-flash-exp:free", True, 278, 180),
        ("mistralai/mistral-7b-instruct:free", True, 312, 200),
        ("meta-llama/llama-3.2-3b-instruct:free", True, 498, 175),
        ("deepseek/deepseek-r1:free", False, 1200, 0),  # Simulate failure
        ("deepseek/deepseek-r1:free", False, 1150, 0),  # Another failure
        ("google/gemini-2.0-flash-exp:free", True, 251, 165),
        ("mistralai/mistral-7b-instruct:free", True, 289, 190),
    ]
    
    for model_id, success, latency, tokens in models_to_test:
        error_type = None if success else "rate_limit"
        error_msg = None if success else "Rate limit exceeded"
        
        monitor.record_request(
            model_id=model_id,
            success=success,
            latency_ms=latency,
            tokens_used=tokens,
            error_type=error_type,
            error_message=error_msg
        )
        
        status = "✅" if success else "❌"
        print(f"  {status} {model_id}: {latency}ms")
        time.sleep(0.1)  # Small delay for visualization
    
    print()
    print("✅ Simulation complete!")
    print()
    
    # Show rankings
    print("="*80)
    print("📊 Step 2: Current Model Rankings")
    print("="*80)
    
    today_usage = {}
    for model in FREE_MODELS:
        model_id = model['id']
        requests, tokens = token_manager.get_today_usage(model_id)
        today_usage[model_id] = (requests, tokens)
    
    monitor.print_model_rankings(FREE_MODELS, today_usage)
    
    # Get recommendation
    print("="*80)
    print("🎯 Step 3: Smart Model Selection")
    print("="*80)
    print()
    
    recommendation = monitor.get_recommendation(FREE_MODELS, today_usage)
    print(recommendation)
    print()
    
    # Show fallback sequence
    print("="*80)
    print("🔄 Step 4: Automatic Fallback Sequence")
    print("="*80)
    print()
    
    fallback_sequence = selector.get_fallback_sequence()
    
    print("If the primary model fails, the system will try these models in order:")
    print()
    for i, model_id in enumerate(fallback_sequence, 1):
        model_info = next((m for m in FREE_MODELS if m['id'] == model_id), None)
        if model_info:
            print(f"  {i}. {model_info['name']}")
            print(f"     ID: {model_id}")
            stats = monitor.get_model_stats(model_id)
            print(f"     Success Rate: {stats['success_rate']*100:.1f}%")
            print()
    
    # Show detailed stats for one model
    print("="*80)
    print("📈 Step 5: Detailed Model Statistics")
    print("="*80)
    print()
    
    best_model_id = fallback_sequence[0] if fallback_sequence else FREE_MODELS[0]['id']
    stats = monitor.get_model_stats(best_model_id)
    
    print(f"Statistics for: {best_model_id}")
    print()
    print(f"Total Requests:       {stats['total_requests']}")
    print(f"Successful:           {stats['successes']}")
    print(f"Failed:               {stats['failures']}")
    print(f"Success Rate:         {stats['success_rate']*100:.1f}%")
    print(f"Error Rate:           {stats['error_rate']*100:.1f}%")
    print(f"Avg Latency:          {stats['avg_latency_ms']:.0f}ms")
    print(f"Consecutive Failures: {stats['consecutive_failures']}")
    print(f"Available:            {'Yes' if stats['is_available'] else 'No'}")
    print()
    
    print("="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print()
    print("💡 Try these commands:")
    print("   • python gh_ai_core.py rankings    - Show live rankings")
    print("   • python gh_ai_core.py recommend   - Get best model now")
    print("   • python gh_ai_core.py ask 'test'  - Auto-select best model")
    print()


if __name__ == "__main__":
    try:
        demo_monitoring()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
