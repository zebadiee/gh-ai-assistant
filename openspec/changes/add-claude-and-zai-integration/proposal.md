# Change Proposal: Add Claude CLI and Z.ai GLM Integrations

## Overview
- Support developers who prefer Anthropic's Claude Code CLI alongside existing OpenRouter flows.
- Allow configuration of Z.ai GLM coding APIs through environment variables or a local `.env` file for lightweight bring-your-own-key usage.

## Problem
- The assistant currently hardcodes OpenRouter as the only cloud provider.
- Developers using Claude CLI or Z.ai GLM must patch the project manually, which is error-prone and duplicates effort.
- There is no standard mechanism for loading provider credentials from environment or `.env` files.

## Proposal
- Introduce a provider abstraction in `gh_ai_core` that selects between OpenRouter, Claude CLI, and Z.ai GLM based on environment configuration.
- Add lightweight clients for Claude CLI and Z.ai GLM with error handling and context integration hooks.
- Implement `.env` loading (fallback to environment variables) for API credentials.
- Update CLI to expose provider choice and document necessary setup steps.

## Success Criteria
- Users can run `GH_AI_PROVIDER=claude-cli python gh_ai_core.py ask ...` and receive responses via the Claude CLI without modifying source code.
- Users can configure `GH_AI_PROVIDER=zai-glm` with `ZAI_API_KEY` (via env or `.env`) and run requests through the Z.ai GLM REST API.
- Default behavior for OpenRouter is unchanged, including token management and rotation.
- Tests and documentation are refreshed to cover the new provider options.

## Risks & Mitigations
- **Risk:** Subprocess integration with Claude CLI could hang or produce large outputs.  
  **Mitigation:** Use timeouts and capture stderr; surface clear error messages.
- **Risk:** Z.ai GLM API contract might differ between accounts.  
  **Mitigation:** Make endpoints configurable (`ZAI_API_BASE`) and log helpful error details.
- **Risk:** `.env` parsing may conflict with existing tooling.  
  **Mitigation:** Implement minimal, non-intrusive loader that skips malformed lines.

## Validation Plan
- Unit tests mocking subprocess (`claude`) and HTTP (`requests`) to cover happy-path and error handling.
- Manual smoke tests switching `GH_AI_PROVIDER` between `openrouter`, `claude-cli`, and `zai-glm` to ensure commands honor provider selection.
- Verify documentation updates by following setup steps from a clean clone.
