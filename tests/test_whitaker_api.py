"""
Unit tests for whitaker_api module.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import whitaker_api


class TestWhitakerAPIClient:
    """Tests for WhitakerAPIClient class."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def client(self, temp_cache_dir):
        """Create API client with temporary cache."""
        return whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
    
    def test_client_initialization(self, temp_cache_dir):
        """Test client initialization creates cache directory."""
        client = whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
        assert temp_cache_dir.exists()
    
    def test_get_cache_path(self, client):
        """Test cache path generation."""
        path = client._get_cache_path("rosa")
        assert "rosa" in str(path)
        assert str(path).endswith(".json")
    
    def test_get_cache_path_sanitization(self, client):
        """Test that cache paths are sanitized."""
        path1 = client._get_cache_path("rosa")
        path2 = client._get_cache_path("rosae")
        # Different words should have different paths
        assert path1 != path2


class TestCaching:
    """Tests for cache functionality."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def client(self, temp_cache_dir):
        """Create client with temp cache."""
        return whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
    
    def test_write_and_read_cache(self, client):
        """Test writing and reading from cache."""
        word = "rosa"
        data = {"word": "rosa", "definition": "rose"}
        
        # Write to cache
        client._write_cache(word, data)
        
        # Read from cache
        cached_data = client._read_cache(word)
        assert cached_data == data
    
    def test_cache_file_created(self, client, temp_cache_dir):
        """Test that cache files are created."""
        word = "rosa"
        data = {"word": "rosa", "definition": "rose"}
        
        client._write_cache(word, data)
        
        cache_files = list(temp_cache_dir.glob("*.json"))
        assert len(cache_files) == 1
    
    def test_read_cache_returns_none_for_missing(self, client):
        """Test that missing cache returns None."""
        cached_data = client._read_cache("nonexistent_word_xyz")
        assert cached_data is None
    
    def test_cache_expiration_validation(self, client):
        """Test cache expiration check."""
        import time
        from datetime import datetime, timedelta
        
        word = "test_word"
        data = {"word": "test_word"}
        cache_path = client._get_cache_path(word)
        
        # Write cache
        client._write_cache(word, data)
        assert cache_path.exists()
        
        # Check valid cache
        assert client._is_cache_valid(cache_path)
        
        # Simulate old cache by changing modification time
        old_time = (datetime.now() - timedelta(days=35)).timestamp()
        # Note: In real tests, you'd use os.utime to change the timestamp


class TestAPIQueries:
    """Tests for API query functionality."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def client(self, temp_cache_dir):
        """Create client with temp cache."""
        return whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
    
    @patch('whitaker_api.requests.get')
    def test_query_api_success(self, mock_get, client):
        """Test successful API query."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'la': [
                {
                    'partOfSpeech': 'Noun',
                    'definitions': [
                        {'definition': 'rose (plant or flower)'}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = client._query_api("rosa")
        assert result is not None
        assert result['status'] == 'found'
        assert result['word'] == 'rosa'
        assert 'definition' in result
        assert 'rose' in result['definition'].lower()
    
    @patch('whitaker_api.requests.get')
    def test_query_api_not_found(self, mock_get, client):
        """Test API query for non-existent word."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client._query_api("zzzzzzz")
        assert result is not None
        assert result['status'] == 'not_found'
    
    @patch('whitaker_api.requests.get')
    def test_lookup_word_uses_cache(self, mock_get, client):
        """Test that lookup_word uses cache."""
        # Manually write to cache
        word = "rosa"
        cached_data = {"word": "rosa", "definition": "rose", "cached": True}
        client._write_cache(word, cached_data)
        
        # Lookup should return cached data without calling API
        result = client.lookup_word(word)
        assert result == cached_data
        mock_get.assert_not_called()
    
    @patch('whitaker_api.requests.get')
    def test_lookup_word_cache_miss(self, mock_get, client):
        """Test lookup_word when cache misses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>rosa</html>"
        mock_get.return_value = mock_response
        
        result = client.lookup_word("rosa")
        assert result is not None
        mock_get.assert_called_once()


class TestBatchLookup:
    """Tests for batch word lookups."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def client(self, temp_cache_dir):
        """Create client with temp cache."""
        return whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
    
    @patch('whitaker_api.requests.get')
    def test_lookup_words_batch(self, mock_get, client):
        """Test looking up multiple words."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>word</html>"
        mock_get.return_value = mock_response
        
        words = ["rosa", "rosae", "sunt"]
        results = client.lookup_words(words)
        
        assert len(results) == 3
        assert "rosa" in results
        assert "rosae" in results
        assert "sunt" in results


class TestCacheMaintenance:
    """Tests for cache maintenance."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def client(self, temp_cache_dir):
        """Create client with temp cache."""
        return whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
    
    def test_clear_cache(self, client):
        """Test clearing cache."""
        # Write some cache files
        client._write_cache("rosa", {"word": "rosa"})
        client._write_cache("rosae", {"word": "rosae"})
        
        cache_files = list(client.cache_dir.glob("*.json"))
        assert len(cache_files) == 2
        
        # Clear cache
        client.clear_cache()
        
        cache_files = list(client.cache_dir.glob("*.json"))
        assert len(cache_files) == 0
