#!/usr/bin/env python3
"""
Test script for Memory Transfer System
Demonstrates intelligent handoff with context preservation
"""

from memory_transfer import MemoryTransferManager, ConversationMemory
import json


def test_basic_functionality():
    """Test basic memory transfer operations"""
    print("=" * 70)
    print("TEST 1: Basic Functionality")
    print("=" * 70)
    
    manager = MemoryTransferManager()
    
    # Test token counting
    text = "This is a test message with some content"
    tokens = manager.count_tokens(text)
    print(f"✅ Token counting: '{text}' = {tokens} tokens")
    
    # Test context window lookup
    for model_id in ["meta-llama/llama-3.2-3b-instruct:free", 
                     "deepseek/deepseek-r1:free",
                     "google/gemini-2.0-flash-exp:free"]:
        window = manager.get_context_window(model_id)
        budget = manager.calculate_memory_budget(model_id)
        print(f"✅ {model_id[:30]:30} → {window:>8,} tokens (budget: {budget} tokens)")
    
    print()


def test_handoff_detection():
    """Test handoff trigger detection"""
    print("=" * 70)
    print("TEST 2: Handoff Detection")
    print("=" * 70)
    
    manager = MemoryTransferManager()
    
    # Test scenarios
    scenarios = [
        ("meta-llama/llama-3.2-3b-instruct:free", 1600, "Can you show me a complete example with JWT?"),
        ("meta-llama/llama-3.2-3b-instruct:free", 500, "What is Python?"),
        ("google/gemini-2.0-flash-exp:free", 900000, "Explain the entire Python ecosystem"),
    ]
    
    for model, current, prompt in scenarios:
        should_handoff, predicted, reason = manager.should_handoff(
            model, current, prompt
        )
        
        window = manager.get_context_window(model)
        usage_pct = (predicted / window) * 100
        
        status = "🔄 HANDOFF" if should_handoff else "✅ CONTINUE"
        print(f"{status} | {model[:30]:30} | {current:>6}/{window:<8,} tokens | "
              f"Predicted: {predicted:>6} ({usage_pct:>5.1f}%)")
        if should_handoff:
            print(f"         Reason: {reason}")
    
    print()


def test_memory_extraction():
    """Test memory extraction and compression"""
    print("=" * 70)
    print("TEST 3: Memory Extraction & Compression")
    print("=" * 70)
    
    manager = MemoryTransferManager()
    
    # Simulate conversation
    conversation_history = [
        {"role": "user", "content": "I'm building a FastAPI application for user authentication"},
        {"role": "assistant", "content": "Great choice! FastAPI is excellent for building APIs. For authentication, you'll want to use OAuth2 with JWT tokens. Here's how to get started..."},
        {"role": "user", "content": "How do I implement JWT token generation?"},
        {"role": "assistant", "content": "For JWT tokens in FastAPI, you'll need the python-jose library. Here's a complete implementation: [code example]"},
        {"role": "user", "content": "Now I need to add refresh token support"},
        {"role": "assistant", "content": "Refresh tokens are important for long-lived sessions. You'll need to store them securely..."},
    ]
    
    technical_files = [
        "auth.py: OAuth2 implementation with JWT",
        "models.py: User and Token database models",
        "config.py: Security configuration"
    ]
    
    project_context = "Building production-ready FastAPI authentication system with JWT and refresh tokens"
    
    # Extract memory
    memory = manager.extract_memory(
        conversation_history,
        technical_files,
        project_context
    )
    
    print("📝 Extracted Memory:")
    print(f"   Technical: {len(memory.technical_context)} chars")
    print(f"   Project: {len(memory.project_state)} chars")
    print(f"   Flow: {len(memory.conversation_flow)} chars")
    print(f"   Metadata: {memory.metadata}")
    print()
    
    # Test compression for different models
    test_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
    ]
    
    for model in test_models:
        compressed = manager.compress_memory(memory, model)
        tokens = manager.count_tokens(compressed)
        budget = manager.calculate_memory_budget(model)
        
        print(f"🗜️  Compressed for {model[:30]}:")
        print(f"   Budget: {budget} tokens")
        print(f"   Actual: {tokens} tokens ({(tokens/budget)*100:.1f}% of budget)")
        print(f"   Preview: {compressed[:100]}...")
        print()


def test_full_handoff():
    """Test complete handoff execution"""
    print("=" * 70)
    print("TEST 4: Complete Handoff Execution")
    print("=" * 70)
    
    manager = MemoryTransferManager()
    
    # Simulate realistic scenario
    conversation_history = [
        {"role": "user", "content": "I'm working on a Python API using FastAPI for user authentication"},
        {"role": "assistant", "content": "Great! FastAPI is excellent for building APIs. Let me help you with authentication..."},
        {"role": "user", "content": "How do I implement JWT authentication?"},
        {"role": "assistant", "content": "For JWT authentication in FastAPI, you'll need python-jose. Here's a complete example with token generation and validation..."},
        {"role": "user", "content": "Now add refresh token rotation"},
    ]
    
    current_model = "meta-llama/llama-3.2-3b-instruct:free"
    current_tokens = 1600
    new_prompt = "Can you show me a complete implementation with refresh token rotation, token blacklisting, and secure storage?"
    
    # Check if handoff needed
    should_handoff, predicted, reason = manager.should_handoff(
        current_model, current_tokens, new_prompt
    )
    
    if should_handoff:
        print(f"🔄 Handoff Triggered!")
        print(f"   Reason: {reason}")
        print()
        
        # Execute handoff
        transfer_prompt, handoff_context = manager.execute_handoff(
            from_model=current_model,
            to_model="google/gemini-2.0-flash-exp:free",
            current_tokens=current_tokens,
            predicted_tokens=predicted,
            conversation_history=conversation_history,
            new_prompt=new_prompt,
            technical_files=["auth.py", "models.py"],
            project_context="Building FastAPI auth system"
        )
        
        # Display handoff summary
        print(manager.format_handoff_summary(handoff_context))
        
        # Show transfer prompt
        print("\n📝 Transfer Prompt Structure:")
        if "[CONTEXT:" in transfer_prompt:
            context_part = transfer_prompt.split("[CONTEXT:")[1].split("]")[0]
            prompt_part = transfer_prompt.split("]")[1].strip()
            context_tokens = manager.count_tokens(context_part)
            prompt_tokens = manager.count_tokens(prompt_part)
            
            print(f"   Context: {context_tokens} tokens")
            print(f"   Prompt: {prompt_tokens} tokens")
            print(f"   Total: {context_tokens + prompt_tokens} tokens")
            print(f"\n   Context Preview: {context_part[:150]}...")
        
        # Get stats
        print("\n📊 Handoff Statistics:")
        stats = manager.get_handoff_stats()
        print(json.dumps(stats, indent=2, default=str))
    else:
        print("✅ No handoff needed in this scenario")
    
    print()


def test_multiple_handoffs():
    """Test multiple sequential handoffs"""
    print("=" * 70)
    print("TEST 5: Multiple Sequential Handoffs")
    print("=" * 70)
    
    manager = MemoryTransferManager()
    
    # Simulate multiple handoffs
    handoff_chain = [
        ("meta-llama/llama-3.2-3b-instruct:free", "deepseek/deepseek-r1:free", 1500),
        ("deepseek/deepseek-r1:free", "google/gemini-2.0-flash-exp:free", 120000),
    ]
    
    conversation = []
    
    for i, (from_model, to_model, current_tokens) in enumerate(handoff_chain, 1):
        print(f"\n🔄 Handoff {i}: {from_model[:25]} → {to_model[:25]}")
        
        transfer_prompt, handoff = manager.execute_handoff(
            from_model=from_model,
            to_model=to_model,
            current_tokens=current_tokens,
            predicted_tokens=current_tokens + 300,
            conversation_history=conversation,
            new_prompt=f"Continue with implementation step {i}"
        )
        
        # Add to conversation
        conversation.append({"role": "user", "content": f"Step {i}"})
        conversation.append({"role": "assistant", "content": f"Response {i}"})
        
        compressed_size = manager.count_tokens(
            manager.compress_memory(handoff.memory, to_model)
        )
        
        print(f"   Memory: {compressed_size} tokens")
        print(f"   Status: ✅ Complete")
    
    # Final stats
    print("\n" + "=" * 70)
    stats = manager.get_handoff_stats()
    print(f"📊 Total Handoffs: {stats['total_handoffs']}")
    print(f"📊 Models Used: {', '.join(stats['models_used'])}")
    print(f"📊 Avg Tokens Saved: {stats['avg_tokens_saved']:,}")
    print("=" * 70)


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║         🧠 MEMORY TRANSFER SYSTEM - COMPREHENSIVE TESTS             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    
    test_basic_functionality()
    test_handoff_detection()
    test_memory_extraction()
    test_full_handoff()
    test_multiple_handoffs()
    
    print("\n✅ All tests completed successfully!")
    print()


if __name__ == "__main__":
    run_all_tests()
