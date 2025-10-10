#!/usr/bin/env python3
"""
Assistant Context Manager
Manages personalized AI assistant context and behavior for gh-ai-assistant.

Allows you to configure assistant name, personality, and context preferences.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Optional


CONFIG_DIR = Path.home() / ".gh-ai-assistant"
CONTEXT_FILE = CONFIG_DIR / "assistant_context.json"


class AssistantContext:
    """Manages persistent assistant context and preferences"""
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.context_file = CONTEXT_FILE
        self._ensure_config_dir()
        self.context = self._load_context()
        
    def _ensure_config_dir(self):
        """Create config directory if needed"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_context(self) -> Dict:
        """Load existing context or create default"""
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                return json.load(f)
        
        # Default context
        return {
            "assistant_name": "Brakel",
            "user_name": "Declan",
            "project_context": "gh-ai-assistant - Enterprise-grade AI reliability system",
            "personality_traits": [
                "Professional coding partner",
                "Proactive problem solver",
                "Context-aware assistant",
                "Technical expert"
            ],
            "preferences": {
                "introduce_self": True,
                "maintain_context": True,
                "technical_focus": "Python, AI systems, FastAPI",
                "communication_style": "concise and professional"
            },
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
    def save_context(self):
        """Save context to file"""
        self.context['last_updated'] = datetime.now().isoformat()
        
        with open(self.context_file, 'w') as f:
            json.dump(self.context, indent=2, fp=f)
            
    def get_system_prompt(self) -> str:
        """Generate system prompt with context"""
        name = self.context.get('assistant_name', 'Assistant')
        user = self.context.get('user_name', 'User')
        project = self.context.get('project_context', 'gh-ai-assistant')
        traits = self.context.get('personality_traits', [])
        prefs = self.context.get('preferences', {})
        
        prompt = f"""You are {name}, {user}'s personal AI coding partner.

PROJECT CONTEXT:
{project}

YOUR ROLE:
{chr(10).join(f'- {trait}' for trait in traits)}

PREFERENCES:
- Technical Focus: {prefs.get('technical_focus', 'General development')}
- Communication: {prefs.get('communication_style', 'Professional')}
- Introduce yourself: {'Yes' if prefs.get('introduce_self') else 'No'}
- Maintain context: {'Yes' if prefs.get('maintain_context') else 'No'}

CURRENT SESSION:
- Working in: gh-ai-assistant repository
- Features: Memory Transfer, Memory Bridge, Token Optimization
- Goal: Build enterprise-grade AI reliability system
"""
        return prompt
        
    def get_greeting(self) -> str:
        """Get personalized greeting"""
        name = self.context.get('assistant_name', 'Assistant')
        user = self.context.get('user_name', 'User')
        
        return f"👋 Hello {user}, I'm {name} - your AI coding partner for gh-ai-assistant!"
        
    def update_context(self, **kwargs):
        """Update context fields"""
        for key, value in kwargs.items():
            if key in self.context:
                self.context[key] = value
            elif key in self.context.get('preferences', {}):
                self.context['preferences'][key] = value
                
        self.save_context()
        
    def display_context(self):
        """Display current context"""
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║              ASSISTANT CONTEXT CONFIGURATION                         ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print(f"Assistant Name: {self.context.get('assistant_name')}")
        print(f"User Name: {self.context.get('user_name')}")
        print(f"Project: {self.context.get('project_context')}")
        print()
        print("Personality Traits:")
        for trait in self.context.get('personality_traits', []):
            print(f"  • {trait}")
        print()
        print("Preferences:")
        for key, value in self.context.get('preferences', {}).items():
            print(f"  • {key}: {value}")
        print()
        print(f"Last Updated: {self.context.get('last_updated')}")
        print()


def main():
    """CLI for assistant context management"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage AI assistant context and preferences"
    )
    
    parser.add_argument('--show', action='store_true',
                       help='Display current context')
    parser.add_argument('--greeting', action='store_true',
                       help='Show personalized greeting')
    parser.add_argument('--prompt', action='store_true',
                       help='Generate system prompt')
    parser.add_argument('--set-name', metavar='NAME',
                       help='Set assistant name')
    parser.add_argument('--set-user', metavar='USER',
                       help='Set user name')
    parser.add_argument('--reset', action='store_true',
                       help='Reset to default context')
    
    args = parser.parse_args()
    
    context = AssistantContext()
    
    if args.show:
        context.display_context()
        
    elif args.greeting:
        print()
        print(context.get_greeting())
        print()
        
    elif args.prompt:
        print()
        print(context.get_system_prompt())
        print()
        
    elif args.set_name:
        context.update_context(assistant_name=args.set_name)
        print(f"✅ Assistant name set to: {args.set_name}")
        context.save_context()
        
    elif args.set_user:
        context.update_context(user_name=args.set_user)
        print(f"✅ User name set to: {args.set_user}")
        context.save_context()
        
    elif args.reset:
        context.context_file.unlink(missing_ok=True)
        print("✅ Context reset to defaults")
        context = AssistantContext()
        context.save_context()
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
