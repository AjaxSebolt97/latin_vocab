## ADDED Requirements

### Requirement: Generate flashcards in CSV format
The system SHALL export analyzed vocabulary as flashcards in CSV format suitable for import into study applications.

#### Scenario: Create CSV flashcard file
- **WHEN** the user requests flashcard generation
- **THEN** the system produces a CSV file with columns for Latin word, English definition, part of speech, frequency, and lemma

#### Scenario: Include metadata in flashcard output
- **WHEN** generating flashcards
- **THEN** each flashcard includes: the Latin word, English definition, part of speech, word frequency count, and lemma form

### Requirement: Support customizable flashcard templates
The system SHALL allow users to customize which fields are included in the flashcard output.

#### Scenario: Include only essential fields
- **WHEN** the user specifies a minimal template (word, definition)
- **THEN** the system generates CSV with only those columns

#### Scenario: Include comprehensive grammatical information
- **WHEN** the user requests a full template
- **THEN** the system includes all available fields: word, lemma, definition, part of speech, frequency, and additional grammatical data

### Requirement: Filter and subset flashcard generation
The system SHALL allow users to generate flashcards for only a subset of vocabulary based on frequency criteria.

#### Scenario: Generate flashcards for top-frequency words
- **WHEN** the user specifies "top 100 words"
- **THEN** the system creates a flashcard deck containing only the 100 most frequently occurring words

#### Scenario: Generate flashcards with frequency threshold
- **WHEN** the user specifies a minimum frequency (e.g., "words appearing 5+ times")
- **THEN** the system creates flashcards only for words meeting that threshold

### Requirement: Export in multiple formats
The system SHALL support exporting flashcards in formats compatible with common study applications.

#### Scenario: Export as CSV for Quizlet/Excel
- **WHEN** the user requests CSV format
- **THEN** the system generates a standard CSV file compatible with Quizlet and spreadsheet applications

#### Scenario: Export as JSON for programmatic access
- **WHEN** the user requests JSON format
- **THEN** the system generates a JSON file with structured vocabulary and flashcard data

### Requirement: Ensure valid and clean flashcard data
The system SHALL validate and clean flashcard data before export, handling missing fields and encoding issues.

#### Scenario: Handle missing definitions
- **WHEN** a word has no definition from the API
- **THEN** the system includes the word with a placeholder or empty definition field, and logs the missing data

#### Scenario: Properly escape special characters
- **WHEN** flashcard content includes special characters (commas, newlines, quotes)
- **THEN** the system properly escapes them according to CSV/JSON format specifications
