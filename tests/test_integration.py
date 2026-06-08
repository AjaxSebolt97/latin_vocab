"""
Integration tests for the complete Latin Vocab pipeline.
"""

import pytest
import tempfile
import csv
import json
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import text_parser
import frequency_analysis
import flashcard_generator


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_latin_text(self, temp_dir):
        """Create sample Latin text file."""
        text = """
        Rosa rosae sunt pulchrae. Rosa est flor.
        Et in rosa pulchra habitant. Agricola amabat rosas.
        Rosae sunt in horto. Et puellae rosam amant.
        Est rosa in horto. Rosa pulchra est. Et flor rosa est.
        """
        text_file = temp_dir / "sample.txt"
        text_file.write_text(text)
        return text_file
    
    def test_parse_to_frequency_workflow(self, sample_latin_text):
        """Test parsing text and analyzing frequency."""
        # Parse
        word_counts = text_parser.parse_file(str(sample_latin_text))
        assert len(word_counts) > 0
        
        # Analyze
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        top_words = analyzer.filter_by_top_n(5)
        
        assert len(top_words) <= 5
        # Most frequent words should be at top
        assert top_words[0][1] >= top_words[-1][1]
    
    def test_flashcard_generation_csv(self, sample_latin_text, temp_dir):
        """Test CSV flashcard generation from text."""
        # Parse
        word_counts = text_parser.parse_file(str(sample_latin_text))
        
        # Analyze
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        top_words = analyzer.filter_by_top_n(10)
        
        # Create mock word data
        word_data = {}
        for word, _ in top_words:
            word_data[word] = {
                "definition": f"definition of {word}",
                "lemma": word,
                "part_of_speech": "noun"
            }
        
        # Generate flashcards
        output_file = temp_dir / "flashcards.csv"
        generator = flashcard_generator.FlashcardGenerator(word_data, word_counts)
        generator.export_csv(top_words, str(output_file))
        
        # Verify
        assert output_file.exists()
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert "word" in rows[0]
    
    def test_flashcard_generation_json(self, sample_latin_text, temp_dir):
        """Test JSON flashcard generation from text."""
        # Parse
        word_counts = text_parser.parse_file(str(sample_latin_text))
        
        # Analyze
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        top_words = analyzer.filter_by_top_n(10)
        
        # Create mock word data
        word_data = {}
        for word, _ in top_words:
            word_data[word] = {"definition": f"def of {word}"}
        
        # Generate
        output_file = temp_dir / "flashcards.json"
        generator = flashcard_generator.FlashcardGenerator(word_data, word_counts)
        generator.export_json(top_words, str(output_file))
        
        # Verify
        assert output_file.exists()
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
    
    def test_multiple_output_formats(self, sample_latin_text, temp_dir):
        """Test generating same vocabulary in multiple formats."""
        # Parse
        word_counts = text_parser.parse_file(str(sample_latin_text))
        
        # Analyze
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        words = analyzer.filter_by_top_n(5)
        
        # Create word data
        word_data = {word: {"definition": f"def of {word}"} for word, _ in words}
        
        generator = flashcard_generator.FlashcardGenerator(word_data, word_counts)
        
        # Export both formats
        csv_file = temp_dir / "cards.csv"
        json_file = temp_dir / "cards.json"
        
        generator.export_csv(words, str(csv_file))
        generator.export_json(words, str(json_file))
        
        # Verify both exist
        assert csv_file.exists()
        assert json_file.exists()
        
        # Verify same number of flashcards
        with open(csv_file, 'r') as f:
            csv_rows = list(csv.DictReader(f))
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        assert len(csv_rows) == len(json_data)


class TestCaching:
    """Tests for API caching across runs."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_cache_reuse(self, temp_cache_dir):
        """Test that API cache is reused on second run."""
        import whitaker_api
        
        client = whitaker_api.WhitakerAPIClient(cache_dir=temp_cache_dir)
        
        # First lookup
        word = "rosa"
        result1 = client.lookup_word(word)
        
        # Check cache was written
        cache_files = list(temp_cache_dir.glob("*.json"))
        assert len(cache_files) > 0
        
        # Second lookup - should use cache
        result2 = client.lookup_word(word)
        
        # Results should be identical
        assert result1 == result2


class TestSampleTexts:
    """Tests with various sample texts."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_simple_text(self, temp_dir):
        """Test with simple repeated words."""
        text = "rosa rosa rosa sunt sunt"
        text_file = temp_dir / "simple.txt"
        text_file.write_text(text)
        
        counts = text_parser.parse_file(str(text_file))
        assert counts["rosa"] == 3
        assert counts["sunt"] == 2
    
    def test_punctuated_text(self, temp_dir):
        """Test with punctuation."""
        text = "Rosa, rosae. Rosa est... pulchra!"
        text_file = temp_dir / "punct.txt"
        text_file.write_text(text)
        
        counts = text_parser.parse_file(str(text_file))
        assert "rosa" in counts
        assert counts["rosa"] == 3
    
    def test_mixed_case_text(self, temp_dir):
        """Test case insensitivity."""
        text = "Rosa ROSA rosa Rosae"
        text_file = temp_dir / "case.txt"
        text_file.write_text(text)
        
        counts = text_parser.parse_file(str(text_file))
        assert counts["rosa"] == 3
        assert counts["rosae"] == 1


class TestFiltering:
    """Tests for vocabulary filtering."""
    
    @pytest.fixture
    def word_counts(self):
        """Sample word frequencies."""
        return {
            "et": 15,
            "rosa": 10,
            "rosae": 8,
            "sunt": 5,
            "in": 3,
            "cum": 2,
            "sed": 1
        }
    
    def test_min_frequency_filtering(self, word_counts):
        """Test filtering by minimum frequency."""
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        
        # Min frequency 5
        filtered = analyzer.filter_by_minimum_count(5)
        words = [w for w, _ in filtered]
        
        assert "et" in words  # 15
        assert "rosa" in words  # 10
        assert "sunt" in words  # 5
        assert "in" not in words  # 3 < 5
    
    def test_top_n_filtering(self, word_counts):
        """Test top N filtering."""
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        
        top_3 = analyzer.filter_by_top_n(3)
        assert len(top_3) == 3
        
        # Verify top 3 are highest
        counts = [count for _, count in top_3]
        assert counts == [15, 10, 8]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
