#!/usr/bin/env python3
"""
API Key Management System - BYOK (Bring Your Own Key)
Easy setup wizard for finding, registering, and managing API keys
"""

import os
import sys
import json
import keyring
from pathlib import Path
from typing import Dict, List, Optional
import webbrowser

CONFIG_DIR = Path.home() / ".gh-ai-assistant"
KEYRING_SERVICE = "gh-ai-assistant"

# Provider information with links and instructions
PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter",
        "description": "Access to 100+ models including all major providers",
        "signup_url": "https://openrouter.ai/keys",
        "docs_url": "https://openrouter.ai/docs",
        "free_tier": "Yes - Many free models available",
        "key_format": "sk-or-...",
        "instructions": [
            "1. Visit https://openrouter.ai/keys",
            "2. Sign up or log in with GitHub/Google",
            "3. Click 'Create Key'",
            "4. Copy the API key (starts with 'sk-or-')",
            "5. Paste it below"
        ],
        "benefits": [
            "51+ free models available",
            "Auto-fallback between providers",
            "Usage tracking and credits",
            "Access to GPT-4, Claude, Gemini, etc."
        ]
    },
    "openai": {
        "name": "OpenAI",
        "description": "GPT-4, GPT-3.5, and other OpenAI models",
        "signup_url": "https://platform.openai.com/api-keys",
        "docs_url": "https://platform.openai.com/docs",
        "free_tier": "Trial credits ($5)",
        "key_format": "sk-...",
        "instructions": [
            "1. Visit https://platform.openai.com/api-keys",
            "2. Sign up or log in",
            "3. Click 'Create new secret key'",
            "4. Name it (e.g., 'gh-ai-assistant')",
            "5. Copy the key (starts with 'sk-')",
            "6. Paste it below"
        ],
        "benefits": [
            "GPT-4 Turbo, GPT-3.5",
            "Function calling",
            "High quality outputs",
            "Well-documented"
        ]
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "description": "Claude 3 Opus, Sonnet, and Haiku models",
        "signup_url": "https://console.anthropic.com/account/keys",
        "docs_url": "https://docs.anthropic.com/",
        "free_tier": "Trial credits",
        "key_format": "sk-ant-...",
        "instructions": [
            "1. Visit https://console.anthropic.com/account/keys",
            "2. Sign up or log in",
            "3. Request API access (may require waitlist)",
            "4. Click 'Create Key'",
            "5. Copy the key (starts with 'sk-ant-')",
            "6. Paste it below"
        ],
        "benefits": [
            "Claude 3 Opus (best reasoning)",
            "Long context windows (200k tokens)",
            "Constitutional AI (safer)",
            "Excellent coding abilities"
        ]
    },
    "huggingface": {
        "name": "Hugging Face",
        "description": "Open source models and inference API",
        "signup_url": "https://huggingface.co/settings/tokens",
        "docs_url": "https://huggingface.co/docs/api-inference/",
        "free_tier": "Yes - Free tier available",
        "key_format": "hf_...",
        "instructions": [
            "1. Visit https://huggingface.co/settings/tokens",
            "2. Sign up or log in",
            "3. Click 'New token'",
            "4. Select 'read' permissions",
            "5. Copy the token (starts with 'hf_')",
            "6. Paste it below"
        ],
        "benefits": [
            "Thousands of open models",
            "Free inference API",
            "Community-driven",
            "Fine-tuned models available"
        ]
    },
    "groq": {
        "name": "Groq",
        "description": "Ultra-fast inference with LPU hardware",
        "signup_url": "https://console.groq.com/keys",
        "docs_url": "https://console.groq.com/docs",
        "free_tier": "Yes - Generous free tier",
        "key_format": "gsk_...",
        "instructions": [
            "1. Visit https://console.groq.com/keys",
            "2. Sign up or log in",
            "3. Click 'Create API Key'",
            "4. Copy the key (starts with 'gsk_')",
            "5. Paste it below"
        ],
        "benefits": [
            "Ultra-fast responses (500+ tokens/sec)",
            "Llama 3, Mixtral models",
            "Free tier: 14,400 requests/day",
            "Low latency"
        ]
    },
    "together": {
        "name": "Together AI",
        "description": "Fast inference for open source models",
        "signup_url": "https://api.together.xyz/settings/api-keys",
        "docs_url": "https://docs.together.ai/",
        "free_tier": "Free trial credits",
        "key_format": "...",
        "instructions": [
            "1. Visit https://api.together.xyz/settings/api-keys",
            "2. Sign up or log in",
            "3. Click 'Create new API key'",
            "4. Copy the key",
            "5. Paste it below"
        ],
        "benefits": [
            "50+ open source models",
            "Fast inference",
            "Competitive pricing",
            "Fine-tuning support"
        ]
    },
    "replicate": {
        "name": "Replicate",
        "description": "Run ML models in the cloud",
        "signup_url": "https://replicate.com/account/api-tokens",
        "docs_url": "https://replicate.com/docs",
        "free_tier": "Free trial credits",
        "key_format": "r8_...",
        "instructions": [
            "1. Visit https://replicate.com/account/api-tokens",
            "2. Sign up or log in",
            "3. Copy your default token or create new",
            "4. Paste it below"
        ],
        "benefits": [
            "Easy deployment",
            "Image, video, audio models",
            "Version control for models",
            "No GPU setup needed"
        ]
    },
    "perplexity": {
        "name": "Perplexity AI",
        "description": "AI search and question answering",
        "signup_url": "https://www.perplexity.ai/settings/api",
        "docs_url": "https://docs.perplexity.ai/",
        "free_tier": "Limited free tier",
        "key_format": "pplx-...",
        "instructions": [
            "1. Visit https://www.perplexity.ai/settings/api",
            "2. Sign up or log in",
            "3. Generate API key",
            "4. Copy the key (starts with 'pplx-')",
            "5. Paste it below"
        ],
        "benefits": [
            "Search-augmented AI",
            "Real-time web access",
            "Citation tracking",
            "Up-to-date information"
        ]
    }
}


class APIKeyManager:
    """Manages API keys for multiple providers"""
    
    def __init__(self):
        self.keyring_service = KEYRING_SERVICE
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    def save_key(self, provider: str, api_key: str):
        """Save API key securely to keyring"""
        keyring.set_password(self.keyring_service, f"{provider}_api_key", api_key)
        print(f"✅ {provider.title()} API key saved securely")
        
    def get_key(self, provider: str) -> Optional[str]:
        """Retrieve API key from keyring"""
        return keyring.get_password(self.keyring_service, f"{provider}_api_key")
        
    def delete_key(self, provider: str):
        """Delete API key from keyring"""
        try:
            keyring.delete_password(self.keyring_service, f"{provider}_api_key")
            print(f"✅ {provider.title()} API key deleted")
        except:
            print(f"⚠️  No key found for {provider}")
            
    def list_configured_providers(self) -> List[str]:
        """List providers with configured keys"""
        configured = []
        for provider in PROVIDERS.keys():
            if self.get_key(provider):
                configured.append(provider)
        return configured
        
    def validate_key_format(self, provider: str, key: str) -> bool:
        """Basic validation of key format"""
        expected = PROVIDERS[provider].get("key_format", "")
        
        if not key or len(key) < 10:
            return False
            
        # Check prefix if specified
        if expected and expected.endswith("..."):
            prefix = expected.replace("...", "")
            if not key.startswith(prefix):
                print(f"⚠️  Warning: Key should start with '{prefix}'")
                return True  # Warning only, still accept
                
        return True


def print_header(text: str):
    """Print formatted header"""
    width = 70
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def print_provider_info(provider_id: str):
    """Display detailed provider information"""
    provider = PROVIDERS[provider_id]
    
    print(f"\n📋 {provider['name']}")
    print("-" * 70)
    print(f"Description: {provider['description']}")
    print(f"Free Tier: {provider['free_tier']}")
    print(f"Key Format: {provider['key_format']}")
    print()
    print("✨ Benefits:")
    for benefit in provider['benefits']:
        print(f"   • {benefit}")
    print()
    print("📝 Setup Instructions:")
    for instruction in provider['instructions']:
        print(f"   {instruction}")
    print()
    print(f"🔗 Sign up: {provider['signup_url']}")
    print(f"📚 Docs: {provider['docs_url']}")
    print("-" * 70)


def interactive_setup():
    """Interactive API key setup wizard"""
    manager = APIKeyManager()
    
    print_header("🔑 API KEY SETUP WIZARD")
    print("Welcome! This wizard will help you set up API keys for AI providers.")
    print()
    
    # Show current status
    configured = manager.list_configured_providers()
    if configured:
        print(f"✅ You have {len(configured)} provider(s) configured:")
        for provider in configured:
            print(f"   • {PROVIDERS[provider]['name']}")
        print()
    else:
        print("ℹ️  No API keys configured yet.")
        print()
    
    # Main menu
    while True:
        print("\nWhat would you like to do?")
        print("1. Add new API key")
        print("2. View provider information")
        print("3. List configured providers")
        print("4. Remove API key")
        print("5. Test API keys")
        print("6. Open signup pages in browser")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == "0":
            print("\n✅ Setup complete! Your keys are saved securely.")
            break
            
        elif choice == "1":
            add_api_key_wizard(manager)
            
        elif choice == "2":
            view_provider_info()
            
        elif choice == "3":
            list_providers(manager)
            
        elif choice == "4":
            remove_api_key(manager)
            
        elif choice == "5":
            test_api_keys(manager)
            
        elif choice == "6":
            open_signup_pages()
            
        else:
            print("❌ Invalid choice. Please try again.")


def add_api_key_wizard(manager: APIKeyManager):
    """Wizard for adding a new API key"""
    print_header("➕ ADD NEW API KEY")
    
    # Show available providers
    print("Available providers:\n")
    for i, (provider_id, info) in enumerate(PROVIDERS.items(), 1):
        status = "✅" if manager.get_key(provider_id) else "  "
        print(f"{status} {i}. {info['name']} - {info['description']}")
    
    print(f"\n   0. Cancel")
    
    choice = input("\nSelect provider (0-{}): ".format(len(PROVIDERS))).strip()
    
    if choice == "0":
        return
        
    try:
        idx = int(choice) - 1
        provider_id = list(PROVIDERS.keys())[idx]
    except (ValueError, IndexError):
        print("❌ Invalid selection")
        return
    
    provider = PROVIDERS[provider_id]
    
    # Show provider details
    print_provider_info(provider_id)
    
    # Ask if user wants to open signup page
    open_page = input("\n🌐 Open signup page in browser? (y/n): ").strip().lower()
    if open_page == 'y':
        webbrowser.open(provider['signup_url'])
        print(f"✅ Opened {provider['signup_url']} in your browser")
    
    # Get API key
    print(f"\n🔑 Enter your {provider['name']} API key")
    print("   (or press Enter to skip)")
    api_key = input("   Key: ").strip()
    
    if not api_key:
        print("⏭️  Skipped")
        return
    
    # Validate format
    if not manager.validate_key_format(provider_id, api_key):
        retry = input("⚠️  Key format looks incorrect. Save anyway? (y/n): ").strip().lower()
        if retry != 'y':
            return
    
    # Save key
    manager.save_key(provider_id, api_key)
    print(f"\n✅ {provider['name']} API key saved successfully!")
    
    # Suggest next steps
    if provider_id == "openrouter":
        print("\n💡 Tip: OpenRouter gives you access to 51+ free models!")
        print("   Run 'python gh_ai_core.py models' to see them all")


def view_provider_info():
    """View detailed information about providers"""
    print_header("📋 PROVIDER INFORMATION")
    
    print("Select provider to view details:\n")
    for i, (provider_id, info) in enumerate(PROVIDERS.items(), 1):
        print(f"{i}. {info['name']}")
    
    print(f"\n0. Back")
    
    choice = input(f"\nSelect provider (0-{len(PROVIDERS)}): ").strip()
    
    if choice == "0":
        return
        
    try:
        idx = int(choice) - 1
        provider_id = list(PROVIDERS.keys())[idx]
        print_provider_info(provider_id)
        input("\nPress Enter to continue...")
    except (ValueError, IndexError):
        print("❌ Invalid selection")


def list_providers(manager: APIKeyManager):
    """List all providers and their configuration status"""
    print_header("📊 PROVIDER STATUS")
    
    for provider_id, info in PROVIDERS.items():
        configured = manager.get_key(provider_id) is not None
        status = "✅ Configured" if configured else "⚪ Not configured"
        
        print(f"{status} - {info['name']}")
        print(f"           {info['description']}")
        print(f"           Free tier: {info['free_tier']}")
        print()
    
    input("Press Enter to continue...")


def remove_api_key(manager: APIKeyManager):
    """Remove an API key"""
    print_header("🗑️  REMOVE API KEY")
    
    configured = manager.list_configured_providers()
    
    if not configured:
        print("ℹ️  No API keys configured.")
        return
    
    print("Configured providers:\n")
    for i, provider_id in enumerate(configured, 1):
        print(f"{i}. {PROVIDERS[provider_id]['name']}")
    
    print("\n0. Cancel")
    
    choice = input(f"\nSelect provider to remove (0-{len(configured)}): ").strip()
    
    if choice == "0":
        return
        
    try:
        idx = int(choice) - 1
        provider_id = configured[idx]
        
        confirm = input(f"\n⚠️  Remove {PROVIDERS[provider_id]['name']} API key? (y/n): ").strip().lower()
        if confirm == 'y':
            manager.delete_key(provider_id)
    except (ValueError, IndexError):
        print("❌ Invalid selection")


def test_api_keys(manager: APIKeyManager):
    """Test configured API keys"""
    print_header("🧪 TEST API KEYS")
    
    configured = manager.list_configured_providers()
    
    if not configured:
        print("ℹ️  No API keys to test.")
        return
    
    print("Testing configured providers...\n")
    
    for provider_id in configured:
        key = manager.get_key(provider_id)
        provider = PROVIDERS[provider_id]
        
        print(f"Testing {provider['name']}...", end=" ")
        
        # Basic format check
        if manager.validate_key_format(provider_id, key):
            print("✅ Format OK")
        else:
            print("⚠️  Format warning")
    
    print("\n💡 Tip: Run actual requests to fully test API keys")
    input("\nPress Enter to continue...")


def open_signup_pages():
    """Open all signup pages in browser"""
    print_header("🌐 OPEN SIGNUP PAGES")
    
    print("This will open signup pages for all providers in your browser.\n")
    
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        return
    
    print("\nOpening pages...\n")
    for provider_id, info in PROVIDERS.items():
        print(f"Opening {info['name']}...")
        webbrowser.open(info['signup_url'])
    
    print(f"\n✅ Opened {len(PROVIDERS)} signup pages")
    input("\nPress Enter to continue...")


def quick_setup(provider: str = "openrouter"):
    """Quick setup for a specific provider"""
    manager = APIKeyManager()
    
    print_header(f"🚀 QUICK SETUP - {PROVIDERS[provider]['name']}")
    
    print_provider_info(provider)
    
    # Open signup page
    print(f"\n🌐 Opening signup page...")
    webbrowser.open(PROVIDERS[provider]['signup_url'])
    
    # Get key
    print(f"\n🔑 After signing up, paste your API key below:")
    api_key = input("   Key: ").strip()
    
    if api_key and manager.validate_key_format(provider, api_key):
        manager.save_key(provider, api_key)
        print(f"\n✅ Setup complete! You can now use {PROVIDERS[provider]['name']}")
    else:
        print("\n⚠️  Setup cancelled or invalid key")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick" and len(sys.argv) > 2:
            # Quick setup for specific provider
            provider = sys.argv[2]
            if provider in PROVIDERS:
                quick_setup(provider)
            else:
                print(f"❌ Unknown provider: {provider}")
                print(f"Available: {', '.join(PROVIDERS.keys())}")
        else:
            print("Usage:")
            print("  python api_keys.py              # Interactive wizard")
            print("  python api_keys.py quick <provider>  # Quick setup")
    else:
        # Interactive wizard
        interactive_setup()


if __name__ == "__main__":
    main()
