# Task Checklist

## Discovery
- [x] Review SpecKit repository to understand templates, commands, and CLI requirements.
- [x] Decide how SpecKit artifacts map to existing OpenSpec files.

## Implementation
- [x] Copy SpecKit command and supporting templates into `.speckit/`.
- [x] Add `scripts/speckit_check.py` to surface prerequisites and next steps.
- [x] Create `docs/spec-kit.md` describing CLI usage and manual flow.
- [x] Update `README.md` and `openspec/AGENTS.md` to reference the immersive workflow.
- [x] Add a one-step launcher script (`./speckit`) for quick starts.

## Testing & Validation
- [x] Run `python scripts/speckit_check.py` and confirm output.
- [x] Run `python3 -m unittest discover` (already green post-change).
- [x] Validate change: `openspec validate add-speckit-immersion --strict`.
