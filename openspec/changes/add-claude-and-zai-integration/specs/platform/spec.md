## ADDED Requirements

### Requirement: Provider Selection Supports Claude CLI and Z.ai GLM
The assistant MUST allow switching between OpenRouter, Claude Code CLI, and Z.ai GLM providers via configuration without modifying source code.

#### Scenario: Claude CLI provider delivers responses
- **GIVEN** `GH_AI_PROVIDER=claude-cli` is set and the Claude CLI binary is available
- **WHEN** the user runs `python gh_ai_core.py ask "Explain decorators"`
- **THEN** the assistant invokes the Claude CLI command with the composed prompt
- **AND** prints the Claude response to stdout
- **AND** surfaces errors when the CLI is missing or exits non-zero

#### Scenario: Z.ai GLM provider uses API key from env
- **GIVEN** `GH_AI_PROVIDER=zai-glm` and `ZAI_API_KEY` are set (directly or via `.env`)
- **WHEN** the user runs `python gh_ai_core.py ask "Summarize this diff"`
- **THEN** the assistant sends an HTTP request to the configured Z.ai GLM endpoint
- **AND** returns the model response to the user
- **AND** handles HTTP errors with a descriptive message

#### Scenario: Default OpenRouter behavior remains unchanged
- **GIVEN** no provider override is specified
- **WHEN** the assistant handles a request
- **THEN** it continues using OpenRouter token management and rotation without regression
