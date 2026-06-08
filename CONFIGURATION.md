# Configuration Guide

This document explains how to configure the Latin Vocab tool.

## Environment Variables

The tool respects the following environment variables:

### LATIN_VOCAB_LOG_LEVEL

Controls the logging level for the application.

**Possible values:** DEBUG, INFO, WARNING, ERROR

**Default:** INFO

**Usage:**
```bash
export LATIN_VOCAB_LOG_LEVEL=DEBUG
python main.py input.txt output.csv
```

## Configuration Files

### Application Directories

The tool creates the following directories in your home folder:

- `~/.latin_vocab/` - Main application directory
- `~/.latin_vocab/api_cache/` - API response cache (JSON files)
- `~/.latin_vocab/logs/` - Application logs

These directories are created automatically on first run.

### Configuration Module

Settings are defined in `config.py`:

```python
# API configuration
WHITAKER_API_URL = "https://www.whitakers-words.com/go"
API_CACHE_EXPIRATION_DAYS = 30
API_REQUEST_DELAY = 0.5  # Seconds between requests
API_RETRY_MAX_ATTEMPTS = 3
API_RETRY_BACKOFF_FACTOR = 2

# Logging
LOG_LEVEL = os.getenv("LATIN_VOCAB_LOG_LEVEL", "INFO")

# Flashcard defaults
DEFAULT_FLASHCARD_FORMAT = "csv"
DEFAULT_FLASHCARD_TEMPLATE = "comprehensive"
```

To modify these settings, edit `config.py` directly.

## Advanced Configuration

### Adjusting API Rate Limiting

If you experience rate limiting issues, adjust `API_REQUEST_DELAY` in `config.py`:

```python
API_REQUEST_DELAY = 1.0  # Increase delay between requests (in seconds)
```

Higher values slow down processing but reduce API rate limit issues.

### Cache Expiration

To change how long cached API responses are kept:

```python
API_CACHE_EXPIRATION_DAYS = 60  # Keep cache for 60 days instead of 30
```

### Retry Behavior

Adjust retry attempts and backoff factor for API failures:

```python
API_RETRY_MAX_ATTEMPTS = 5  # Try more times
API_RETRY_BACKOFF_FACTOR = 3  # Longer backoff between retries
```

## File Encoding

The tool supports the following text file encodings:

- **utf-8** (default): Modern standard
- **latin-1** (ISO-8859-1): Older texts and systems

Specify encoding with the `--encoding` option:

```bash
python main.py input.txt output.csv --encoding latin-1
```

## Logging Configuration

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO** (default): General informational messages
- **WARNING**: Warning messages for issues
- **ERROR**: Error messages only

### Log Output

Logs are written to `~/.latin_vocab/logs/latin_vocab.log`.

Log files are rotated when they exceed 10 MB, with 5 backups kept.

## Performance Tuning

### For Large Texts (10,000+ words)

Use frequency filtering to process smaller vocabulary sets:

```bash
python main.py large_text.txt output.csv --top-n 200
```

Or filter by frequency:

```bash
python main.py large_text.txt output.csv --min-frequency 3
```

This reduces API lookups and speeds up flashcard generation.

### For Batch Processing

Process multiple files with a script:

```bash
#!/bin/bash

for file in *.txt; do
    output="${file%.txt}_flashcards.csv"
    python main.py "$file" "$output" --top-n 100
done
```

## Troubleshooting Configuration Issues

### Cache not being used

Verify cache directory exists:
```bash
ls ~/.latin_vocab/api_cache/
```

Cache is stored as JSON files named after words (e.g., `rosa.json`).

### Log file not created

Verify log directory exists and is writable:
```bash
ls -la ~/.latin_vocab/
```

The directory should have read/write permissions.

### API timeouts

If you see timeout errors, increase the request delay in `config.py`:

```python
API_REQUEST_DELAY = 2.0
```

## Default Templates

### Comprehensive Template (default)

Includes all available information:
- word
- lemma
- definition
- part_of_speech
- frequency
- grammatical_info

### Minimal Template

Includes only essential fields:
- word
- definition

Use with `--template minimal`:

```bash
python main.py input.txt output.csv --template minimal
```

## Format-Specific Configuration

### CSV Export

The CSV file includes a header row with column names. Columns are tab-separated for better compatibility with Excel.

### JSON Export

The JSON file contains an array of flashcard objects. Each object includes all template fields with null values for missing data.

## Whitaker's Words API

### URL

The tool uses the public Whitaker's Words API:
```
https://www.whitakers-words.com/go?lookup=<word>
```

### API Documentation

See: https://www.whitakers-words.com/

### Rate Limits

- No official published rate limits
- Tool implements conservative throttling (0.5s between requests)
- Cache prevents redundant requests

## Next Steps

After configuration, see [README.md](README.md) for usage examples.
