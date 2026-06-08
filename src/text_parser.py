"""
Text parser module for extracting and normalizing Latin words from text files.

Provides functionality to parse Latin text, extract individual words, count occurrences,
and handle various encodings and punctuation.
"""

import re
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def tokenize(text: str) -> List[str]:
    """
    Tokenize text by splitting on whitespace.
    
    Args:
        text: The text to tokenize
        
    Returns:
        List of tokens from the text
    """
    return text.split()


def remove_punctuation(word: str) -> str:
    """
    Remove punctuation from a word and normalize to lowercase.
    
    Args:
        word: The word to clean
        
    Returns:
        The cleaned word with punctuation removed and lowercased
    """
    # Keep only letters and basic characters (handle combining marks for accents)
    cleaned = re.sub(r'[^\w\u0300-\u036f-]', '', word, flags=re.UNICODE)
    return cleaned.lower().strip()


def parse_text(text: str) -> Dict[str, int]:
    """
    Parse text and return word frequency counts.
    
    Tokenizes text, removes punctuation, normalizes to lowercase, and counts occurrences.
    Filters out empty tokens.
    
    Args:
        text: The text to parse
        
    Returns:
        Dictionary mapping words to their occurrence counts
    """
    word_counts = defaultdict(int)
    
    tokens = tokenize(text)
    for token in tokens:
        cleaned_word = remove_punctuation(token)
        if cleaned_word:  # Only count non-empty words
            word_counts[cleaned_word] += 1
    
    return dict(word_counts)


def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read a text file with specified encoding and error handling.
    
    Args:
        file_path: Path to the text file
        encoding: File encoding (default: utf-8, also supports latin-1)
        
    Returns:
        The contents of the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        UnicodeDecodeError: If the file cannot be decoded
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as e:
        logger.error(f"Failed to read file {file_path} with encoding {encoding}: {e}")
        raise


def parse_file(file_path: str, encoding: str = 'utf-8') -> Dict[str, int]:
    """
    Parse a Latin text file and return word frequency counts.
    
    Reads the file with the specified encoding and parses the text.
    
    Args:
        file_path: Path to the text file to parse
        encoding: File encoding (default: utf-8)
        
    Returns:
        Dictionary mapping words to their occurrence counts
        
    Raises:
        FileNotFoundError: If the file does not exist
        UnicodeDecodeError: If the file cannot be decoded
    """
    text = read_text_file(file_path, encoding=encoding)
    return parse_text(text)


def get_word_list(word_counts: Dict[str, int]) -> List[str]:
    """
    Get a list of unique words from a word count dictionary.
    
    Args:
        word_counts: Dictionary of word counts
        
    Returns:
        List of unique words
    """
    return list(word_counts.keys())


def get_total_word_count(word_counts: Dict[str, int]) -> int:
    """
    Get total word count across all occurrences.
    
    Args:
        word_counts: Dictionary of word counts
        
    Returns:
        Total number of words in the text
    """
    return sum(word_counts.values())
