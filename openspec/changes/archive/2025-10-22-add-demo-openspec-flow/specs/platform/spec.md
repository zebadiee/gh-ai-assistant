## ADDED Requirements

### Requirement: Demo Validation Flow
The system SHALL include a demo change that can be strictly validated to showcase the OpenSpec workflow.

#### Scenario: Validation passes
- GIVEN the demo change `add-demo-openspec-flow` exists
- WHEN the user runs `openspec validate add-demo-openspec-flow --strict`
- THEN validation succeeds with no errors

#### Scenario: Listed among changes
- GIVEN the repository is at the project root
- WHEN the user runs `openspec list`
- THEN `add-demo-openspec-flow` appears in the list of changes

### Requirement: Demo Documentation Presence
The system SHALL document the demo via a minimal design file explaining intent and scope.

#### Scenario: Design file exists
- GIVEN the repository contains the demo change folder
- WHEN the user inspects `openspec/changes/add-demo-openspec-flow/design.md`
- THEN the file exists and describes goals, decisions, and archiving plan
