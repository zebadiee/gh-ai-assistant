## Context
This design accompanies a minimal demo change to illustrate the OpenSpec validation flow from PowerShell and how SpecKit artifacts map into change proposals.

## Goals / Non-Goals
- Goals: Show structure (proposal, tasks, delta spec), enable strict validation, document the rationale.
- Non-Goals: No product behavior changes, no code migration.

## Decisions
- Use a single capability folder `specs/platform/` for the demo delta.
- Keep scenarios concise and focused on validation behavior.
- Treat this as tooling-only; safe to archive after demonstration.

## Risks / Trade-offs
- Minimal content may under-represent real-world complexity; mitigated by adding multiple scenarios.

## Migration Plan
- None required. After demonstration, archive with `openspec archive add-demo-openspec-flow --skip-specs`.

## Open Questions
- None.

