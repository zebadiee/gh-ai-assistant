#!/usr/bin/env python3
"""
Test suite for GitHub CLI AI Assistant
"""

import unittest
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
from contextlib import nullcontext

# Import from gh_ai_core
import sys
sys.path.insert(0, os.path.dirname(__file__))
from gh_ai_core import (
    TokenManager,
    OpenRouterClient,
    AIAssistant,
    GitHubContextExtractor,
    keyring as core_keyring,
)


class TestTokenManager(unittest.TestCase):
    """Test TokenManager functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_usage.db"
        
    def tearDown(self):
        """Clean up test files"""
        if self.db_path.exists():
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
        
    def test_database_initialization(self):
        """Test database is created correctly"""
        manager = TokenManager()
        manager.db_path = self.db_path
        manager._init_database()
        
        self.assertTrue(self.db_path.exists())
        
        # Check table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        self.assertIn('usage', tables)
        
    def test_record_usage(self):
        """Test recording usage data"""
        manager = TokenManager()
        manager.db_path = self.db_path
        manager._init_database()
        
        manager.record_usage("test-model", 100, 0.001)
        
        # Verify record exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usage WHERE model = 'test-model'")
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "test-model")
        self.assertEqual(result[3], 100)
        
    def test_get_today_usage(self):
        """Test retrieving today's usage"""
        manager = TokenManager()
        manager.db_path = self.db_path
        manager._init_database()
        
        # Add test data
        manager.record_usage("test-model", 100)
        manager.record_usage("test-model", 200)
        
        requests, tokens = manager.get_today_usage("test-model")
        
        self.assertEqual(requests, 2)
        self.assertEqual(tokens, 300)


class TestOpenRouterClient(unittest.TestCase):
    """Test OpenRouter client"""
    
    def test_client_initialization(self):
        """Test client is initialized with correct headers"""
        client = OpenRouterClient("test-api-key")
        
        self.assertEqual(client.api_key, "test-api-key")
        self.assertIn("Authorization", client.headers)
        self.assertIn("Bearer test-api-key", client.headers["Authorization"])
        
    @patch('requests.post')
    def test_chat_completion_success(self, mock_post):
        """Test successful chat completion"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 50}
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient("test-api-key")
        result = client.chat_completion(
            "test-model",
            [{"role": "user", "content": "Hello"}]
        )
        
        self.assertIn("choices", result)
        self.assertEqual(result["choices"][0]["message"]["content"], "Test response")


class TestGitHubContextExtractor(unittest.TestCase):
    """Test GitHub context extraction"""
    
    @patch('subprocess.run')
    def test_get_repo_info(self, mock_run):
        """Test repository info extraction"""
        mock_run.side_effect = [
            MagicMock(stdout="https://github.com/user/repo.git\n"),
            MagicMock(stdout="main\n"),
            MagicMock(stdout="abc123 Test commit\n")
        ]
        
        extractor = GitHubContextExtractor()
        info = extractor.get_repo_info()
        
        self.assertIn("repo_url", info)
        self.assertIn("branch", info)
        self.assertIn("recent_commits", info)


class TestAIAssistant(unittest.TestCase):
    """Test AI Assistant integration"""
    
    def test_api_key_loading(self):
        """Test API key is loaded from keyring"""
        if core_keyring is None:
            self.skipTest("keyring module not available")
        with patch('gh_ai_core.keyring.get_password', return_value="test-api-key"):
            assistant = AIAssistant()
            self.assertEqual(assistant.api_key, "test-api-key")
        
    def test_enhance_prompt_with_context(self):
        """Test prompt enhancement with context"""
        with patch('gh_ai_core.keyring.get_password', return_value=None):
            assistant = AIAssistant()
        
        with patch.object(assistant.github_context, 'get_repo_info', return_value={}):
            with patch.object(assistant.github_context, 'get_current_changes', return_value=""):
                messages = assistant.enhance_prompt_with_context("Test prompt")
                
                self.assertIsInstance(messages, list)
                self.assertTrue(any(msg['content'] == 'Test prompt' for msg in messages))

    @patch('gh_ai_core.ClaudeCLIClient')
    def test_claude_cli_provider(self, mock_cli_cls):
        """Claude CLI provider should route through the CLI wrapper."""
        os.environ['GH_AI_PROVIDER'] = 'claude-cli'
        mock_cli = MagicMock()
        mock_cli.chat_completion.return_value = {"content": "CLI response"}
        mock_cli_cls.return_value = mock_cli
        keyring_ctx = patch('gh_ai_core.keyring.get_password', return_value=None) if core_keyring else nullcontext()
        with keyring_ctx:
            assistant = AIAssistant()
        output = assistant.ask('Hello from Claude', use_context=False)

        self.assertEqual(output, 'CLI response')
        mock_cli.chat_completion.assert_called_once()
        os.environ.pop('GH_AI_PROVIDER', None)

    @patch('gh_ai_core.ZaiGLMClient')
    @patch.object(TokenManager, 'record_usage')
    def test_zai_glm_provider(self, mock_record_usage, mock_glm_cls):
        """Z.ai GLM provider should call the HTTP client and record usage."""
        os.environ['GH_AI_PROVIDER'] = 'zai-glm'
        os.environ['ZAI_API_KEY'] = 'dummy-key'
        keyring_ctx = patch('gh_ai_core.keyring.get_password', return_value=None) if core_keyring else nullcontext()
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = {
            'choices': [{'message': {'content': 'GLM output'}}],
            'usage': {'total_tokens': 42, 'total_cost': 0.0}
        }
        mock_glm_cls.return_value = mock_client
        with keyring_ctx:
            assistant = AIAssistant()
        output = assistant.ask('Hello GLM', use_context=False)

        self.assertEqual(output, 'GLM output')
        mock_client.chat_completion.assert_called_once()
        mock_record_usage.assert_called_once_with('zai-glm', 42, 0.0)

        os.environ.pop('GH_AI_PROVIDER', None)
        os.environ.pop('ZAI_API_KEY', None)



def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
