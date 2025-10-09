#!/usr/bin/env python3
"""
Validation script for GitHub CLI AI Assistant
Verifies all components are working correctly
"""

import os
import sys
import sqlite3
from pathlib import Path
import subprocess

def print_status(test_name, passed, message=""):
    """Print test status"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"      {message}")

def test_python_version():
    """Test Python version is 3.8+"""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 8
    print_status("Python Version", passed, f"Python {version.major}.{version.minor}.{version.micro}")
    return passed

def test_dependencies():
    """Test required dependencies are installed"""
    try:
        import requests
        import keyring
        print_status("Dependencies", True, "requests and keyring installed")
        return True
    except ImportError as e:
        print_status("Dependencies", False, f"Missing: {e}")
        return False

def test_module_import():
    """Test gh_ai_core module can be imported"""
    try:
        import gh_ai_core
        print_status("Module Import", True, "gh_ai_core.py loads successfully")
        return True
    except Exception as e:
        print_status("Module Import", False, str(e))
        return False

def test_directory_structure():
    """Test configuration directory can be created"""
    config_dir = Path.home() / ".gh-ai-assistant"
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        passed = config_dir.exists()
        print_status("Config Directory", passed, str(config_dir))
        return passed
    except Exception as e:
        print_status("Config Directory", False, str(e))
        return False

def test_database():
    """Test SQLite database operations"""
    try:
        db_path = Path.home() / ".gh-ai-assistant" / "test_validation.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
        cursor.execute("INSERT INTO test (value) VALUES ('test')")
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        conn.close()
        
        # Cleanup
        db_path.unlink()
        
        passed = result is not None
        print_status("Database Operations", passed, "SQLite working correctly")
        return passed
    except Exception as e:
        print_status("Database Operations", False, str(e))
        return False

def test_git_available():
    """Test git is available (for context extraction)"""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        passed = result.returncode == 0
        version = result.stdout.strip() if passed else "Not found"
        print_status("Git Installation", passed, version)
        return passed
    except Exception as e:
        print_status("Git Installation", False, "Git not found")
        return False

def test_keyring():
    """Test system keyring is accessible"""
    try:
        import keyring
        # Try to set and get a test value
        service = "gh-ai-assistant-test"
        keyring.set_password(service, "test", "test_value")
        value = keyring.get_password(service, "test")
        keyring.delete_password(service, "test")
        
        passed = value == "test_value"
        print_status("Keyring Access", passed, "System keyring accessible")
        return passed
    except Exception as e:
        print_status("Keyring Access", False, str(e))
        return False

def test_file_permissions():
    """Test file creation and execution permissions"""
    try:
        test_file = Path.home() / ".gh-ai-assistant" / "test_file.txt"
        test_file.write_text("test")
        content = test_file.read_text()
        test_file.unlink()
        
        passed = content == "test"
        print_status("File Permissions", passed, "Read/write working")
        return passed
    except Exception as e:
        print_status("File Permissions", False, str(e))
        return False

def test_network():
    """Test network connectivity to OpenRouter"""
    try:
        import requests
        response = requests.get("https://openrouter.ai", timeout=10)
        passed = response.status_code == 200
        print_status("Network Connectivity", passed, "Can reach OpenRouter")
        return passed
    except Exception as e:
        print_status("Network Connectivity", False, "Cannot reach OpenRouter")
        return False

def test_executable_scripts():
    """Test scripts are executable"""
    script_path = Path(__file__).parent / "gh-ai"
    try:
        passed = os.access(script_path, os.X_OK)
        print_status("Script Permissions", passed, f"{script_path.name} is executable")
        return passed
    except Exception as e:
        print_status("Script Permissions", False, str(e))
        return False

def test_component_initialization():
    """Test core components can be initialized"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from gh_ai_core import TokenManager, OpenRouterClient, GitHubContextExtractor
        
        # Test TokenManager
        manager = TokenManager()
        
        # Test OpenRouterClient (without making API calls)
        client = OpenRouterClient("test-key")
        
        # Test GitHubContextExtractor
        extractor = GitHubContextExtractor()
        
        print_status("Component Initialization", True, "All classes instantiate correctly")
        return True
    except Exception as e:
        print_status("Component Initialization", False, str(e))
        return False

def run_validation():
    """Run all validation tests"""
    print("🔍 GitHub CLI AI Assistant - Validation Suite\n")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Module Import", test_module_import),
        ("Directory Structure", test_directory_structure),
        ("Database Operations", test_database),
        ("Git Installation", test_git_available),
        ("Keyring Access", test_keyring),
        ("File Permissions", test_file_permissions),
        ("Network Connectivity", test_network),
        ("Script Permissions", test_executable_scripts),
        ("Component Initialization", test_component_initialization),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print_status(name, False, f"Unexpected error: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({percentage:.1f}%)\n")
    
    if passed == total:
        print("✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python gh_ai_core.py setup")
        print("2. Enter your OpenRouter API key")
        print("3. Start using: python gh_ai_core.py ask 'Hello!'")
        return True
    else:
        print("❌ Some tests failed. Please address the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Make scripts executable: chmod +x gh-ai")
        print("- Check Python version: python --version (needs 3.8+)")
        return False

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
