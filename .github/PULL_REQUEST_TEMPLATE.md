# Pull Request Template

Provide enough context to review safely and quickly. Link your OpenSpec change and any SpecKit artifacts.

## Summary
- What’s changing and why? (1–3 sentences)

## OpenSpec Change(s)
- Change ID(s):
- Links:
  - `openspec/changes/<id>/proposal.md`
  - `openspec/changes/<id>/design.md` (if present)
  - `openspec/changes/<id>/tasks.md`
  - Delta specs under `openspec/changes/<id>/specs/*/spec.md`

## Assumptions and Signals
- Assumptions (what must remain true):
- Signals to watch (metrics, feedback, constraints):

## Decision Log and Pivot Plan
- Decision log (if used): `openspec/changes/<id>/decision-log.md`
- Pivot plan (if used): `openspec/changes/<id>/pivot.md`

## Success and Kill Criteria
- Success criteria (measurable):
- Kill/stop criteria (predefined):

## Tasks and Validation
- Key tasks completed (from `tasks.md`):
- Validation output: `openspec validate <id> --strict` result:
- Additional tests/checks:

## Breaking Changes
- Does this introduce breaking changes? If yes, describe impact and migration:

## Risks / Mitigations
- Risks:
- Mitigations:

## Checklist
- [ ] Proposal reviewed and approved
- [ ] Delta specs updated with scenarios
- [ ] `openspec validate <id> --strict` passes
- [ ] Tasks updated to reflect reality
- [ ] Docs updated (README/Guides if applicable)
