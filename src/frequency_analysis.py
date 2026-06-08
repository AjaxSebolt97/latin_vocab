"""
Frequency analysis module for analyzing word frequencies in Latin text.

Provides functionality to calculate word frequencies, sort, filter, and generate reports.
"""

import logging
from typing import Dict, List, Tuple, Optional
from statistics import quantiles

logger = logging.getLogger(__name__)


class FrequencyAnalyzer:
    """Analyzer for word frequency statistics."""
    
    def __init__(self, word_counts: Dict[str, int]):
        """
        Initialize the analyzer with word counts.
        
        Args:
            word_counts: Dictionary mapping words to their occurrence counts
        """
        self.word_counts = word_counts
        self.total_words = sum(word_counts.values())
    
    def get_frequency_stats(self) -> Dict[str, any]:
        """
        Get frequency statistics for the text.
        
        Returns:
            Dictionary with statistics (total words, unique words, etc.)
        """
        return {
            'total_words': self.total_words,
            'unique_words': len(self.word_counts),
            'average_frequency': self.total_words / len(self.word_counts) if self.word_counts else 0
        }
    
    def get_sorted_by_frequency(self, descending: bool = True) -> List[Tuple[str, int]]:
        """
        Get words sorted by frequency.
        
        Args:
            descending: If True, sort from highest to lowest frequency
            
        Returns:
            List of (word, count) tuples sorted by frequency
        """
        return sorted(self.word_counts.items(), key=lambda x: x[1], reverse=descending)
    
    def filter_by_minimum_count(self, min_count: int) -> List[Tuple[str, int]]:
        """
        Get words with at least a minimum count.
        
        Args:
            min_count: Minimum occurrence count
            
        Returns:
            List of (word, count) tuples filtered by minimum count
        """
        filtered = [(word, count) for word, count in self.word_counts.items() 
                    if count >= min_count]
        return sorted(filtered, key=lambda x: x[1], reverse=True)
    
    def filter_by_percentile(self, percentile: float) -> List[Tuple[str, int]]:
        """
        Get top N% of most frequent words by percentile.
        
        Args:
            percentile: Percentile threshold (0-100, e.g., 50 for top 50%)
            
        Returns:
            List of (word, count) tuples in top percentile
        """
        if not self.word_counts or percentile <= 0 or percentile > 100:
            return []
        
        counts = sorted(self.word_counts.values(), reverse=True)
        
        # Calculate the cutoff count for the percentile
        percentile_index = int(len(counts) * (100 - percentile) / 100)
        cutoff = counts[percentile_index] if percentile_index < len(counts) else counts[-1]
        
        filtered = [(word, count) for word, count in self.word_counts.items() 
                    if count >= cutoff]
        return sorted(filtered, key=lambda x: x[1], reverse=True)
    
    def filter_by_top_n(self, n: int) -> List[Tuple[str, int]]:
        """
        Get the top N most frequent words.
        
        Args:
            n: Number of top words to return
            
        Returns:
            List of (word, count) tuples for top N words
        """
        sorted_words = self.get_sorted_by_frequency()
        return sorted_words[:n]
    
    def calculate_percentages(self, word_counts: Optional[Dict[str, int]] = None) -> Dict[str, float]:
        """
        Calculate percentage of total for each word.
        
        Args:
            word_counts: Optional custom word counts dict (default: uses self.word_counts)
            
        Returns:
            Dictionary mapping words to their percentage of total
        """
        counts = word_counts or self.word_counts
        percentages = {}
        
        for word, count in counts.items():
            percentages[word] = (count / self.total_words * 100) if self.total_words > 0 else 0
        
        return percentages
    
    def generate_report(self, words: Optional[List[Tuple[str, int]]] = None) -> str:
        """
        Generate a text report of word frequencies.
        
        Args:
            words: Optional list of (word, count) tuples to report (default: all words sorted)
            
        Returns:
            Formatted text report
        """
        if words is None:
            words = self.get_sorted_by_frequency()
        
        percentages = self.calculate_percentages()
        
        lines = []
        lines.append("=" * 60)
        lines.append("WORD FREQUENCY REPORT")
        lines.append("=" * 60)
        lines.append(f"Total words: {self.total_words}")
        lines.append(f"Unique words: {len(self.word_counts)}")
        lines.append("")
        lines.append(f"{'Rank':<6} {'Word':<20} {'Count':<8} {'Percentage':<12}")
        lines.append("-" * 60)
        
        for rank, (word, count) in enumerate(words, 1):
            percentage = percentages.get(word, 0)
            lines.append(f"{rank:<6} {word:<20} {count:<8} {percentage:>6.2f}%")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
