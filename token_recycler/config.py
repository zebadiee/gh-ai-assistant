"""
Shared configuration for token recycling, caching, and usage tracking.
Centralizes filesystem locations and default parameters so TokenManager,
TokenOptimizer, and upcoming recycler services stay in sync.
"""

from pathlib import Path

# Base configuration directory under the user's home folder
CONFIG_DIR = Path.home() / ".gh-ai-assistant"

# SQLite database paths
USAGE_DB = CONFIG_DIR / "usage.db"
TOKEN_CACHE_DB = CONFIG_DIR / "token_cache.db"
TOKEN_METRICS_DB = CONFIG_DIR / "token_metrics.db"

# Default behavioral knobs that multiple components share
DEFAULT_MAX_CACHE_AGE_HOURS = 24
DEFAULT_MAX_WORKERS = 10


def ensure_config_dir() -> None:
    """Create the config directory if it does not already exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
