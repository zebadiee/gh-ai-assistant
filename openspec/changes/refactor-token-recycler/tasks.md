# Task Checklist

## Discovery
- [x] Audit current cache + metrics paths in `token_optimizer.py` and `gh_ai_core.py` to confirm integration points.
- [x] Confirm migration strategy for existing `token_cache.db` and `token_metrics.db` files.

## Implementation
- [x] Extract shared constants and helper functions into `token_recycler/config.py`.
- [x] Implement `TokenRecyclerService` with cache-first lookup, API fallback hooks, and adapter calls into `TokenManager`.
- [ ] Replace direct optimizer usage in CLI entry points with the new service wrapper.
- [ ] Add maintenance helper/CLI flag that prunes expired cache rows and vacuums databases.

## Testing & Validation
- [ ] Create unit tests for recycler cache hit/miss flows and cleanup routines using temporary SQLite files.
- [ ] Update integration tests or smoke scripts to cover cache reuse and cleanup invocation.
- [ ] Run `python -m unittest discover` and CLI smoke commands to verify no regressions.
