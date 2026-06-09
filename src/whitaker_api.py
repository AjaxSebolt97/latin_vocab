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
from html.parser import HTMLParser

logger = logging.getLogger(__name__)

# Wiktionary API base URL for Latin definitions (more reliable than Whitaker's Words)
API_URL = "https://en.wiktionary.org/api/rest_v1/page/definition"

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".latin_vocab" / "api_cache"

# Cache expiration (days)
CACHE_EXPIRATION_DAYS = 30

# Request throttling
REQUEST_DELAY = 0.3  # Seconds between requests
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2


class HTMLStripper(HTMLParser):
    """Simple HTML tag stripper for parsing Wiktionary definitions."""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_data(self):
        return ''.join(self.text).strip()


def strip_html(html_text: str) -> str:
    """Remove HTML tags from text."""
    if not html_text:
        return ""
    stripper = HTMLStripper()
    try:
        stripper.feed(html_text)
        return stripper.get_data()
    except Exception:
        return html_text


class WhitakerAPIClient:
    """Client for looking up Latin words using Wiktionary API."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the API client.
        
        Args:
            cache_dir: Directory to store API response cache (default: ~/.latin_vocab/api_cache)
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_request_time = 0
        # Set up headers with User-Agent required by Wiktionary
        self.headers = {
            'User-Agent': 'Latin-Vocab-Tool/1.0 (+https://github.com/username/latin_vocab)'
        }
        logger.info(f"Using Wiktionary API for Latin word definitions")
    
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
    
    def _parse_wiktionary_definition(self, definitions_list: list) -> str:
        """
        Parse definition from Wiktionary API response.
        
        Args:
            definitions_list: List of definitions from Wiktionary
            
        Returns:
            Formatted definition string (HTML tags stripped)
        """
        if not definitions_list:
            return ""
        
        # Get the first definition if available
        if isinstance(definitions_list, list) and len(definitions_list) > 0:
            first_def = definitions_list[0]
            if isinstance(first_def, dict) and 'definition' in first_def:
                # Strip HTML tags from the definition
                html_def = first_def['definition']
                return strip_html(html_def)
            elif isinstance(first_def, str):
                return strip_html(first_def)
        
        return ""
    
    def _query_api(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Query Wiktionary API for a Latin word with retry logic.
        
        Args:
            word: The Latin word to look up
            
        Returns:
            Dictionary with word data (definition, part of speech, etc.), or None if lookup failed
        """
        for attempt in range(RETRY_MAX_ATTEMPTS):
            try:
                self._throttle_requests()
                
                # Query Wiktionary API for Latin definitions
                url = f"{API_URL}/{word}"
                response = requests.get(url, headers=self.headers, params={'redirect': 'true'}, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Extract Latin definitions (language code: "la")
                        if 'la' in data:
                            latin_data = data['la']
                            definitions = []
                            pos_tags = []
                            
                            if isinstance(latin_data, list):
                                for entry in latin_data:
                                    if isinstance(entry, dict):
                                        # Extract definitions
                                        if 'definitions' in entry:
                                            definitions.extend(entry['definitions'])
                                        # Extract part of speech
                                        if 'partOfSpeech' in entry:
                                            pos_tags.append(entry['partOfSpeech'])
                            
                            if definitions or pos_tags:
                                return {
                                    'word': word,
                                    'status': 'found',
                                    'definition': self._parse_wiktionary_definition(definitions),
                                    'part_of_speech': pos_tags[0] if pos_tags else '',
                                    'lemma': word,
                                    'grammatical_info': ''
                                }
                        
                        # No Latin data found
                        return {
                            'word': word,
                            'status': 'not_found',
                            'definition': '',
                            'part_of_speech': '',
                            'lemma': word,
                            'grammatical_info': ''
                        }
                        
                    except json.JSONDecodeError:
                        logger.debug(f"Failed to parse JSON response for '{word}'")
                        return None
                        
                elif response.status_code == 404:
                    return {
                        'word': word,
                        'status': 'not_found',
                        'definition': '',
                        'part_of_speech': '',
                        'lemma': word,
                        'grammatical_info': ''
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
        Look up a word in Wiktionary API with local caching.
        
        First checks local cache, then queries API if not cached.
        
        Args:
            word: The Latin word to look up
            
        Returns:
            Dictionary with word data (definition, part_of_speech, lemma, etc.), or None if lookup failed
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
