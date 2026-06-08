"""
Main CLI interface for Latin Vocab tool.

Provides command-line interface for parsing Latin text, analyzing vocabulary,
and generating flashcards.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional
from tkinter import Tk, filedialog

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import logging_config
import config
import text_parser
import whitaker_api
import frequency_analysis
import flashcard_generator

logger = logging_config.get_logger(__name__)


class LatinVocabTool:
    """Main tool for processing Latin vocabulary and generating flashcards."""
    
    def __init__(self):
        """Initialize the tool."""
        self.api_client = whitaker_api.WhitakerAPIClient()
    
    def parse_latin_text(self, input_file: str, encoding: str = 'utf-8') -> dict:
        """
        Parse a Latin text file.
        
        Args:
            input_file: Path to the input text file
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with parse results
            
        Raises:
            FileNotFoundError: If input file not found
        """
        logger.info(f"Parsing text file: {input_file}")
        
        try:
            word_counts = text_parser.parse_file(input_file, encoding=encoding)
            total_words = text_parser.get_total_word_count(word_counts)
            unique_words = len(word_counts)
            
            logger.info(f"Parsed {total_words} words, {unique_words} unique")
            
            return {
                'word_counts': word_counts,
                'total_words': total_words,
                'unique_words': unique_words
            }
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            raise
    
    def lookup_vocabulary(self, words: list) -> dict:
        """
        Look up words in Whitaker's Words API.
        
        Args:
            words: List of words to look up
            
        Returns:
            Dictionary mapping words to their lookup results
        """
        logger.info(f"Looking up {len(words)} unique words")
        
        results = {}
        for i, word in enumerate(words, 1):
            if i % 10 == 0:
                logger.debug(f"Progress: {i}/{len(words)} words looked up")
            
            result = self.api_client.lookup_word(word)
            results[word] = result
        
        logger.info(f"Completed {len(results)} word lookups")
        return results
    
    def analyze_frequency(self, word_counts: dict, 
                        min_frequency: Optional[int] = None,
                        top_n: Optional[int] = None) -> list:
        """
        Analyze word frequencies and filter.
        
        Args:
            word_counts: Dictionary of word counts
            min_frequency: Minimum frequency threshold (optional)
            top_n: Get top N words (optional)
            
        Returns:
            List of (word, count) tuples
        """
        logger.info("Analyzing word frequencies")
        
        analyzer = frequency_analysis.FrequencyAnalyzer(word_counts)
        
        if top_n is not None:
            logger.info(f"Filtering to top {top_n} words")
            return analyzer.filter_by_top_n(top_n)
        elif min_frequency is not None:
            logger.info(f"Filtering to minimum frequency {min_frequency}")
            return analyzer.filter_by_minimum_count(min_frequency)
        else:
            logger.info("No filtering applied")
            return analyzer.get_sorted_by_frequency()
    
    def generate_flashcards(self, words: list, word_data: dict,
                          word_counts: dict, output_file: str,
                          format: str = 'csv',
                          template: str = 'comprehensive') -> None:
        """
        Generate flashcards and export.
        
        Args:
            words: List of (word, count) tuples
            word_data: Dictionary mapping words to their API data
            word_counts: Dictionary of word frequencies
            output_file: Path to write flashcards
            format: Export format ('csv' or 'json')
            template: Template name ('minimal' or 'comprehensive')
            
        Raises:
            ValueError: If format or template is invalid
            IOError: If write fails
        """
        logger.info(f"Generating {len(words)} flashcards")
        
        try:
            generator = flashcard_generator.FlashcardGenerator(word_data, word_counts)
            
            # Get template
            template_fields = flashcard_generator.FlashcardGenerator.get_template(template)
            
            # Export
            generator.export(words, output_file, format=format, template=template_fields)
            
            logger.info(f"Flashcards exported to: {output_file}")
        except (ValueError, IOError) as e:
            logger.error(f"Failed to generate flashcards: {e}")
            raise
    
    def run_pipeline(self, input_file: str, output_file: str,
                    min_frequency: Optional[int] = None,
                    top_n: Optional[int] = None,
                    format: str = 'csv',
                    template: str = 'comprehensive',
                    encoding: str = 'utf-8',
                    progress: bool = True) -> None:
        """
        Run the complete pipeline: parse → lookup → analyze → generate.
        
        Args:
            input_file: Path to input Latin text file
            output_file: Path to write flashcards
            min_frequency: Minimum word frequency filter (optional)
            top_n: Top N words filter (optional)
            format: Flashcard export format
            template: Flashcard template
            encoding: File encoding
            progress: Show progress messages
        """
        try:
            # Step 1: Parse text
            if progress:
                print("📖 Parsing Latin text...")
            parse_result = self.parse_latin_text(input_file, encoding=encoding)
            word_counts = parse_result['word_counts']
            if progress:
                print(f"   {parse_result['total_words']} total words, {parse_result['unique_words']} unique")
            
            # Step 2: Analyze frequency
            if progress:
                print("📊 Analyzing word frequencies...")
            filtered_words = self.analyze_frequency(word_counts, 
                                                   min_frequency=min_frequency,
                                                   top_n=top_n)
            if progress:
                print(f"   {len(filtered_words)} words selected")
            
            # Step 3: Look up vocabulary
            if progress:
                print("🔍 Looking up word definitions...")
            word_list = [word for word, _ in filtered_words]
            word_data_result = self.lookup_vocabulary(word_list)
            
            # Step 4: Generate flashcards
            if progress:
                print(f"📝 Generating flashcards ({format})...")
            self.generate_flashcards(filtered_words, word_data_result, word_counts,
                                    output_file, format=format, template=template)
            
            if progress:
                print(f"✅ Done! Flashcards saved to: {output_file}")
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            if progress:
                print(f"❌ Error: {e}")
            raise


def pick_input_file() -> Optional[str]:
    """
    Open a file dialog for the user to select an input file.
    
    Returns:
        Path to selected file, or None if cancelled
    """
    root = Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select Latin Text File",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    root.destroy()
    
    return file_path if file_path else None


def pick_output_file(default_format: str = 'csv') -> Optional[str]:
    """
    Open a file dialog for the user to select output file location.
    
    Args:
        default_format: Default file format (csv or json)
    
    Returns:
        Path for output file, or None if cancelled
    """
    filetypes = [
        ("CSV Files", "*.csv"),
        ("JSON Files", "*.json"),
        ("All Files", "*.*")
    ]
    
    root = Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.asksaveasfilename(
        title="Save Flashcards As",
        filetypes=filetypes,
        defaultextension=f".{default_format}"
    )
    root.destroy()
    
    return file_path if file_path else None


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Latin vocabulary flashcard generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate CSV flashcards (will prompt for files via dialog)
  python main.py
  
  # Generate top 100 words only
  python main.py --top-n 100
  
  # Generate words appearing at least 5 times
  python main.py --min-frequency 5
  
  # Export as JSON with minimal template
  python main.py --format json --template minimal
        """
    )
    
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--template', choices=['minimal', 'comprehensive'], 
                       default='comprehensive',
                       help='Flashcard template (default: comprehensive)')
    
    parser.add_argument('--min-frequency', type=int, default=None,
                       help='Minimum word frequency threshold')
    parser.add_argument('--top-n', type=int, default=None,
                       help='Limit to top N most frequent words')
    
    parser.add_argument('--encoding', default='utf-8',
                       help='Text file encoding (default: utf-8)')
    
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Logging level (default: INFO)')
    
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress progress messages')
    
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear API cache before running')
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logging_config.setup_logging(level=args.log_level)
    logger.info("Latin Vocab Tool started")
    
    # Ask user to select input file
    print("Opening file browser to select Latin text file...")
    input_file = pick_input_file()
    
    if not input_file:
        print("No file selected. Exiting.")
        sys.exit(0)
    
    # Check input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Ask user to select output file location
    print("Opening file browser to select output file location...")
    output_file = pick_output_file(default_format=args.format)
    
    if not output_file:
        print("No output file selected. Exiting.")
        sys.exit(0)
    
    # Clear cache if requested
    if args.clear_cache:
        logger.info("Clearing API cache")
        api_client = whitaker_api.WhitakerAPIClient()
        api_client.clear_cache()
    
    # Run pipeline
    try:
        tool = LatinVocabTool()
        tool.run_pipeline(
            input_file,
            output_file,
            min_frequency=args.min_frequency,
            top_n=args.top_n,
            format=args.format,
            template=args.template,
            encoding=args.encoding,
            progress=not args.quiet
        )
        logger.info("Completed successfully")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
