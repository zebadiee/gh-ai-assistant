#!/usr/bin/env python3
"""
Setup configuration for GitHub CLI AI Assistant
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="gh-ai-assistant",
    version="1.0.0",
    description="GitHub CLI AI Assistant with intelligent token management and free model optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/gh-ai-assistant",
    py_modules=["gh_ai_core"],
    install_requires=[
        "requests>=2.31.0",
        "keyring>=24.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gh-ai=gh_ai_core:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="github cli ai assistant openrouter deepseek token-management",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/gh-ai-assistant/issues",
        "Source": "https://github.com/yourusername/gh-ai-assistant",
    },
)
