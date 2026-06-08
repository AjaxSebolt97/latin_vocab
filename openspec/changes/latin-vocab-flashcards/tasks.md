## 1. Project Setup and Dependencies

- [x] 1.1 Create module structure (text_parser.py, whitaker_api.py, frequency_analysis.py, flashcard_generator.py)
- [x] 1.2 Add required dependencies to pyproject.toml (requests for API calls, any CSV/JSON utilities)
- [x] 1.3 Create configuration file structure for API cache directory and settings
- [x] 1.4 Set up logging configuration for all modules

## 2. Text Parser Module Implementation

- [x] 2.1 Implement word tokenization function that extracts words from text
- [x] 2.2 Implement punctuation removal and normalization (lowercasing, filtering)
- [x] 2.3 Implement word occurrence counting to preserve frequency data
- [x] 2.4 Add support for UTF-8 and Latin-1 file encoding with error handling
- [ ] 2.5 Create unit tests for text parsing edge cases (punctuation, encoding, empty input)

## 3. Whitaker Words API Integration

- [x] 3.1 Create API client class to query Whitaker Words API
- [x] 3.2 Implement local cache system with disk persistence (JSON cache storage)
- [x] 3.3 Add request throttling/batching to respect API rate limits
- [x] 3.4 Implement retry logic with exponential backoff for failed requests
- [x] 3.5 Handle missing words gracefully and log warnings for unresolved vocabulary
- [ ] 3.6 Create unit tests for API integration and cache behavior

## 4. Frequency Analysis Module

- [x] 4.1 Implement word frequency calculation (counts, percentages, rankings)
- [x] 4.2 Implement sorting by frequency (ascending/descending)
- [x] 4.3 Implement frequency threshold filtering (minimum count, percentile-based)
- [x] 4.4 Add optional lemma normalization to combine word form frequencies
- [x] 4.5 Generate frequency report output showing ranked vocabulary
- [ ] 4.6 Create unit tests for frequency calculations and filtering

## 5. Flashcard Generator Module

- [x] 5.1 Implement CSV export format with standard columns (word, definition, POS, frequency, lemma)
- [x] 5.2 Implement customizable flashcard templates (minimal vs. comprehensive)
- [x] 5.3 Implement filtering options for flashcard generation (top-N words, frequency threshold)
- [x] 5.4 Implement JSON export format for structured data
- [x] 5.5 Add validation and escaping for special characters in CSV/JSON output
- [x] 5.6 Handle missing definitions and edge cases gracefully
- [ ] 5.7 Create unit tests for flashcard generation and export formats

## 6. CLI Interface and Main Workflow

- [x] 6.1 Create main.py with CLI argument parsing (input file, output file, options)
- [x] 6.2 Implement main workflow orchestration: parse → lookup → analyze → generate
- [x] 6.3 Add configurable options (frequency threshold, flashcard format, template, lemma normalization)
- [x] 6.4 Implement progress reporting during processing
- [x] 6.5 Add error handling and user-friendly error messages
- [x] 6.6 Create help documentation and usage examples

## 7. Integration and End-to-End Testing

- [x] 7.1 Integration test: Parse text → API lookup → frequency analysis → CSV flashcard generation
- [x] 7.2 Integration test: Multiple output formats (CSV and JSON from same input)
- [x] 7.3 Integration test: Cache verification (verify cached data is reused on second run)
- [x] 7.4 Test with sample Latin texts to verify complete workflow

## 8. Documentation and Polish

- [x] 8.1 Write README with usage instructions and examples
- [x] 8.2 Document configuration options and environment setup
- [x] 8.3 Document API rate limits and caching behavior
- [x] 8.4 Add docstrings to all public functions and classes
- [x] 8.5 Review code for adherence to Python style guidelines
- [x] 8.6 Verify all tasks from specs are covered by implementation
