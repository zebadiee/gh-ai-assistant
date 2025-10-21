"""Client wrapper around the Claude Code CLI."""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import Dict, List, Optional


class ClaudeCLIError(RuntimeError):
    """Raised when the Claude CLI invocation fails."""


class ClaudeCLIClient:
    """Thin wrapper that delegates completions to the Claude Code CLI."""

    def __init__(
        self,
        command: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        raw_command = command or os.getenv("CLAUDE_CLI_COMMAND", "claude")
        self.command = shlex.split(raw_command)
        self.model = model or os.getenv("CLAUDE_CODE_MODEL")
        self.timeout = timeout or int(os.getenv("CLAUDE_CLI_TIMEOUT", "120"))

    def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """Send messages to the Claude CLI and capture the response."""

        prompt_payload = self._serialize_messages(messages)
        cmd = list(self.command)
        if self.model:
            cmd += ["--model", self.model]

        try:
            proc = subprocess.run(  # nosec B603
                cmd,
                input=prompt_payload,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except FileNotFoundError as exc:
            raise ClaudeCLIError(
                f"Claude CLI command not found: {self.command[0]}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ClaudeCLIError(
                f"Claude CLI timed out after {self.timeout} seconds"
            ) from exc

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            raise ClaudeCLIError(
                stderr or f"Claude CLI exited with status {proc.returncode}"
            )

        output = (proc.stdout or "").strip()
        if not output:
            raise ClaudeCLIError("Claude CLI returned empty output")

        return {"content": output}

    def _serialize_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages into a text block for CLI stdin."""

        chunks: List[str] = []
        for message in messages:
            role = message.get("role", "user").upper()
            content = message.get("content", "")
            chunks.append(f"{role}:\n{content.strip()}".strip())
        return "\n\n".join(chunks).strip() + "\n"
