"""
Unit tests for text_parser module.
"""

import pytest
import tempfile
from pathlib import Path
import sys
from pathlib import Path as PathlibPath

# Add src directory to path for imports
sys.path.insert(0, str(PathlibPath(__file__).parent.parent / 'src'))

import text_parser


class TestTokenize:
    """Tests for word tokenization."""
    
    def test_tokenize_simple_text(self):
        """Test tokenization of simple text."""
        text = "rosa rosae sunt"
        tokens = text_parser.tokenize(text)
        assert tokens == ["rosa", "rosae", "sunt"]
    
    def test_tokenize_with_punctuation(self):
        """Test tokenization with punctuation."""
        text = "rosa. rosae, sunt!"
        tokens = text_parser.tokenize(text)
        assert tokens == ["rosa.", "rosae,", "sunt!"]
    
    def test_tokenize_multiple_spaces(self):
        """Test tokenization with multiple spaces."""
        text = "rosa    rosae  sunt"
        tokens = text_parser.tokenize(text)
        # split() handles multiple spaces correctly
        assert len(tokens) == 3
        assert tokens[0] == "rosa"


class TestRemovePunctuation:
    """Tests for punctuation removal and normalization."""
    
    def test_remove_punctuation_simple(self):
        """Test removing punctuation from words."""
        assert text_parser.remove_punctuation("rosa.") == "rosa"
        assert text_parser.remove_punctuation("rosae,") == "rosae"
        assert text_parser.remove_punctuation("sunt!") == "sunt"
    
    def test_lowercasing(self):
        """Test that words are lowercased."""
        assert text_parser.remove_punctuation("Rosa") == "rosa"
        assert text_parser.remove_punctuation("ROSAE") == "rosae"
    
    def test_multiple_punctuation(self):
        """Test removing multiple punctuation marks."""
        assert text_parser.remove_punctuation("rosa...") == "rosa"
        assert text_parser.remove_punctuation("(rosae)") == "rosae"
    
    def test_empty_after_punctuation_removal(self):
        """Test when word is only punctuation."""
        assert text_parser.remove_punctuation("...") == ""
        assert text_parser.remove_punctuation("!!!") == ""


class TestParseText:
    """Tests for text parsing and word counting."""
    
    def test_parse_simple_text(self):
        """Test parsing simple text."""
        text = "rosa rosae rosa"
        counts = text_parser.parse_text(text)
        assert counts["rosa"] == 2
        assert counts["rosae"] == 1
    
    def test_parse_with_punctuation(self):
        """Test parsing text with punctuation."""
        text = "rosa. rosae, rosa!"
        counts = text_parser.parse_text(text)
        assert counts["rosa"] == 2
        assert counts["rosae"] == 1
    
    def test_parse_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        text = "Rosa ROSA rosa"
        counts = text_parser.parse_text(text)
        assert counts["rosa"] == 3
    
    def test_parse_empty_text(self):
        """Test parsing empty text."""
        counts = text_parser.parse_text("")
        assert counts == {}
    
    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only text."""
        counts = text_parser.parse_text("   \n\t  ")
        assert counts == {}
    
    def test_frequency_counting(self):
        """Test that frequencies are counted correctly."""
        text = "et et et et in in causa"
        counts = text_parser.parse_text(text)
        assert counts["et"] == 4
        assert counts["in"] == 2
        assert counts["causa"] == 1


class TestReadTextFile:
    """Tests for reading text files."""
    
    def test_read_utf8_file(self):
        """Test reading UTF-8 encoded file."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                         suffix='.txt', delete=False) as f:
            f.write("rosa rosae sunt")
            temp_path = f.name
        
        try:
            content = text_parser.read_text_file(temp_path)
            assert content == "rosa rosae sunt"
        finally:
            Path(temp_path).unlink()
    
    def test_read_latin1_file(self):
        """Test reading Latin-1 encoded file."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='latin-1',
                                         suffix='.txt', delete=False) as f:
            f.write("rosa café")
            temp_path = f.name
        
        try:
            content = text_parser.read_text_file(temp_path, encoding='latin-1')
            assert "rosa" in content
        finally:
            Path(temp_path).unlink()
    
    def test_read_nonexistent_file(self):
        """Test reading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            text_parser.read_text_file("/nonexistent/path/file.txt")


class TestParseFile:
    """Tests for parsing files."""
    
    def test_parse_file(self):
        """Test parsing a text file."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         suffix='.txt', delete=False) as f:
            f.write("rosa rosae rosa sunt")
            temp_path = f.name
        
        try:
            counts = text_parser.parse_file(temp_path)
            assert counts["rosa"] == 2
            assert counts["rosae"] == 1
            assert counts["sunt"] == 1
        finally:
            Path(temp_path).unlink()
    
    def test_parse_file_with_punctuation(self):
        """Test parsing file with punctuation."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         suffix='.txt', delete=False) as f:
            f.write("Sunt optimi. Rosae sunt pulchrae.")
            temp_path = f.name
        
        try:
            counts = text_parser.parse_file(temp_path)
            assert "sunt" == "sunt"
            assert counts["sunt"] == 2
        finally:
            Path(temp_path).unlink()


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_get_word_list(self):
        """Test getting unique word list."""
        counts = {"rosa": 2, "sunt": 1}
        words = text_parser.get_word_list(counts)
        assert set(words) == {"rosa", "sunt"}
    
    def test_get_total_word_count(self):
        """Test getting total word count."""
        counts = {"rosa": 2, "sunt": 1, "et": 3}
        total = text_parser.get_total_word_count(counts)
        assert total == 6
    
    def test_get_total_word_count_empty(self):
        """Test total word count for empty dictionary."""
        total = text_parser.get_total_word_count({})
        assert total == 0
