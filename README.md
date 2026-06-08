# Latin Vocab - Latin Vocabulary Flashcard Generator

A tool that reads Latin texts, identifies the most commonly used words, and generates flashcards for study. Integrates with Whitaker's Words API to retrieve accurate definitions and grammatical information.

## Features

- **Text Parsing**: Extract and normalize words from Latin texts with support for UTF-8 and Latin-1 encodings
- **Word Frequency Analysis**: Identify the most common vocabulary in your text
- **Whitaker's Words Integration**: Automatically look up definitions and grammatical information
- **Smart Caching**: Cache API responses locally to speed up subsequent runs
- **Flashcard Export**: Generate flashcards in CSV or JSON formats compatible with Anki, Quizlet, and other study tools
- **Flexible Filtering**: Filter vocabulary by frequency threshold or top N words
- **Customizable Templates**: Choose between minimal (word + definition) or comprehensive (includes lemma, part of speech, frequency)

## Project Structure

```
latin_vocab/
├── main.py                 # Entry point with CLI and file dialogs
├── src/                    # Core application modules
│   ├── __init__.py
│   ├── config.py          # Configuration and settings
│   ├── logging_config.py  # Logging setup
│   ├── text_parser.py     # Text parsing and normalization
│   ├── whitaker_api.py    # Whitaker Words API integration
│   ├── frequency_analysis.py  # Word frequency analysis
│   └── flashcard_generator.py # Flashcard export
├── tests/                  # Test suite (140+ tests)
│   ├── __init__.py
│   ├── test_text_parser.py
│   ├── test_whitaker_api.py
│   ├── test_frequency_analysis.py
│   ├── test_flashcard_generator.py
│   └── test_integration.py
├── inputs/                 # Sample input files
│   └── sample_text.txt
├── outputs/                # Generated output files
│   └── sample_output.csv
├── pyproject.toml          # Project configuration
└── README.md
```

## Installation

### Requirements
- Python 3.11 or higher
- uv (recommended) or pip for package management

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd latin_vocab
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies using uv:
```bash
uv pip install -e .
```

Or with pip:
```bash
pip install -e .
```

For development (with test dependencies):
```bash
uv pip install -e ".[dev]"
```

## Usage

### Basic Usage

The tool now uses interactive file dialogs for selecting input and output files:

```bash
python main.py
```

This will:
1. Open a file browser to select your Latin text file
2. Open a save dialog to choose where to save the flashcards

### Running from the Virtual Environment

Make sure the virtual environment is activated before running:

```bash
.venv\Scripts\python main.py  # Windows
# or
source .venv/bin/activate && python main.py  # macOS/Linux
```

### Command-Line Options

```
positional arguments:
  input_file            Path to input Latin text file
  output_file           Path to write flashcard output file

options:
  --format {csv,json}           Output format (default: csv)
  --template {minimal,comprehensive}  Flashcard template (default: comprehensive)
  --min-frequency MIN_FREQUENCY  Minimum word frequency threshold
  --top-n TOP_N                  Limit to top N most frequent words
  --encoding ENCODING            Text file encoding (default: utf-8)
  --log-level {DEBUG,INFO,WARNING,ERROR}  Logging level (default: INFO)
  --quiet                        Suppress progress messages
  --clear-cache                  Clear API cache before running
```

### Examples

**Generate CSV flashcards for top 100 words:**
```bash
python main.py latin_text.txt flashcards.csv --top-n 100
```

**Generate flashcards only for words appearing 5+ times:**
```bash
python main.py latin_text.txt flashcards.csv --min-frequency 5
```

**Export as JSON with minimal template:**
```bash
python main.py latin_text.txt flashcards.json --format json --template minimal
```

**Debug output with verbose logging:**
```bash
python main.py latin_text.txt flashcards.csv --log-level DEBUG
```

**Clear cached definitions and regenerate:**
```bash
python main.py latin_text.txt flashcards.csv --clear-cache
```

## Output Formats

### CSV Format

Columns: word, lemma, definition, part_of_speech, frequency, grammatical_info

Compatible with:
- Excel/Google Sheets
- Anki (import as Basic Note Type)
- Quizlet
- SuperMemory

### JSON Format

Structured format with complete word metadata:
```json
[
  {
    "word": "rosa",
    "lemma": "rosa",
    "definition": "rose",
    "part_of_speech": "noun",
    "frequency": "10",
    "grammatical_info": "1st decl"
  }
]
```

## Architecture

The tool follows a modular pipeline architecture:

```
Input Text
    ↓
[text_parser] → Extract and normalize words
    ↓
[frequency_analysis] → Calculate word frequencies
    ↓
[whitaker_api] → Look up definitions (with caching)
    ↓
[flashcard_generator] → Generate and export flashcards
    ↓
Output File (CSV or JSON)
```

### Modules

- **text_parser.py**: Text parsing and word extraction
- **whitaker_api.py**: Whitaker's Words API integration with local caching
- **frequency_analysis.py**: Word frequency analysis and filtering
- **flashcard_generator.py**: Flashcard generation and export
- **config.py**: Configuration and constants
- **logging_config.py**: Logging setup
- **main.py**: CLI interface and orchestration

## Configuration

### API Cache

The tool caches API responses in `~/.latin_vocab/api_cache/`. Cache entries expire after 30 days.

To clear the cache:
```bash
python main.py input.txt output.csv --clear-cache
```

### Logging

Logs are written to `~/.latin_vocab/logs/latin_vocab.log`. Control the log level with `--log-level`:

```bash
python main.py input.txt output.csv --log-level DEBUG
```

## Performance

- **First run**: Slower due to API lookups. Processing time depends on text size and API rate limits.
- **Subsequent runs**: Much faster due to caching. Same vocabulary across texts reuses cached definitions.
- **Rate limiting**: The tool implements request throttling (0.5s between requests) and retry logic with exponential backoff to respect API rate limits.

### Typical Performance

- Parsing: ~100-1000 words per second
- API lookups: ~2 words per second (with throttling)
- Flashcard generation: ~1000 flashcards per second

For a typical 5000-word text with 500 unique words:
- **First run**: ~5 minutes (API lookups are rate-limited)
- **Second run**: ~30 seconds (uses cached data)

## API Rate Limits

Whitaker's Words API has rate limits. The tool:
- Throttles requests (0.5s between requests)
- Implements retry logic with exponential backoff
- Caches responses locally to minimize API calls
- Logs warnings for unrecognized words

If you encounter rate limit errors:
1. Wait and retry later
2. Process fewer words at a time
3. Use the `--clear-cache` option less frequently

## Troubleshooting

### "File not found: input.txt"
Ensure the input file exists and the path is correct.

### "Failed to decode file" error
Try specifying the correct encoding:
```bash
python main.py input.txt output.csv --encoding latin-1
```

### API lookups are slow
The tool throttles API requests to avoid rate limiting. This is normal. Subsequent runs will be much faster due to caching.

### "API request failed" warnings
Some words may not be recognized by Whitaker's Words (e.g., proper nouns, very rare words). The tool logs these as warnings and continues processing. Check the log file for details.

### Out of memory on large texts
Process the text in smaller chunks or use the `--top-n` option to limit flashcard generation.

## Testing

Run unit tests:
```bash
pytest test_*.py -v
```

Run integration tests:
```bash
pytest test_integration.py -v
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Development

### Adding New Modules

1. Create a new Python module in the root directory
2. Add appropriate tests in `test_<module>.py`
3. Update `main.py` to integrate if needed
4. Update documentation

### Extending Functionality

- **New export formats**: Extend `flashcard_generator.py`
- **New data sources**: Create new API clients alongside `whitaker_api.py`
- **New filtering options**: Extend `frequency_analysis.py`
- **New text preprocessing**: Extend `text_parser.py`

## Limitations

- **Latin-only**: Currently supports only Latin text
- **API-dependent**: Requires internet connection for first run (cached after)
- **Unrecognized words**: Proper nouns and very rare words may not be found
- **CLI-only**: No graphical user interface
- **No persistent storage**: Flashcard sets are not stored; generate new ones each run

## Future Enhancements

- Web UI for easier interaction
- Support for multiple languages
- Spaced repetition scheduling
- User-configurable dictionary backends
- Anki deck generation (direct `.apkg` export)
- Text preprocessing (lemmatization, stemming)
- Frequency comparison across multiple texts

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues, feature requests, or questions:
- Check existing logs in `~/.latin_vocab/logs/`
- Run with `--log-level DEBUG` for detailed debugging
- Review the code and tests for implementation details

## Acknowledgments

- Whitaker's Words API for Latin word data and definitions
- Latin grammar reference sources

