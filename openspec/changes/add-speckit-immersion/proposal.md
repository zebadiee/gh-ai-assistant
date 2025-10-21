# Change Proposal: Add SpecKit Immersive Workflow

## Overview
- Bundle SpecKit prompts and templates directly in this repository.
- Provide helper tooling so any teammate can follow the `/speckit.*` flow without bespoke setup.
- Document how SpecKit maps onto the existing OpenSpec change process.

## Problem
- Contributors needed to install SpecKit separately and discover the workflow on their own.
- AI assistants lacked project-local command prompts, leading to inconsistent specs and plans.
- No helper existed to guide users through prerequisites (Python 3.11, `uv`, `pipx`) or to explain how SpecKit outputs map to OpenSpec artifacts.

## Proposal
- Vendor the SpecKit command and template files under `.speckit/`.
- Add `docs/spec-kit.md` and `scripts/speckit_check.py` to explain and validate the workflow.
- Update onboarding docs (`README`, `openspec/AGENTS.md`) to reference the new immersive flow.

## Success Criteria
- `.speckit/commands/*.md` and `.speckit/templates/*.md` exist in the repo.
- `python scripts/speckit_check.py` reports repository state and tooling guidance.
- Documentation clearly links the SpecKit flow with `openspec/changes/<change>/` artifacts.
- OpenSpec change validates with `openspec validate add-speckit-immersion --strict`.

## Risks & Mitigations
- **Risk:** Project drifts from upstream SpecKit templates.  
  **Mitigation:** Record source reference in docs and encourage periodic updates.
- **Risk:** Script expectations diverge for Windows users.  
  **Mitigation:** Keep helper script Python-based with no platform-specific commands.

## Validation Plan
- Run `python scripts/speckit_check.py` to confirm directories and guidance.
- Execute `python3 -m unittest discover` (already part of CI) to ensure no regressions.
- Validate new change via `openspec validate add-speckit-immersion --strict`.
