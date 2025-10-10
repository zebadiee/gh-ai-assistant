#!/usr/bin/env python3
"""
Intelligent Memory Transfer System
Handles seamless AI model handoffs while preserving project continuity.

Core Features:
- Dynamic token budgets (15% of context window, max 300 tokens)
- Predictive handoffs (triggers at 80% usage)
- Adaptive compression based on target model capabilities
- Priority-based context preservation
"""

import json
import tiktoken
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


# Model context window configurations
MODEL_CONTEXT_WINDOWS = {
    "deepseek/deepseek-r1:free": 131072,
    "google/gemini-2.0-flash-exp:free": 1000000,
    "mistralai/mistral-7b-instruct:free": 32768,
    "meta-llama/llama-3.2-3b-instruct:free": 131072,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
    # Ollama models
    "deepseek-r1:1.5b": 131072,
    "llama3.2": 131072,
}

# Memory allocation percentages
MEMORY_BUDGET_PERCENT = 0.15  # 15% of context window
MAX_MEMORY_TOKENS = 300  # Cap for efficiency
MIN_MEMORY_TOKENS = 40  # Minimum for ultra-compressed

# Handoff trigger threshold
HANDOFF_THRESHOLD = 0.80  # 80% usage triggers handoff


@dataclass
class ConversationMemory:
    """Structured memory for conversation context"""
    technical_context: str  # Code, APIs, technical details
    project_state: str  # Current project status, goals
    conversation_flow: str  # Recent discussion points
    metadata: str  # Timestamps, model info, etc.
    
    def to_compressed_string(self, max_tokens: int) -> str:
        """Compress memory to fit within token budget"""
        encoder = tiktoken.get_encoding("cl100k_base")
        
        # Priority allocation (percentages of max_tokens)
        allocations = {
            'technical': int(max_tokens * 0.45),  # 45% for technical
            'project': int(max_tokens * 0.30),    # 30% for project state
            'conversation': int(max_tokens * 0.20), # 20% for flow
            'metadata': int(max_tokens * 0.05)    # 5% for metadata
        }
        
        compressed_parts = []
        
        # Compress each section
        if self.technical_context:
            compressed_parts.append(
                self._compress_section(
                    self.technical_context, 
                    allocations['technical'], 
                    encoder,
                    prefix="TECH:"
                )
            )
            
        if self.project_state:
            compressed_parts.append(
                self._compress_section(
                    self.project_state, 
                    allocations['project'], 
                    encoder,
                    prefix="STATE:"
                )
            )
            
        if self.conversation_flow:
            compressed_parts.append(
                self._compress_section(
                    self.conversation_flow, 
                    allocations['conversation'], 
                    encoder,
                    prefix="FLOW:"
                )
            )
            
        if self.metadata:
            compressed_parts.append(
                self._compress_section(
                    self.metadata, 
                    allocations['metadata'], 
                    encoder,
                    prefix="META:"
                )
            )
        
        return " | ".join(compressed_parts)
    
    def _compress_section(self, text: str, max_tokens: int, 
                         encoder, prefix: str = "") -> str:
        """Compress a section to fit within token limit"""
        if not text:
            return ""
            
        # Add prefix
        full_text = f"{prefix} {text}" if prefix else text
        
        # Tokenize
        tokens = encoder.encode(full_text)
        
        # Truncate if needed
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
            
        # Decode back to text
        return encoder.decode(tokens)


@dataclass
class HandoffContext:
    """Context for model handoff"""
    from_model: str
    to_model: str
    current_tokens: int
    predicted_tokens: int
    memory: ConversationMemory
    timestamp: datetime
    reason: str  # Why handoff was triggered
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'from_model': self.from_model,
            'to_model': self.to_model,
            'current_tokens': self.current_tokens,
            'predicted_tokens': self.predicted_tokens,
            'memory': asdict(self.memory),
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason
        }


class MemoryTransferManager:
    """Manages intelligent memory transfer between AI models"""
    
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.current_memory: Optional[ConversationMemory] = None
        self.handoff_history: List[HandoffContext] = []
        
    def get_context_window(self, model_id: str) -> int:
        """Get context window size for model"""
        # Try exact match
        if model_id in MODEL_CONTEXT_WINDOWS:
            return MODEL_CONTEXT_WINDOWS[model_id]
        
        # Try partial match (for Ollama models with versions)
        for key, value in MODEL_CONTEXT_WINDOWS.items():
            if key in model_id or model_id in key:
                return value
        
        # Default to conservative estimate
        return 4096
    
    def calculate_memory_budget(self, model_id: str) -> int:
        """Calculate token budget for memory transfer"""
        context_window = self.get_context_window(model_id)
        
        # 15% of context window
        budget = int(context_window * MEMORY_BUDGET_PERCENT)
        
        # Cap at max for efficiency
        budget = min(budget, MAX_MEMORY_TOKENS)
        
        # Ensure minimum for ultra-small models
        budget = max(budget, MIN_MEMORY_TOKENS)
        
        return budget
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def predict_response_tokens(self, prompt: str, 
                               context_history: List[str] = None) -> int:
        """
        Predict how many tokens the response will use
        Based on prompt complexity and historical patterns
        """
        prompt_tokens = self.count_tokens(prompt)
        
        # Heuristic: response is usually 1.5-2x prompt length for technical queries
        # For simple queries, it might be similar length
        
        # Check if prompt seems complex (code, technical terms, etc.)
        is_complex = any(keyword in prompt.lower() for keyword in [
            'code', 'function', 'class', 'implement', 'debug', 'error',
            'algorithm', 'optimize', 'explain', 'how to'
        ])
        
        if is_complex:
            # Complex queries get longer responses
            predicted = int(prompt_tokens * 2.0)
        else:
            # Simple queries get similar-length responses
            predicted = int(prompt_tokens * 1.2)
        
        # Add buffer for safety
        predicted = int(predicted * 1.2)
        
        # Cap at reasonable maximum
        return min(predicted, 2048)
    
    def should_handoff(self, current_model: str, current_tokens: int,
                      next_prompt: str) -> Tuple[bool, int, str]:
        """
        Determine if we should trigger a handoff
        
        Returns:
            (should_handoff, predicted_total, reason)
        """
        context_window = self.get_context_window(current_model)
        predicted_response = self.predict_response_tokens(next_prompt)
        predicted_total = current_tokens + predicted_response
        
        usage_percent = predicted_total / context_window
        
        if usage_percent >= HANDOFF_THRESHOLD:
            reason = f"Predicted {usage_percent*100:.1f}% usage ({predicted_total}/{context_window} tokens)"
            return True, predicted_total, reason
        
        return False, predicted_total, ""
    
    def extract_memory(self, conversation_history: List[Dict],
                      technical_files: List[str] = None,
                      project_context: str = None) -> ConversationMemory:
        """
        Extract essential memory from conversation history
        """
        # Extract technical context
        technical_parts = []
        if technical_files:
            technical_parts.extend(technical_files[:3])  # Last 3 files
        
        # Extract code and technical discussions from history
        for msg in conversation_history[-10:]:  # Last 10 messages
            content = msg.get('content', '')
            if any(keyword in content.lower() for keyword in [
                'code', 'function', 'class', 'error', 'bug', 'implement'
            ]):
                technical_parts.append(content[:200])  # First 200 chars
        
        technical_context = " | ".join(technical_parts)
        
        # Extract project state
        project_state = project_context or ""
        if conversation_history:
            # Look for project-related messages
            for msg in conversation_history[-5:]:
                content = msg.get('content', '')
                if any(keyword in content.lower() for keyword in [
                    'project', 'goal', 'implement', 'feature', 'task'
                ]):
                    project_state += f" {content[:150]}"
        
        # Extract conversation flow (recent messages)
        flow_parts = []
        for msg in conversation_history[-3:]:  # Last 3 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')[:100]  # First 100 chars
            flow_parts.append(f"{role}: {content}")
        
        conversation_flow = " | ".join(flow_parts)
        
        # Metadata
        metadata = f"msgs:{len(conversation_history)}"
        
        return ConversationMemory(
            technical_context=technical_context,
            project_state=project_state,
            conversation_flow=conversation_flow,
            metadata=metadata
        )
    
    def compress_memory(self, memory: ConversationMemory, 
                       target_model: str) -> str:
        """
        Compress memory for target model
        """
        budget = self.calculate_memory_budget(target_model)
        compressed = memory.to_compressed_string(budget)
        
        # Verify it fits
        actual_tokens = self.count_tokens(compressed)
        if actual_tokens > budget:
            # Emergency compression - just take first N tokens
            tokens = self.encoder.encode(compressed)[:budget]
            compressed = self.encoder.decode(tokens)
        
        return compressed
    
    def generate_handoff_prompt(self, memory: ConversationMemory,
                               target_model: str,
                               new_prompt: str) -> str:
        """
        Generate transfer prompt for next model
        """
        compressed_memory = self.compress_memory(memory, target_model)
        memory_tokens = self.count_tokens(compressed_memory)
        
        # Create handoff instruction
        handoff_prompt = (
            f"[CONTEXT: {compressed_memory}]\n\n"
            f"Continuing conversation. {new_prompt}"
        )
        
        return handoff_prompt
    
    def execute_handoff(self, from_model: str, to_model: str,
                       current_tokens: int, predicted_tokens: int,
                       conversation_history: List[Dict],
                       new_prompt: str,
                       technical_files: List[str] = None,
                       project_context: str = None) -> Tuple[str, HandoffContext]:
        """
        Execute a complete handoff sequence
        
        Returns:
            (transfer_prompt, handoff_context)
        """
        # Extract memory
        memory = self.extract_memory(
            conversation_history,
            technical_files,
            project_context
        )
        
        # Generate transfer prompt
        transfer_prompt = self.generate_handoff_prompt(
            memory, to_model, new_prompt
        )
        
        # Create handoff context
        handoff = HandoffContext(
            from_model=from_model,
            to_model=to_model,
            current_tokens=current_tokens,
            predicted_tokens=predicted_tokens,
            memory=memory,
            timestamp=datetime.now(),
            reason="Predictive handoff to prevent token overflow"
        )
        
        # Store in history
        self.handoff_history.append(handoff)
        self.current_memory = memory
        
        return transfer_prompt, handoff
    
    def get_handoff_stats(self) -> Dict:
        """Get statistics about handoffs"""
        if not self.handoff_history:
            return {
                'total_handoffs': 0,
                'avg_tokens_saved': 0,
                'models_used': []
            }
        
        total_handoffs = len(self.handoff_history)
        models_used = list(set(
            [h.from_model for h in self.handoff_history] +
            [h.to_model for h in self.handoff_history]
        ))
        
        # Calculate tokens saved (avoided overflow)
        tokens_saved = []
        for handoff in self.handoff_history:
            from_window = self.get_context_window(handoff.from_model)
            saved = from_window - handoff.current_tokens
            tokens_saved.append(saved)
        
        avg_saved = sum(tokens_saved) / len(tokens_saved) if tokens_saved else 0
        
        return {
            'total_handoffs': total_handoffs,
            'avg_tokens_saved': int(avg_saved),
            'models_used': models_used,
            'latest_handoff': self.handoff_history[-1].to_dict() if self.handoff_history else None
        }
    
    def format_handoff_summary(self, handoff: HandoffContext) -> str:
        """Format a nice summary of handoff"""
        from_window = self.get_context_window(handoff.from_model)
        to_window = self.get_context_window(handoff.to_model)
        usage_pct = (handoff.current_tokens / from_window) * 100
        
        compressed_size = self.count_tokens(
            self.compress_memory(handoff.memory, handoff.to_model)
        )
        
        return f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    🔄 MODEL HANDOFF EXECUTED                        ║
╚══════════════════════════════════════════════════════════════════════╝

From Model: {handoff.from_model}
  └─ Context Window: {from_window:,} tokens
  └─ Current Usage: {handoff.current_tokens:,} tokens ({usage_pct:.1f}%)
  └─ Predicted: +{handoff.predicted_tokens - handoff.current_tokens:,} tokens → {usage_pct + ((handoff.predicted_tokens - handoff.current_tokens)/from_window)*100:.1f}%

To Model: {handoff.to_model}
  └─ Context Window: {to_window:,} tokens
  └─ Memory Compressed: {compressed_size} tokens
  └─ Reason: {handoff.reason}

✅ Seamless transition with context preservation
""".strip()


def main():
    """Demo of memory transfer system"""
    manager = MemoryTransferManager()
    
    # Simulate conversation
    conversation_history = [
        {"role": "user", "content": "I'm working on a Python API using FastAPI"},
        {"role": "assistant", "content": "Great! FastAPI is excellent for building APIs..."},
        {"role": "user", "content": "How do I implement authentication?"},
        {"role": "assistant", "content": "For authentication in FastAPI, you can use OAuth2..."},
    ]
    
    # Simulate current state
    current_model = "meta-llama/llama-3.2-3b-instruct:free"
    current_tokens = 1600  # Example
    next_prompt = "Can you show me a complete example with JWT tokens?"
    
    # Check if handoff needed
    should_handoff, predicted, reason = manager.should_handoff(
        current_model, current_tokens, next_prompt
    )
    
    if should_handoff:
        print(f"⚠️  Handoff Triggered: {reason}\n")
        
        # Execute handoff
        transfer_prompt, handoff = manager.execute_handoff(
            from_model=current_model,
            to_model="deepseek/deepseek-r1:free",  # Larger context window
            current_tokens=current_tokens,
            predicted_tokens=predicted,
            conversation_history=conversation_history,
            new_prompt=next_prompt,
            project_context="Building FastAPI authentication system"
        )
        
        # Show summary
        print(manager.format_handoff_summary(handoff))
        
        print(f"\n📝 Transfer Prompt Preview:")
        print(f"{transfer_prompt[:200]}...")
        
        # Show stats
        stats = manager.get_handoff_stats()
        print(f"\n📊 Handoff Statistics:")
        print(json.dumps(stats, indent=2, default=str))
    else:
        print(f"✅ No handoff needed. Predicted usage: {(predicted/manager.get_context_window(current_model))*100:.1f}%")


if __name__ == "__main__":
    main()
