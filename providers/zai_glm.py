"""Client for the Z.ai GLM coding API."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests


class ZaiGLMError(RuntimeError):
    """Raised when the Z.ai GLM API returns an error."""


class ZaiGLMClient:
    """Simple REST client for the Z.ai GLM chat completion endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ZAI_API_KEY")
        self.api_base = (api_base or os.getenv("ZAI_API_BASE") or "https://api.z.ai/v1").rstrip("/")
        self.model = model or os.getenv("ZAI_MODEL", "glm-4-air")
        self.timeout = timeout or int(os.getenv("ZAI_TIMEOUT", "60"))
        self.temperature = float(os.getenv("ZAI_TEMPERATURE", "0.7"))

    def chat_completion(self, messages: List[Dict[str, str]]) -> Dict:
        """Call the Z.ai GLM chat completions endpoint."""

        if not self.api_key:
            raise ZaiGLMError("ZAI_API_KEY is not set. Provide it via env or .env file.")

        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ZaiGLMError(f"Z.ai GLM request failed: {exc}") from exc

        if resp.status_code >= 400:
            raise ZaiGLMError(self._format_error(resp))

        try:
            return resp.json()
        except ValueError as exc:
            raise ZaiGLMError("Invalid JSON response from Z.ai GLM") from exc

    def _format_error(self, resp: requests.Response) -> str:
        try:
            data = resp.json()
        except ValueError:
            data = {}
        message = (
            data.get("error", {}).get("message")
            or data.get("message")
            or resp.text
        )
        return f"Z.ai GLM error {resp.status_code}: {message}"
