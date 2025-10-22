# OpenSpec + SpecKit Cross-Platform Workflow

This repo supports a fast SpecKit drafting flow with formal OpenSpec validation on Windows, macOS, Linux, and WSL.

## Quick Start

- Draft with SpecKit
  - Run `/speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement` using `.speckit/commands/*`.
  - Produce: proposal (Why/What/Impact), tasks checklist, and delta specs with GIVEN/WHEN/THEN scenarios.

- Scaffold OpenSpec change from templates
  - PowerShell (Windows): `./scripts/speckit_map.ps1 -Id add-feature -Capability platform`
  - Bash (macOS/Linux/WSL): `./scripts/speckit_map.sh add-feature platform`
  - Generated files:
    - `openspec/changes/<id>/proposal.md`
    - `openspec/changes/<id>/tasks.md`
    - `openspec/changes/<id>/design.md` (omit with `--no-design` / `-NoDesign`)
    - `openspec/changes/<id>/specs/<capability>/spec.md`

- Validate
  - `openspec validate <id> --strict`
  - Iterate until clean; ensure each requirement has at least one scenario.

- Approval, implement, archive
  - Get the proposal approved, implement changes, mark tasks as complete.
  - Archive after deployment: `openspec archive <id> --yes` (use `--skip-specs` for tooling-only changes).

## Scripts and Templates

- PowerShell: `scripts/speckit_map.ps1`
  - Flags: `-NoDesign`, `-Force`

- Bash: `scripts/speckit_map.sh`
  - Flags: `--no-design`, `--force`

- Templates (shared by both):
  - `.speckit/templates/openspec/proposal-skeleton.md`
  - `.speckit/templates/openspec/tasks-skeleton.md`
  - `.speckit/templates/openspec/design-skeleton.md`
  - `.speckit/templates/openspec/delta-spec-skeleton.md`

## Tips

- Use relative paths; both scripts are IDE-friendly (VS Code / LM Studio).
- Use Markdown preview for proposal, tasks, design, and spec files.
- Prefer modifying existing capabilities over duplicates; see `openspec/AGENTS.md` for rules.

