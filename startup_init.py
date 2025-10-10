#!/usr/bin/env python3
"""
Startup Initialization System
Ensures assistant is ready with:
- Latest free models refreshed
- Conversation storage initialized
- API keys configured
- All systems operational
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import subsystems
try:
    from model_refresh import refresh_free_models
    from conversation_store import ConversationStore
    from api_keys import APIKeyManager, PROVIDERS
    MODEL_SYSTEMS_AVAILABLE = True
except ImportError as e:
    MODEL_SYSTEMS_AVAILABLE = False
    print(f"⚠️  Import error: {e}")


class StartupInitializer:
    """
    Comprehensive startup initialization
    Prepares all systems before assistant becomes operational
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.checks_passed = []
        self.checks_failed = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log startup messages"""
        if self.verbose:
            emoji = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "WARNING": "⚠️ ",
                "ERROR": "❌",
                "PROGRESS": "🔄"
            }.get(level, "  ")
            print(f"{emoji} {message}")
    
    def run_check(self, name: str, check_func, critical: bool = False) -> bool:
        """
        Run a startup check
        
        Args:
            name: Name of the check
            check_func: Function to run
            critical: If True, failure will abort startup
            
        Returns:
            True if check passed
        """
        self.log(f"Running check: {name}", "PROGRESS")
        
        try:
            result = check_func()
            if result:
                self.checks_passed.append(name)
                self.log(f"{name}: OK", "SUCCESS")
                return True
            else:
                self.checks_failed.append(name)
                level = "ERROR" if critical else "WARNING"
                self.log(f"{name}: FAILED", level)
                if critical:
                    self.log("Critical check failed, aborting", "ERROR")
                    sys.exit(1)
                return False
        except Exception as e:
            self.checks_failed.append(name)
            level = "ERROR" if critical else "WARNING"
            self.log(f"{name}: FAILED - {e}", level)
            if critical:
                self.log("Critical check failed, aborting", "ERROR")
                sys.exit(1)
            return False
    
    def check_python_version(self) -> bool:
        """Ensure Python version is compatible"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"Python {version.major}.{version.minor}.{version.micro}", "INFO")
            return True
        else:
            self.log(f"Python {version.major}.{version.minor} is too old (need 3.8+)", "ERROR")
            return False
    
    def check_dependencies(self) -> bool:
        """Check required dependencies"""
        required = ['requests', 'keyring']
        missing = []
        
        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            self.log(f"Missing packages: {', '.join(missing)}", "ERROR")
            self.log("Install with: pip install " + " ".join(missing), "INFO")
            return False
        return True
    
    def refresh_models(self) -> bool:
        """Refresh free models from OpenRouter"""
        if not MODEL_SYSTEMS_AVAILABLE:
            self.log("Model refresh system not available", "WARNING")
            return False
            
        try:
            self.log("Fetching latest free models from OpenRouter...", "PROGRESS")
            models = refresh_free_models(force=False)  # Use cache if recent
            
            if models and len(models) > 0:
                self.log(f"Loaded {len(models)} free models", "SUCCESS")
                
                # Show top 3
                if self.verbose:
                    self.log("Top models:", "INFO")
                    for model in models[:3]:
                        print(f"   • {model['name']}")
                        
                return True
            else:
                self.log("No models loaded (using defaults)", "WARNING")
                return False
        except Exception as e:
            self.log(f"Model refresh failed: {e}", "WARNING")
            return False
    
    def init_conversation_store(self) -> bool:
        """Initialize conversation storage"""
        if not MODEL_SYSTEMS_AVAILABLE:
            self.log("Conversation store not available", "WARNING")
            return False
            
        try:
            store = ConversationStore()
            self.log("Conversation storage initialized", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Conversation store init failed: {e}", "WARNING")
            return False
    
    def check_api_keys(self) -> bool:
        """Check for configured API keys"""
        if not MODEL_SYSTEMS_AVAILABLE:
            self.log("API key manager not available", "WARNING")
            return False
            
        try:
            manager = APIKeyManager()
            configured = manager.list_configured_providers()
            
            if configured:
                self.log(f"API keys configured: {', '.join(configured)}", "SUCCESS")
                return True
            else:
                self.log("No API keys configured", "WARNING")
                self.log("Run 'python api_keys.py' to set up", "INFO")
                return False
        except Exception as e:
            self.log(f"API key check failed: {e}", "WARNING")
            return False
    
    def create_config_dirs(self) -> bool:
        """Ensure configuration directories exist"""
        try:
            config_dir = Path.home() / ".gh-ai-assistant"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Create cache directory
            cache_dir = config_dir / "cache"
            cache_dir.mkdir(exist_ok=True)
            
            self.log(f"Config directory: {config_dir}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to create config dirs: {e}", "ERROR")
            return False
    
    def print_banner(self):
        """Print startup banner"""
        if self.verbose:
            print()
            print("╔══════════════════════════════════════════════════════════════════════╗")
            print("║                                                                      ║")
            print("║              🤖 GitHub CLI AI Assistant v2.0                         ║")
            print("║              Initializing Systems...                                ║")
            print("║                                                                      ║")
            print("╚══════════════════════════════════════════════════════════════════════╝")
            print()
    
    def print_summary(self):
        """Print startup summary"""
        if self.verbose:
            print()
            print("=" * 70)
            print("STARTUP SUMMARY")
            print("=" * 70)
            print(f"✅ Passed: {len(self.checks_passed)}")
            print(f"⚠️  Failed: {len(self.checks_failed)}")
            
            if self.checks_failed:
                print("\nFailed checks (non-critical):")
                for check in self.checks_failed:
                    print(f"  • {check}")
            
            print()
            print("=" * 70)
            print("✅ System Ready")
            print("=" * 70)
            print()
    
    def initialize(self) -> bool:
        """
        Run full startup initialization
        
        Returns:
            True if startup successful
        """
        self.print_banner()
        
        # Critical checks (will abort if failed)
        self.run_check("Python Version", self.check_python_version, critical=True)
        self.run_check("Dependencies", self.check_dependencies, critical=True)
        self.run_check("Config Directories", self.create_config_dirs, critical=True)
        
        # Non-critical checks (warnings only)
        self.run_check("Free Models Refresh", self.refresh_models, critical=False)
        self.run_check("Conversation Storage", self.init_conversation_store, critical=False)
        self.run_check("API Keys", self.check_api_keys, critical=False)
        
        self.print_summary()
        
        return len(self.checks_failed) == 0


def quick_init(verbose: bool = False) -> bool:
    """
    Quick initialization for embedded use
    
    Args:
        verbose: Print initialization messages
        
    Returns:
        True if initialization successful
    """
    initializer = StartupInitializer(verbose=verbose)
    
    # Run only essential checks
    initializer.create_config_dirs()
    
    # Silently refresh models if available
    try:
        if MODEL_SYSTEMS_AVAILABLE:
            refresh_free_models(force=False)
            ConversationStore()  # Init DB
    except:
        pass
    
    return True


def main():
    """Interactive startup initialization"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GitHub AI Assistant Startup Initialization"
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (minimal output)'
    )
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force refresh of free models'
    )
    
    args = parser.parse_args()
    
    initializer = StartupInitializer(verbose=not args.quiet)
    
    # Override model refresh to force if requested
    if args.force_refresh:
        original_refresh = initializer.refresh_models
        def force_refresh_models():
            if MODEL_SYSTEMS_AVAILABLE:
                refresh_free_models(force=True)
                return True
            return False
        initializer.refresh_models = force_refresh_models
    
    # Run initialization
    success = initializer.initialize()
    
    # Exit with status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
