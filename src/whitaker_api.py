"""
Whitaker Words API integration module for looking up Latin word definitions.

Provides functionality to query the Whitaker Words API, cache responses locally,
handle rate limiting, and implement retry logic.
"""

import requests
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Whitaker Words API base URL
WHITAKER_API_URL = "https://www.whitakers-words.com/go"

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".latin_vocab" / "api_cache"

# Cache expiration (days)
CACHE_EXPIRATION_DAYS = 30

# Request throttling
REQUEST_DELAY = 0.5  # Seconds between requests
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2


class WhitakerAPIClient:
    """Client for interacting with Whitaker's Words API."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the API client.
        
        Args:
            cache_dir: Directory to store API response cache (default: ~/.latin_vocab/api_cache)
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_request_time = 0
    
    def _throttle_requests(self):
        """Implement request throttling to respect API rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _get_cache_path(self, word: str) -> Path:
        """Get the cache file path for a word."""
        # Sanitize word for use as filename
        safe_word = "".join(c if c.isalnum() else "_" for c in word)
        return self.cache_dir / f"{safe_word}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file exists and is not expired."""
        if not cache_path.exists():
            return False
        
        mod_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - mod_time
        return age < timedelta(days=CACHE_EXPIRATION_DAYS)
    
    def _read_cache(self, word: str) -> Optional[Dict[str, Any]]:
        """Read word data from cache if available and valid."""
        cache_path = self._get_cache_path(word)
        
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read cache for '{word}': {e}")
            return None
    
    def _write_cache(self, word: str, data: Dict[str, Any]):
        """Write word data to cache."""
        cache_path = self._get_cache_path(word)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.warning(f"Failed to write cache for '{word}': {e}")
    
    def _query_api(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Query the Whitaker Words API for a word with retry logic.
        
        Args:
            word: The Latin word to look up
            
        Returns:
            Dictionary with API response data, or None if lookup failed
        """
        for attempt in range(RETRY_MAX_ATTEMPTS):
            try:
                self._throttle_requests()
                
                params = {'lookup': word}
                response = requests.get(WHITAKER_API_URL, params=params, timeout=10)
                
                if response.status_code == 200:
                    # Parse response - Whitaker's Words returns HTML
                    # For now, return basic structure with the response
                    return {
                        'word': word,
                        'status': 'found',
                        'response': response.text[:200]  # Store first 200 chars for reference
                    }
                elif response.status_code == 404:
                    return {
                        'word': word,
                        'status': 'not_found',
                        'response': None
                    }
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except (requests.RequestException, Exception) as e:
                if attempt < RETRY_MAX_ATTEMPTS - 1:
                    wait_time = REQUEST_DELAY * (RETRY_BACKOFF_FACTOR ** attempt)
                    logger.debug(f"API request failed for '{word}' (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"API request failed for '{word}' after {RETRY_MAX_ATTEMPTS} attempts: {e}")
                    return None
        
        return None
    
    def lookup_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Look up a word in Whitaker's Words API with caching.
        
        First checks local cache, then queries API if not cached.
        
        Args:
            word: The Latin word to look up
            
        Returns:
            Dictionary with word data, or None if lookup failed
        """
        # Check cache first
        cached_data = self._read_cache(word)
        if cached_data:
            logger.debug(f"Cache hit for '{word}'")
            return cached_data
        
        # Query API
        logger.debug(f"Querying API for '{word}'")
        data = self._query_api(word)
        
        # Cache the result (even if not found, to avoid repeated failed lookups)
        if data:
            self._write_cache(word, data)
        
        return data
    
    def lookup_words(self, words: list) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Look up multiple words.
        
        Args:
            words: List of Latin words to look up
            
        Returns:
            Dictionary mapping words to their lookup results
        """
        results = {}
        for word in words:
            results[word] = self.lookup_word(word)
        
        return results
    
    def clear_cache(self):
        """Clear all cached API responses."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
