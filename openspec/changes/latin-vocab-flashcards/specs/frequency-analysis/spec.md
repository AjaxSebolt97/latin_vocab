## ADDED Requirements

### Requirement: Calculate word frequency statistics
The system SHALL count the occurrences of each word in the input text and calculate frequency statistics (total count, percentage of total words, rank by frequency).

#### Scenario: Identify most frequent words
- **WHEN** analyzing a text with 100 words where "et" appears 10 times
- **THEN** the system identifies "et" as appearing 10 times (10% of total words) and ranks it by frequency

#### Scenario: Handle single-occurrence words
- **WHEN** the text contains words that appear only once
- **THEN** the system includes them in the frequency analysis with a count of 1

### Requirement: Sort and filter by frequency
The system SHALL provide functionality to sort vocabulary by frequency and filter based on configurable thresholds.

#### Scenario: Sort words by frequency descending
- **WHEN** the user requests a frequency-sorted list
- **THEN** the system returns words ordered from highest to lowest frequency count

#### Scenario: Filter by minimum frequency threshold
- **WHEN** the user specifies a minimum frequency threshold (e.g., "only words appearing 3+ times")
- **THEN** the system filters the vocabulary list to include only words meeting that threshold

#### Scenario: Filter by frequency percentile
- **WHEN** the user requests the "top 100 most frequent words" or "words in top 50% of frequency"
- **THEN** the system returns the appropriate subset of vocabulary

### Requirement: Generate frequency report
The system SHALL produce a detailed frequency report showing word rankings, counts, and percentage distribution.

#### Scenario: Produce text frequency report
- **WHEN** analysis is complete
- **THEN** the system generates a report showing words ranked by frequency with occurrence counts and percentages

### Requirement: Group related word forms
The system SHALL optionally normalize different grammatical forms of the same lemma and combine their frequencies.

#### Scenario: Optionally combine lemma frequencies
- **WHEN** lemma normalization is enabled
- **THEN** different forms of the same word (e.g., nominative "puella", ablative "puellae") are counted together with combined frequency

#### Scenario: Preserve word forms when normalization disabled
- **WHEN** lemma normalization is disabled
- **THEN** each word form is counted separately as its own vocabulary entry
