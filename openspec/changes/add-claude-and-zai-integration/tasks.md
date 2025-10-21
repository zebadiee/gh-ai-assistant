# Task Checklist

## Discovery
- [x] Audit existing provider selection and CLI flags in `gh_ai_core.py`.
- [x] Document Claude Code CLI invocation requirements (command name, model flag, stdin expectations).
- [x] Document Z.ai GLM REST endpoints and expected headers/body.

## Implementation
- [x] Add environment/.env loader utilities for provider configuration.
- [x] Implement provider abstraction and instantiate Claude CLI and Z.ai GLM clients.
- [x] Wire provider selection into `gh_ai_core.AIAssistant` with CLI flag/env overrides.
- [x] Extend cleanup/reporting flows to handle non-OpenRouter providers gracefully.

## Testing & Documentation
- [x] Add unit tests covering Claude CLI subprocess and Z.ai GLM HTTP interactions (mocked).
- [x] Update README / docs with setup instructions for new providers.
- [x] Run `python -m unittest discover` and record results (note missing optional deps if applicable).
