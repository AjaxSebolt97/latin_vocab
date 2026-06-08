"""
Unit tests for flashcard_generator module.
"""

import pytest
import tempfile
import csv
import json
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from flashcard_generator import FlashcardGenerator, TEMPLATE_MINIMAL, TEMPLATE_COMPREHENSIVE


class TestFlashcardGenerator:
    """Tests for FlashcardGenerator class."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample word data and frequencies for testing."""
        word_data = {
            "rosa": {
                "definition": "rose",
                "lemma": "rosa",
                "part_of_speech": "noun"
            },
            "rosae": {
                "definition": "of roses",
                "lemma": "rosa",
                "part_of_speech": "noun"
            },
            "sunt": {
                "definition": "they are",
                "lemma": "sum",
                "part_of_speech": "verb"
            }
        }
        word_frequencies = {
            "rosa": 10,
            "rosae": 5,
            "sunt": 3
        }
        return word_data, word_frequencies
    
    @pytest.fixture
    def generator(self, sample_data):
        """Create generator with sample data."""
        word_data, frequencies = sample_data
        return FlashcardGenerator(word_data, frequencies)
    
    def test_initialization(self, generator):
        """Test generator initialization."""
        assert generator.word_data is not None
        assert generator.word_frequencies is not None


class TestFlashcardRecords:
    """Tests for flashcard record building."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data."""
        word_data = {
            "rosa": {
                "definition": "rose",
                "lemma": "rosa",
                "part_of_speech": "noun"
            }
        }
        word_frequencies = {"rosa": 10}
        return word_data, word_frequencies
    
    @pytest.fixture
    def generator(self, sample_data):
        """Create generator."""
        word_data, frequencies = sample_data
        return FlashcardGenerator(word_data, frequencies)
    
    def test_build_record_comprehensive(self, generator):
        """Test building comprehensive flashcard record."""
        record = generator._build_flashcard_record("rosa", TEMPLATE_COMPREHENSIVE)
        assert record["word"] == "rosa"
        assert record["definition"] == "rose"
        assert record["lemma"] == "rosa"
        assert record["frequency"] == "10"
    
    def test_build_record_minimal(self, generator):
        """Test building minimal flashcard record."""
        record = generator._build_flashcard_record("rosa", TEMPLATE_MINIMAL)
        assert record["word"] == "rosa"
        assert record["definition"] == "rose"
        assert len(record) == 2  # Only two fields
    
    def test_build_record_missing_data(self, generator):
        """Test building record with missing data."""
        record = generator._build_flashcard_record("unknown_word", TEMPLATE_COMPREHENSIVE)
        assert record["word"] == "unknown_word"
        assert record["definition"] == ""  # Missing data fills with empty string


class TestCSVEscaping:
    """Tests for CSV field escaping."""
    
    @pytest.fixture
    def generator(self):
        """Create generator."""
        return FlashcardGenerator({}, {})
    
    def test_escape_simple_text(self, generator):
        """Test escaping simple text."""
        escaped = generator._escape_csv_field("rosa")
        assert escaped == "rosa"  # No escaping needed
    
    def test_escape_with_comma(self, generator):
        """Test escaping text with comma."""
        escaped = generator._escape_csv_field("rose, flower")
        assert '"' in escaped
        assert "rose, flower" in escaped
    
    def test_escape_with_quote(self, generator):
        """Test escaping text with quote."""
        escaped = generator._escape_csv_field('say "hello"')
        assert '""' in escaped  # Quote should be doubled
    
    def test_escape_with_newline(self, generator):
        """Test escaping text with newline."""
        escaped = generator._escape_csv_field("line1\nline2")
        assert '"' in escaped
    
    def test_escape_none(self, generator):
        """Test escaping None value."""
        escaped = generator._escape_csv_field(None)
        assert escaped == ""


class TestGenerateFlashcards:
    """Tests for flashcard generation."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data."""
        word_data = {
            "rosa": {"definition": "rose", "lemma": "rosa"},
            "sind": {"definition": "are", "lemma": "sum"}
        }
        word_frequencies = {"rosa": 10, "sind": 5}
        return word_data, word_frequencies
    
    @pytest.fixture
    def generator(self, sample_data):
        """Create generator."""
        word_data, frequencies = sample_data
        return FlashcardGenerator(word_data, frequencies)
    
    def test_generate_flashcards(self, generator):
        """Test generating flashcards."""
        words = [("rosa", 10), ("sind", 5)]
        flashcards = generator.generate_flashcards(words)
        assert len(flashcards) == 2
        assert flashcards[0]["word"] == "rosa"
        assert flashcards[1]["word"] == "sind"
    
    def test_generate_with_template(self, generator):
        """Test generating with specific template."""
        words = [("rosa", 10)]
        flashcards = generator.generate_flashcards(words, TEMPLATE_MINIMAL)
        assert len(flashcards[0]) == 2  # Minimal template
        flashcards = generator.generate_flashcards(words, TEMPLATE_COMPREHENSIVE)
        assert len(flashcards[0]) >= 4  # Comprehensive template


class TestCSVExport:
    """Tests for CSV export."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data."""
        word_data = {
            "rosa": {"definition": "rose", "lemma": "rosa"},
            "sind": {"definition": "are", "lemma": "sum"}
        }
        word_frequencies = {"rosa": 10, "sind": 5}
        return word_data, word_frequencies
    
    @pytest.fixture
    def generator(self, sample_data):
        """Create generator."""
        word_data, frequencies = sample_data
        return FlashcardGenerator(word_data, frequencies)
    
    def test_export_csv(self, generator):
        """Test CSV export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "flashcards.csv"
            words = [("rosa", 10), ("sind", 5)]
            
            generator.export_csv(words, str(output_file))
            
            assert output_file.exists()
            
            # Verify CSV contents
            with open(output_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["word"] == "rosa"
    
    def test_export_csv_creates_directory(self, generator):
        """Test that export creates missing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "subdir" / "flashcards.csv"
            words = [("rosa", 10)]
            
            generator.export_csv(words, str(output_file))
            
            assert output_file.exists()
            assert output_file.parent.exists()


class TestJSONExport:
    """Tests for JSON export."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data."""
        word_data = {
            "rosa": {"definition": "rose"},
            "sind": {"definition": "are"}
        }
        word_frequencies = {"rosa": 10, "sind": 5}
        return word_data, word_frequencies
    
    @pytest.fixture
    def generator(self, sample_data):
        """Create generator."""
        word_data, frequencies = sample_data
        return FlashcardGenerator(word_data, frequencies)
    
    def test_export_json(self, generator):
        """Test JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "flashcards.json"
            words = [("rosa", 10), ("sind", 5)]
            
            generator.export_json(words, str(output_file))
            
            assert output_file.exists()
            
            # Verify JSON contents
            with open(output_file, 'r') as f:
                data = json.load(f)
                assert len(data) == 2
                assert data[0]["word"] == "rosa"
    
    def test_export_json_creates_directory(self, generator):
        """Test that JSON export creates missing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "subdir" / "flashcards.json"
            words = [("rosa", 10)]
            
            generator.export_json(words, str(output_file))
            
            assert output_file.exists()


class TestExportInterface:
    """Tests for unified export interface."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data."""
        word_data = {"rosa": {"definition": "rose"}}
        word_frequencies = {"rosa": 10}
        return word_data, word_frequencies
    
    @pytest.fixture
    def generator(self, sample_data):
        """Create generator."""
        word_data, frequencies = sample_data
        return FlashcardGenerator(word_data, frequencies)
    
    def test_export_csv_format(self, generator):
        """Test export with CSV format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "flashcards.csv"
            words = [("rosa", 10)]
            
            generator.export(words, str(output_file), format='csv')
            
            assert output_file.exists()
    
    def test_export_json_format(self, generator):
        """Test export with JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "flashcards.json"
            words = [("rosa", 10)]
            
            generator.export(words, str(output_file), format='json')
            
            assert output_file.exists()
    
    def test_export_unknown_format(self, generator):
        """Test export with unknown format raises error."""
        words = [("rosa", 10)]
        with pytest.raises(ValueError):
            generator.export(words, "output.txt", format='unknown')


class TestTemplates:
    """Tests for template functionality."""
    
    def test_get_minimal_template(self):
        """Test getting minimal template."""
        template = FlashcardGenerator.get_template('minimal')
        assert template == TEMPLATE_MINIMAL
    
    def test_get_comprehensive_template(self):
        """Test getting comprehensive template."""
        template = FlashcardGenerator.get_template('comprehensive')
        assert template == TEMPLATE_COMPREHENSIVE
    
    def test_get_unknown_template(self):
        """Test getting unknown template raises error."""
        with pytest.raises(ValueError):
            FlashcardGenerator.get_template('unknown')
