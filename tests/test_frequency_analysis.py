"""
Unit tests for frequency_analysis module.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from frequency_analysis import FrequencyAnalyzer


class TestFrequencyAnalyzer:
    """Tests for FrequencyAnalyzer class."""
    
    @pytest.fixture
    def sample_word_counts(self):
        """Sample word frequency counts for testing."""
        return {
            "rosa": 10,
            "rosae": 8,
            "sunt": 5,
            "et": 15,
            "in": 3,
            "cum": 2,
            "sed": 1
        }
    
    @pytest.fixture
    def analyzer(self, sample_word_counts):
        """Create analyzer with sample data."""
        return FrequencyAnalyzer(sample_word_counts)
    
    def test_initialization(self, analyzer, sample_word_counts):
        """Test analyzer initialization."""
        assert analyzer.word_counts == sample_word_counts
        assert analyzer.total_words == sum(sample_word_counts.values())
    
    def test_get_frequency_stats(self, analyzer):
        """Test getting frequency statistics."""
        stats = analyzer.get_frequency_stats()
        assert stats['total_words'] == 44
        assert stats['unique_words'] == 7
        assert stats['average_frequency'] > 0


class TestSorting:
    """Tests for sorting functionality."""
    
    @pytest.fixture
    def sample_word_counts(self):
        """Sample word frequency counts."""
        return {
            "rosa": 10,
            "rosae": 8,
            "sunt": 5,
            "et": 15,
            "in": 3
        }
    
    @pytest.fixture
    def analyzer(self, sample_word_counts):
        """Create analyzer."""
        return FrequencyAnalyzer(sample_word_counts)
    
    def test_sort_descending(self, analyzer):
        """Test sorting by frequency descending."""
        sorted_words = analyzer.get_sorted_by_frequency(descending=True)
        counts = [count for _, count in sorted_words]
        assert counts == [15, 10, 8, 5, 3]  # "et", "rosa", "rosae", "sunt", "in"
    
    def test_sort_ascending(self, analyzer):
        """Test sorting by frequency ascending."""
        sorted_words = analyzer.get_sorted_by_frequency(descending=False)
        counts = [count for _, count in sorted_words]
        assert counts == [3, 5, 8, 10, 15]  # "in", "sunt", "rosae", "rosa", "et"
    
    def test_first_word_most_frequent(self, analyzer):
        """Test that first sorted word is most frequent."""
        sorted_words = analyzer.get_sorted_by_frequency()
        assert sorted_words[0][0] == "et"  # Most frequent


class TestFiltering:
    """Tests for filtering functionality."""
    
    @pytest.fixture
    def sample_word_counts(self):
        """Sample word frequency counts."""
        return {
            "rosa": 10,
            "rosae": 8,
            "sunt": 5,
            "et": 15,
            "in": 3,
            "cum": 2,
            "sed": 1
        }
    
    @pytest.fixture
    def analyzer(self, sample_word_counts):
        """Create analyzer."""
        return FrequencyAnalyzer(sample_word_counts)
    
    def test_filter_by_minimum_count(self, analyzer):
        """Test filtering by minimum count."""
        filtered = analyzer.filter_by_minimum_count(5)
        words = [word for word, _ in filtered]
        assert "et" in words  # 15
        assert "rosa" in words  # 10
        assert "rosae" in words  # 8
        assert "sunt" in words  # 5
        assert "in" not in words  # 3
        assert "cum" not in words  # 2
        assert "sed" not in words  # 1
    
    def test_filter_by_minimum_count_zero(self, analyzer):
        """Test filtering with min count 0."""
        filtered = analyzer.filter_by_minimum_count(0)
        assert len(filtered) == 7  # All words
    
    def test_filter_by_minimum_count_none(self, analyzer):
        """Test filtering with high minimum count."""
        filtered = analyzer.filter_by_minimum_count(100)
        assert len(filtered) == 0  # No words
    
    def test_filter_by_top_n(self, analyzer):
        """Test getting top N words."""
        top_3 = analyzer.filter_by_top_n(3)
        assert len(top_3) == 3
        words = [word for word, _ in top_3]
        assert words[0] == "et"  # Most frequent
    
    def test_filter_by_top_n_zero(self, analyzer):
        """Test top 0 words."""
        top_0 = analyzer.filter_by_top_n(0)
        assert len(top_0) == 0
    
    def test_filter_by_top_n_exceeds_list(self, analyzer):
        """Test top N when N exceeds word count."""
        top_100 = analyzer.filter_by_top_n(100)
        assert len(top_100) == 7  # Only 7 words available
    
    def test_filter_by_percentile(self, analyzer):
        """Test filtering by percentile."""
        top_50 = analyzer.filter_by_percentile(50)
        # Top 50% should include most frequent words
        assert len(top_50) > 0
        # Most frequent word should always be included
        words = [word for word, _ in top_50]
        assert "et" in words


class TestPercentages:
    """Tests for percentage calculation."""
    
    @pytest.fixture
    def sample_word_counts(self):
        """Sample word frequency counts."""
        return {
            "rosa": 50,
            "rosae": 50
        }
    
    @pytest.fixture
    def analyzer(self, sample_word_counts):
        """Create analyzer."""
        return FrequencyAnalyzer(sample_word_counts)
    
    def test_calculate_percentages(self, analyzer):
        """Test percentage calculations."""
        percentages = analyzer.calculate_percentages()
        assert percentages["rosa"] == 50.0
        assert percentages["rosae"] == 50.0
    
    def test_percentages_sum_to_100(self, analyzer):
        """Test that percentages sum to 100."""
        percentages = analyzer.calculate_percentages()
        total = sum(percentages.values())
        assert abs(total - 100.0) < 0.01  # Allow for float rounding
    
    def test_single_word_percentage(self):
        """Test percentage for single word."""
        analyzer = FrequencyAnalyzer({"word": 100})
        percentages = analyzer.calculate_percentages()
        assert percentages["word"] == 100.0


class TestReporting:
    """Tests for report generation."""
    
    @pytest.fixture
    def sample_word_counts(self):
        """Sample word frequency counts."""
        return {
            "rosa": 10,
            "sunt": 5,
            "et": 15
        }
    
    @pytest.fixture
    def analyzer(self, sample_word_counts):
        """Create analyzer."""
        return FrequencyAnalyzer(sample_word_counts)
    
    def test_generate_report(self, analyzer):
        """Test report generation."""
        report = analyzer.generate_report()
        assert "WORD FREQUENCY REPORT" in report
        assert "rosa" in report
        assert "sunt" in report
        assert "et" in report
        assert "Total words" in report
        assert "Unique words" in report
    
    def test_report_contains_percentages(self, analyzer):
        """Test that report contains percentage information."""
        report = analyzer.generate_report()
        assert "%" in report
    
    def test_report_formatting(self, analyzer):
        """Test report formatting."""
        report = analyzer.generate_report()
        lines = report.split("\n")
        # Should have header, divider, and data rows
        assert len(lines) > 5
        assert any("=" in line for line in lines)


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_word_counts(self):
        """Test with empty word counts."""
        analyzer = FrequencyAnalyzer({})
        assert analyzer.total_words == 0
        assert analyzer.get_frequency_stats()['unique_words'] == 0
    
    def test_single_word(self):
        """Test with single word."""
        analyzer = FrequencyAnalyzer({"rosa": 1})
        sorted_words = analyzer.get_sorted_by_frequency()
        assert len(sorted_words) == 1
        assert sorted_words[0][0] == "rosa"
    
    def test_single_word_percentage(self):
        """Test percentage with single word."""
        analyzer = FrequencyAnalyzer({"rosa": 5})
        percentages = analyzer.calculate_percentages()
        assert percentages["rosa"] == 100.0
