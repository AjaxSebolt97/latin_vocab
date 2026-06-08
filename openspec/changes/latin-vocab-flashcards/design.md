## Context

The current project provides a foundation for Latin vocabulary learning. This change extends it by automating the process of analyzing Latin texts to identify high-frequency vocabulary and generate targeted study materials. Students currently must manually look up unfamiliar words and create study aids. This design automates vocabulary analysis and flashcard generation from raw Latin text.

## Goals / Non-Goals

**Goals:**
- Enable users to upload or input Latin text and extract vocabulary data
- Integrate with Whitaker Words API to retrieve accurate word definitions and grammatical information
- Analyze word frequencies and identify the most commonly encountered vocabulary
- Generate flashcard sets suitable for import into study applications
- Provide a flexible, modular architecture for future enhancements

**Non-Goals:**
- Provide a web UI or GUI (CLI tool for initial implementation)
- Support languages other than Latin
- Store or manage persistent user data or flashcard collections
- Implement spaced repetition algorithms
- Build a complete study application (only generate flashcards)

## Decisions

**Decision 1: Whitaker Words API Integration**
- **Choice**: Use the Whitaker Words API for word lookups
- **Rationale**: Whitaker's Words is the standard for Latin word analysis and requires no authentication, making it ideal for this use case
- **Alternatives Considered**: 
  - Build a custom Latin dictionary (too much maintenance, less accurate)
  - Use commercial APIs (expensive, adds dependencies)

**Decision 2: Architecture - Modular Pipeline**
- **Choice**: Implement as a series of independent modules: Parser → API Lookup → Frequency Analysis → Flashcard Generation
- **Rationale**: Allows each component to be tested, modified, and reused independently. Enables future enhancements like caching, batching, or alternative output formats
- **Alternatives Considered**:
  - Monolithic script (harder to test and extend)
  - Single class with all logic (tight coupling)

**Decision 3: Whitaker API Caching**
- **Choice**: Cache API responses locally to reduce API calls and improve performance on repeated runs
- **Rationale**: The same vocabulary appears across multiple texts; caching avoids redundant requests
- **Alternatives Considered**:
  - No caching (slower, higher API load)
  - Database backend (overcomplicated for initial version)

**Decision 4: Flashcard Format**
- **Choice**: Generate flashcards in CSV format initially, with extensible design for JSON and other formats
- **Rationale**: CSV is widely supported by flashcard applications (Anki, Quizlet), requires minimal dependencies, and is human-readable for debugging
- **Alternatives Considered**:
  - JSON only (less compatible with existing tools)
  - Direct Anki deck format (tight coupling to one tool)

**Decision 5: Error Handling and Robustness**
- **Choice**: Gracefully handle missing or malformed data; log warnings but continue processing
- **Rationale**: Whitaker API may not recognize all words (e.g., proper nouns, variant forms); processing should continue rather than halt
- **Alternatives Considered**:
  - Strict validation with error halting (too restrictive)
  - Silent failure (difficult to debug)

## Risks / Trade-offs

**[Risk]** Whitaker Words API is external and could become unavailable
- **Mitigation**: Implement local caching with disk persistence. Users can still work with previously-cached vocabulary offline.

**[Risk]** API rate limiting could affect processing of very large texts
- **Mitigation**: Implement request batching and rate-limiting logic. Document expected processing times. Users can run analysis in chunks if needed.

**[Risk]** Proper nouns, archaic forms, and variant spellings may not be recognized by Whitaker API
- **Mitigation**: Provide warnings in output. Allow users to manually add custom vocabulary entries for unrecognized words.

**[Risk]** CSV format may lose grammatical metadata that could be useful for study
- **Mitigation**: Design CSV with multiple columns for word, lemma, part of speech, frequency. Support JSON export for users needing richer data.

**[Trade-off]** Simplicity vs. Feature Richness
- CLI-only initially (simpler) vs. Web UI (more accessible but more complex)
- Chosen: CLI initially; UI can be added later as non-goal

## Open Questions

1. Should the tool support analyzing multiple texts and comparing vocabulary across them?
2. Should there be user-configurable frequency thresholds or filtering rules?
3. Should the tool normalize different forms of the same word (e.g., nominative vs. ablative)?
4. What flashcard formats besides CSV should be prioritized for initial release?
