## ADDED Requirements

### Requirement: Parse text file to extract words
The system SHALL read Latin text from an input file, extract individual words by tokenizing on whitespace and punctuation, and produce a list of normalized words (lowercased, punctuation removed).

#### Scenario: Successfully parse simple Latin text
- **WHEN** a user provides a text file containing Latin words separated by whitespace
- **THEN** the system extracts each word, removes punctuation, converts to lowercase, and returns a list of words

#### Scenario: Handle punctuation correctly
- **WHEN** the input text contains Latin words with attached punctuation (e.g., "Romam.", "puellae,", "est?")
- **THEN** the system removes punctuation and returns the base word form

#### Scenario: Filter empty and whitespace-only tokens
- **WHEN** the input text contains multiple whitespace characters or empty tokens
- **THEN** the system filters them out and only returns non-empty words

### Requirement: Preserve word occurrence count
The system SHALL maintain the original count of how many times each word appears in the text, before any deduplication or normalization.

#### Scenario: Count word occurrences
- **WHEN** the input text contains the word "et" appearing 5 times
- **THEN** the system preserves that count as 5, not converting to a single entry

### Requirement: Support multiple input formats
The system SHALL accept text input from files with common encodings (UTF-8, Latin-1) and handle encoding errors gracefully.

#### Scenario: Read UTF-8 encoded text
- **WHEN** a user provides a UTF-8 encoded text file with Latin text
- **THEN** the system reads and parses it correctly

#### Scenario: Handle encoding errors
- **WHEN** a file has encoding issues or invalid characters
- **THEN** the system logs a warning and continues processing the valid portions
