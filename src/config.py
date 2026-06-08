"""
Configuration module for Latin Vocab tool.

Manages settings for API caching, logging, and other configuration options.
"""

from pathlib import Path
from typing import Optional
import os

# Application directories
APP_NAME = "latin_vocab"
APP_HOME = Path.home() / f".{APP_NAME}"
CACHE_DIR = APP_HOME / "api_cache"
LOG_DIR = APP_HOME / "logs"

# API configuration
WHITAKER_API_URL = "https://www.whitakers-words.com/go"
API_CACHE_EXPIRATION_DAYS = 30
API_REQUEST_DELAY = 0.5  # Seconds between requests
API_RETRY_MAX_ATTEMPTS = 3
API_RETRY_BACKOFF_FACTOR = 2

# Logging configuration
LOG_LEVEL = os.getenv("LATIN_VOCAB_LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "latin_vocab.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Flashcard defaults
DEFAULT_FLASHCARD_FORMAT = "csv"
DEFAULT_FLASHCARD_TEMPLATE = "comprehensive"


def ensure_app_directories():
    """Create necessary application directories if they don't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_dir() -> Path:
    """
    Get the API cache directory, creating it if necessary.
    
    Returns:
        Path object for the cache directory
    """
    ensure_app_directories()
    return CACHE_DIR


def get_log_dir() -> Path:
    """
    Get the logging directory, creating it if necessary.
    
    Returns:
        Path object for the log directory
    """
    ensure_app_directories()
    return LOG_DIR


def get_log_file() -> Path:
    """
    Get the log file path, creating parent directory if necessary.
    
    Returns:
        Path object for the log file
    """
    ensure_app_directories()
    return LOG_FILE
