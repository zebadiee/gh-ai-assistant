## ADDED Requirements

### Requirement: Repo Provides SpecKit Assets
The repository MUST ship SpecKit templates and helper tooling so contributors can run the `/speckit.*` workflow without external setup.

#### Scenario: Command templates are available
- **GIVEN** a fresh clone of the repository
- **WHEN** a user inspects `.speckit/commands/`
- **THEN** they find markdown templates for `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`, `/speckit.clarify`, `/speckit.checklist`, and `/speckit.analyze`

#### Scenario: Supporting templates are versioned
- **GIVEN** a contributor runs `/speckit.specify`
- **WHEN** the assistant loads `.speckit/templates/spec-template.md`
- **THEN** the template exists in the repo without requiring an external download

#### Scenario: Helper script guides setup
- **GIVEN** Python ≥ 3.9 is available
- **WHEN** a user runs `python scripts/speckit_check.py`
- **THEN** the script reports SpecKit directory status, tooling prerequisites, and links to documentation

#### Scenario: One-command entrypoint exists
- **GIVEN** a contributor is in the repo root
- **WHEN** they execute `./speckit`
- **THEN** the helper script runs and the terminal prints next steps for the SpecKit flow

### Requirement: Documentation Links SpecKit to OpenSpec
The project MUST explain how to operate SpecKit commands and how outputs align with OpenSpec artifacts.

#### Scenario: README introduces the immersive flow
- **GIVEN** a visitor reads `README.md`
- **WHEN** they reach the SpecKit section
- **THEN** they learn where templates live, how to run the helper script, and where to find the full guide

#### Scenario: Dedicated guide describes full workflow
- **GIVEN** a user opens `docs/spec-kit.md`
- **WHEN** they follow the steps
- **THEN** they can run `/speckit.*` commands (CLI or manual) and map results to `openspec/changes/<id>/`

#### Scenario: AI assistants follow SpecKit instructions
- **GIVEN** an AI agent reads `openspec/AGENTS.md`
- **WHEN** it handles a change request requiring planning/spec work
- **THEN** it references the SpecKit flow to produce aligned artifacts
