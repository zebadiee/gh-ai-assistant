# Change Proposal: Refactor Token Recycler

## Overview
- Unify caching, token accounting, and optimization logic into a dedicated token recycler service that is easy to integrate from both CLI commands and background monitors.
- Reduce duplication between `TokenManager` usage metrics and `TokenOptimizer` cache/metrics state while keeping user-facing behavior stable.

## Problem
- Cache logic in `token_optimizer.py` is tightly coupled to CLI usage flows and cannot be reused from monitoring scripts without re-instantiating the full optimizer stack.
- Token usage analytics live separately in `TokenManager` (`gh_ai_core.py`) and the optimizer metrics database, leading to inconsistent numbers and manual reconciliation.
- Cache eviction and cleanup tooling is manual; stale entries accumulate in `~/.gh-ai-assistant/token_cache.db` and degrade performance over time.

## Proposal
- Introduce a `TokenRecyclerService` abstraction that wraps cache lookup, API invocation, and metrics persistence with a single entry point that callers can inject.
- Move shared configuration (paths, cache TTLs, worker pools) into a `token_recycler/config.py` module consumed by both `TokenManager` and the recycler.
- Replace the current direct SQLite writes in `TokenOptimizer` with adapter methods that write usage deltas through `TokenManager` so daily limits remain accurate.
- Add scheduled maintenance helpers (CLI flag + library function) to reclaim expired cache rows and vacuum the database.

## Success Criteria
- CLI `gh_ai_core.py` flows can opt into the recycler via a thin wrapper without breaking existing commands.
- Cache hits are logged once and reflected in both the recycler metrics and `TokenManager` aggregates.
- Running the new cleanup helper removes expired cache rows and compacts both cache and metrics databases.
- Unit coverage exists for the recycler service, adapters, and cleanup paths with mocks for network interactions.

## Risks & Mitigations
- **Risk:** Tight coupling between new service and existing classes could introduce circular imports.  
  **Mitigation:** Keep adapters interface-based and inject dependencies during initialization within `gh_ai_core.AIAssistant`.
- **Risk:** Migration of metrics paths could corrupt existing databases.  
  **Mitigation:** Provide idempotent upgrades that detect existing schema and migrate in-place with backups before altering tables.

## Validation Plan
- Add targeted unit tests for recycler flows (cache hit, cache miss, cleanup) using temporary SQLite files.
- Exercise CLI smoke tests (`python gh_ai_core.py stats`, `... ask`) with mocked API responses to confirm behavior stability.
- Manually inspect SQLite files after cleanup to ensure row counts drop and file size shrinks.
