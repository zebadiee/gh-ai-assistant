## ADDED Requirements

### Requirement: Token Recycler Orchestrates Cache-First Responses
The system MUST expose a token recycler service that performs semantic cache lookups before invoking OpenRouter and records results back into shared metrics stores.

#### Scenario: Cache hit serves stored completion
- **GIVEN** a prior request whose prompt hash exists in `~/.gh-ai-assistant/token_cache.db`
- **WHEN** the CLI issues the same prompt through the token recycler service
- **THEN** the assistant returns the cached completion without calling the OpenRouter API
- **AND** the cache hit is appended to the recycler metrics with the associated model identifier

#### Scenario: Cache miss falls back to API and records usage
- **GIVEN** a prompt that is not yet cached for the selected model
- **WHEN** the token recycler handles the request
- **THEN** it invokes OpenRouter via the provided API adapter
- **AND** writes the resulting usage to both recycler metrics and the `TokenManager` usage ledger

### Requirement: Token Recycler Maintains Storage Hygiene
The system MUST provide a maintenance entry point (library function and CLI flag) to prune expired cache entries and vacuum the recycler databases without manual SQLite commands.

#### Scenario: Maintenance run prunes expired cache rows
- **GIVEN** cached responses older than the configured maximum age
- **WHEN** an operator runs the recycler maintenance helper
- **THEN** rows exceeding the age threshold are removed from the cache database
- **AND** the database file is vacuumed to reclaim disk space
