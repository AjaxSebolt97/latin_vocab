"""
Flashcard generator module for creating flashcards from vocabulary data.

Provides functionality to export vocabulary as flashcards in CSV and JSON formats
with customizable templates and filtering options.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# Flashcard templates
TEMPLATE_MINIMAL = ['word', 'definition']
TEMPLATE_COMPREHENSIVE = ['word', 'lemma', 'definition', 'part_of_speech', 'frequency', 'grammatical_info']


class FlashcardGenerator:
    """Generator for creating flashcards from vocabulary data."""
    
    def __init__(self, word_data: Dict[str, Dict[str, Any]], word_frequencies: Dict[str, int]):
        """
        Initialize the flashcard generator.
        
        Args:
            word_data: Dictionary mapping words to their API data
            word_frequencies: Dictionary mapping words to their frequency counts
        """
        self.word_data = word_data
        self.word_frequencies = word_frequencies
    
    def _escape_csv_field(self, field: Optional[str]) -> str:
        """Escape special characters in CSV fields."""
        if field is None:
            return ""
        
        field_str = str(field)
        
        # Escape quotes and wrap in quotes if necessary
        if ',' in field_str or '"' in field_str or '\n' in field_str:
            field_str = field_str.replace('"', '""')
            field_str = f'"{field_str}"'
        
        return field_str
    
    def _build_flashcard_record(self, word: str, template: List[str]) -> Dict[str, str]:
        """
        Build a flashcard record for a word based on template.
        
        Args:
            word: The word
            template: List of field names to include
            
        Returns:
            Dictionary with flashcard data
        """
        word_info = self.word_data.get(word, {})
        frequency = self.word_frequencies.get(word, 1)
        
        record = {}
        for field in template:
            if field == 'word':
                record['word'] = word
            elif field == 'lemma':
                record['lemma'] = word_info.get('lemma', '')
            elif field == 'definition':
                record['definition'] = word_info.get('definition', '')
            elif field == 'part_of_speech':
                record['part_of_speech'] = word_info.get('part_of_speech', '')
            elif field == 'frequency':
                record['frequency'] = str(frequency)
            elif field == 'grammatical_info':
                record['grammatical_info'] = word_info.get('grammatical_info', '')
        
        return record
    
    def generate_flashcards(self, words: List[Tuple[str, int]], 
                           template: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Generate flashcard records for a list of words.
        
        Args:
            words: List of (word, frequency) tuples
            template: List of field names (default: TEMPLATE_COMPREHENSIVE)
            
        Returns:
            List of flashcard dictionaries
        """
        if template is None:
            template = TEMPLATE_COMPREHENSIVE
        
        flashcards = []
        for word, _ in words:
            record = self._build_flashcard_record(word, template)
            flashcards.append(record)
        
        return flashcards
    
    def export_csv(self, words: List[Tuple[str, int]], output_path: str,
                   template: Optional[List[str]] = None):
        """
        Export flashcards to CSV format.
        
        Args:
            words: List of (word, frequency) tuples
            output_path: Path to write CSV file
            template: List of field names (default: TEMPLATE_COMPREHENSIVE)
            
        Raises:
            IOError: If file cannot be written
        """
        if template is None:
            template = TEMPLATE_COMPREHENSIVE
        
        flashcards = self.generate_flashcards(words, template)
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=template)
                writer.writeheader()
                writer.writerows(flashcards)
            
            logger.info(f"Exported {len(flashcards)} flashcards to CSV: {output_path}")
            
        except IOError as e:
            logger.error(f"Failed to export CSV: {e}")
            raise
    
    def export_json(self, words: List[Tuple[str, int]], output_path: str,
                    template: Optional[List[str]] = None):
        """
        Export flashcards to JSON format.
        
        Args:
            words: List of (word, frequency) tuples
            output_path: Path to write JSON file
            template: List of field names (default: TEMPLATE_COMPREHENSIVE)
            
        Raises:
            IOError: If file cannot be written
        """
        if template is None:
            template = TEMPLATE_COMPREHENSIVE
        
        flashcards = self.generate_flashcards(words, template)
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(flashcards, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {len(flashcards)} flashcards to JSON: {output_path}")
            
        except IOError as e:
            logger.error(f"Failed to export JSON: {e}")
            raise
    
    def export(self, words: List[Tuple[str, int]], output_path: str, 
               format: str = 'csv', template: Optional[List[str]] = None):
        """
        Export flashcards in specified format.
        
        Args:
            words: List of (word, frequency) tuples
            output_path: Path to write output file
            format: Export format ('csv' or 'json')
            template: List of field names
            
        Raises:
            ValueError: If format is not recognized
            IOError: If file cannot be written
        """
        format_lower = format.lower()
        
        if format_lower == 'csv':
            self.export_csv(words, output_path, template)
        elif format_lower == 'json':
            self.export_json(words, output_path, template)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'csv' or 'json'")
    
    @staticmethod
    def get_template(template_name: str) -> List[str]:
        """
        Get a predefined flashcard template.
        
        Args:
            template_name: Template name ('minimal' or 'comprehensive')
            
        Returns:
            List of field names for the template
            
        Raises:
            ValueError: If template is not recognized
        """
        templates = {
            'minimal': TEMPLATE_MINIMAL,
            'comprehensive': TEMPLATE_COMPREHENSIVE
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        return templates[template_name]
