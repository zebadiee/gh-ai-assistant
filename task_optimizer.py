#!/usr/bin/env python3
"""
Task-Specific Model Optimization
Adds multi-neuron support - different models excel at different tasks
Like one voice with specialized neural pathways for different cognitive functions
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re

@dataclass
class TaskProfile:
    """Profile for a specific task type"""
    name: str
    keywords: List[str]
    preferred_models: List[str]
    description: str
    weight_adjustments: Dict[str, float]  # Adjust scoring weights for this task


# Task-specific model preferences (one voice, multi-neuron specialization)
TASK_PROFILES = {
    "coding_interview": TaskProfile(
        name="Coding Interview",
        keywords=["algorithm", "complexity", "o(n)", "o(1)", "leetcode", "implement", 
                 "function", "class", "sorting", "array", "tree", "graph",
                 "dynamic programming", "recursion", "interview", "coding challenge",
                 "solve", "problem", "write a function", "consecutive", "sequence",
                 "binary search", "hash", "linked list", "time complexity", "space complexity"],
        preferred_models=[
            "deepseek/deepseek-r1:free",  # Excellent for reasoning and code
            "meta-llama/llama-3.2-3b-instruct:free",  # Good code generation
            "google/gemini-2.0-flash-exp:free"  # Fast for simple coding tasks
        ],
        description="Coding interviews, algorithms, data structures",
        weight_adjustments={
            "error_rate": 50,  # Accuracy is critical
            "consecutive_failures": 30,
            "latency": 10,  # Can wait for quality
            "usage": 10
        }
    ),
    
    "system_design": TaskProfile(
        name="System Design",
        keywords=["architecture", "scalability", "distributed", "microservices",
                 "database design", "API design", "load balancing", "caching",
                 "design system", "high availability", "fault tolerance"],
        preferred_models=[
            "deepseek/deepseek-r1:free",  # Best for complex reasoning
            "google/gemini-2.0-flash-exp:free",  # Good for explanations
            "meta-llama/llama-3.2-3b-instruct:free"
        ],
        description="System design, architecture discussions",
        weight_adjustments={
            "error_rate": 45,
            "consecutive_failures": 25,
            "latency": 15,  # Can take time for complex designs
            "usage": 15
        }
    ),
    
    "quick_question": TaskProfile(
        name="Quick Question",
        keywords=["what is", "define", "explain briefly", "quick", "simple",
                 "tell me", "how do i", "?"],
        preferred_models=[
            "google/gemini-2.0-flash-exp:free",  # Fastest
            "mistralai/mistral-7b-instruct:free",  # Fast and accurate
            "meta-llama/llama-3.2-3b-instruct:free"
        ],
        description="Quick factual questions, definitions",
        weight_adjustments={
            "error_rate": 35,
            "consecutive_failures": 25,
            "latency": 30,  # Speed matters here
            "usage": 10
        }
    ),
    
    "code_review": TaskProfile(
        name="Code Review",
        keywords=["review", "improve", "optimize", "refactor", "bug",
                 "best practices", "code smell", "clean code", "analyze"],
        preferred_models=[
            "deepseek/deepseek-r1:free",  # Best reasoning
            "meta-llama/llama-3.2-3b-instruct:free",
            "google/gemini-2.0-flash-exp:free"
        ],
        description="Code review, refactoring suggestions",
        weight_adjustments={
            "error_rate": 45,
            "consecutive_failures": 30,
            "latency": 15,
            "usage": 10
        }
    ),
    
    "conversation": TaskProfile(
        name="Conversation",
        keywords=["hi", "hello", "thanks", "tell me about", "chat", "discuss",
                 "conversation", "talk"],
        preferred_models=[
            "meta-llama/llama-3.2-3b-instruct:free",  # Natural conversation
            "google/gemini-2.0-flash-exp:free",
            "mistralai/mistral-7b-instruct:free"
        ],
        description="Natural conversation, general chat",
        weight_adjustments={
            "error_rate": 30,
            "consecutive_failures": 20,
            "latency": 25,  # Want responsiveness
            "usage": 25
        }
    ),
    
    "math_reasoning": TaskProfile(
        name="Math & Reasoning",
        keywords=["prove", "mathematical", "theorem", "equation", "calculate",
                 "probability", "statistics", "logic", "reasoning"],
        preferred_models=[
            "deepseek/deepseek-r1:free",  # Excellent reasoning
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.2-3b-instruct:free"
        ],
        description="Mathematical reasoning, proofs",
        weight_adjustments={
            "error_rate": 50,  # Accuracy critical
            "consecutive_failures": 30,
            "latency": 10,
            "usage": 10
        }
    )
}


class TaskClassifier:
    """Classify user prompts into task types for specialized model selection"""
    
    def __init__(self):
        self.profiles = TASK_PROFILES
        
    def classify(self, prompt: str) -> Optional[TaskProfile]:
        """
        Classify a prompt into a task type
        Returns the best matching TaskProfile or None for general tasks
        """
        prompt_lower = prompt.lower()
        
        # Score each task profile
        scores = {}
        for task_type, profile in self.profiles.items():
            score = 0
            for keyword in profile.keywords:
                if keyword in prompt_lower:
                    score += 1
            
            # Bonus for exact phrase matches
            if any(kw in prompt_lower for kw in profile.keywords[:3]):
                score += 2
                
            if score > 0:
                scores[task_type] = score
        
        if not scores:
            return None
            
        # Return highest scoring profile
        best_task = max(scores.items(), key=lambda x: x[1])
        
        # Only return if confidence is high enough
        if best_task[1] >= 1:
            return self.profiles[best_task[0]]
        
        return None
    
    def get_optimized_scoring(self, prompt: str) -> Dict[str, float]:
        """
        Get task-optimized scoring weights for a prompt
        Returns adjusted weights or defaults
        """
        profile = self.classify(prompt)
        
        if profile:
            return profile.weight_adjustments
        
        # Default weights
        return {
            "error_rate": 40,
            "consecutive_failures": 30,
            "latency": 20,
            "usage": 10
        }
    
    def get_preferred_models(self, prompt: str) -> Optional[List[str]]:
        """
        Get preferred models for a prompt based on task type
        Returns model IDs in priority order, or None for default selection
        """
        profile = self.classify(prompt)
        
        if profile:
            return profile.preferred_models
        
        return None
    
    def explain_selection(self, prompt: str) -> str:
        """
        Explain why certain models are preferred for this prompt
        """
        profile = self.classify(prompt)
        
        if profile:
            return (f"🎯 Detected task: {profile.name}\n"
                   f"   {profile.description}\n"
                   f"   Optimized for: {', '.join(profile.keywords[:3])}")
        
        return "🔍 General task - using default model selection"


class MultiNeuronSelector:
    """
    Enhanced model selector with task-specific optimization
    Like one voice with multiple specialized neural pathways
    """
    
    def __init__(self, monitor, free_models, token_manager):
        from model_monitor import SmartModelSelector
        
        self.base_selector = SmartModelSelector(monitor, free_models, token_manager)
        self.classifier = TaskClassifier()
        self.monitor = monitor
        self.free_models = free_models
        self.token_manager = token_manager
        
    def select_model(self, prompt: str, explain: bool = False) -> str:
        """
        Select optimal model based on task type
        
        Args:
            prompt: User's prompt
            explain: If True, print explanation of selection
            
        Returns:
            Model ID to use
        """
        # Classify the task
        task_weights = self.classifier.get_optimized_scoring(prompt)
        preferred_models = self.classifier.get_preferred_models(prompt)
        
        if explain:
            explanation = self.classifier.explain_selection(prompt)
            print(explanation)
        
        # Get today's usage
        today_usage = {}
        for model in self.free_models:
            model_id = model['id']
            requests, tokens = self.token_manager.get_today_usage(model_id)
            today_usage[model_id] = (requests, tokens)
        
        # If we have preferred models for this task, try them first
        if preferred_models:
            for model_id in preferred_models:
                # Check if model is available
                model_info = next((m for m in self.free_models if m['id'] == model_id), None)
                if not model_info:
                    continue
                
                requests, _ = today_usage.get(model_id, (0, 0))
                
                # Skip if at limit
                if requests >= model_info['daily_limit']:
                    continue
                
                # Check performance
                stats = self.monitor.get_model_stats(model_id)
                
                # Skip if too many failures
                if stats['consecutive_failures'] >= 3:
                    continue
                
                # This preferred model is available
                if explain:
                    print(f"   ✓ Selected: {model_info['name']}")
                
                return model_id
        
        # Fall back to default selection
        if explain:
            print("   ℹ️  Preferred models unavailable, using best available")
        
        best = self.monitor.get_best_model(
            self.free_models,
            today_usage,
            exclude_models=self.base_selector.failed_models
        )
        
        if best:
            return best['model']['id']
        
        # Last resort: any available model
        for model in self.free_models:
            model_id = model['id']
            requests, _ = today_usage.get(model_id, (0, 0))
            if requests < model['daily_limit']:
                return model_id
        
        return None
    
    def mark_failure(self, model_id: str, error_type: str = None):
        """Pass through to base selector"""
        self.base_selector.mark_failure(model_id, error_type)
    
    def clear_failures(self):
        """Pass through to base selector"""
        self.base_selector.clear_failures()


def main():
    """Demo of task-specific model selection"""
    classifier = TaskClassifier()
    
    test_prompts = [
        "Solve this LeetCode problem: find longest consecutive sequence",
        "Design a distributed cache system with high availability",
        "What is Python?",
        "Review my code and suggest improvements",
        "Hi, I'd like to chat about programming",
        "Prove that the sum of angles in a triangle equals 180 degrees"
    ]
    
    print("="*80)
    print("🧠 MULTI-NEURON MODEL SELECTION DEMO")
    print("="*80)
    print("\nDemonstrating task-specific model optimization:\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"{i}. Prompt: \"{prompt}\"")
        print("-" * 80)
        
        profile = classifier.classify(prompt)
        if profile:
            print(f"   Task Type: {profile.name}")
            print(f"   Description: {profile.description}")
            print(f"   Preferred Models:")
            for j, model in enumerate(profile.preferred_models, 1):
                print(f"      {j}. {model}")
            print(f"   Scoring Weights: {profile.weight_adjustments}")
        else:
            print("   Task Type: General (default selection)")
        
        print()
    
    print("="*80)
    print("💡 This is like one voice with multiple specialized neural pathways:")
    print("   • Coding interviews → DeepSeek (best reasoning)")
    print("   • Quick questions → Gemini (fastest)")
    print("   • Conversations → Llama (most natural)")
    print("="*80)


if __name__ == "__main__":
    main()
