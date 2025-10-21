"""Token recycler service that unifies caching, API invocation, and metrics."""

from __future__ import annotations

import time
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from token_optimizer import (  # Reuse existing cache/metrics building blocks
    CachedResponse,
    ParallelTokenizer,
    TokenCache,
    TokenMetrics,
    TokenMetricsTracker,
)
from token_recycler.config import DEFAULT_MAX_CACHE_AGE_HOURS

if TYPE_CHECKING:  # Avoid runtime import cycle
    from gh_ai_core import TokenManager


@dataclass
class TokenRecyclerResult:
    """Outcome of a recycler request."""

    content: Optional[str]
    cache_hit: bool
    metrics: Optional[TokenMetrics] = None
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0

    def is_error(self) -> bool:
        return self.error is not None

    def tokens_used(self) -> int:
        if not self.metrics:
            return 0
        if self.cache_hit:
            return 0
        return int(self.metrics.total_tokens)


class TokenRecyclerService:
    """Coordinate cache lookups, API dispatch, and metrics persistence."""

    def __init__(
        self,
        api_call: Callable[..., Dict[str, Any]],
        token_manager: Optional["TokenManager"] = None,
        *,
        cache: Optional[TokenCache] = None,
        metrics_tracker: Optional[TokenMetricsTracker] = None,
        tokenizer: Optional[ParallelTokenizer] = None,
        default_max_tokens: int = 2048,
    ) -> None:
        self.api_call = api_call
        self.token_manager = token_manager
        self.cache = cache or TokenCache()
        self.metrics = metrics_tracker or TokenMetricsTracker()
        self.tokenizer = tokenizer or ParallelTokenizer()
        self.default_max_tokens = default_max_tokens

    def process(
        self,
        *,
        prompt: str,
        model: str,
        messages: List[Dict[str, Any]],
        use_cache: bool = True,
        max_tokens: Optional[int] = None,
        api_kwargs: Optional[Dict[str, Any]] = None,
    ) -> TokenRecyclerResult:
        """Handle a prompt lifecycle with cache-first semantics."""

        started = time.perf_counter()
        prompt_tokens = self.tokenizer.count_tokens(prompt, model)
        cache_entry: Optional[CachedResponse] = None

        if use_cache:
            cache_entry = self.cache.get(prompt, model)

        if cache_entry:
            latency_ms = (time.perf_counter() - started) * 1000
            metrics = TokenMetrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=cache_entry.tokens,
                total_tokens=prompt_tokens + cache_entry.tokens,
                cost=0.0,
                latency_ms=latency_ms,
                cache_hit=True,
                model=model,
                timestamp=datetime.now(),
            )
            self.metrics.record(metrics)
            return TokenRecyclerResult(
                content=cache_entry.response,
                cache_hit=True,
                metrics=metrics,
                raw_response=None,
                latency_ms=latency_ms,
            )

        latency_start = time.perf_counter()
        kwargs = dict(api_kwargs or {})
        if max_tokens is not None:
            kwargs.setdefault("max_tokens", max_tokens)
        elif self.default_max_tokens is not None:
            kwargs.setdefault("max_tokens", self.default_max_tokens)

        response = self.api_call(model, messages, **kwargs)
        latency_ms = (time.perf_counter() - latency_start) * 1000

        if isinstance(response, dict) and response.get("error"):
            return TokenRecyclerResult(
                content=None,
                cache_hit=False,
                metrics=None,
                raw_response=response,
                error=response,
                latency_ms=latency_ms,
            )

        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            return TokenRecyclerResult(
                content=None,
                cache_hit=False,
                metrics=None,
                raw_response=response,
                error={"type": "parse_error", "detail": str(exc), "response": response},
                latency_ms=latency_ms,
            )

        usage = response.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
        completion_tokens = usage.get("completion_tokens")
        if completion_tokens is None:
            completion_tokens = self.tokenizer.count_tokens(content, model)
        total_tokens = usage.get("total_tokens")
        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens

        prompt_tokens = int(prompt_tokens)
        completion_tokens = int(completion_tokens)
        total_tokens = int(total_tokens)
        cost = float(usage.get("cost", 0.0) or 0.0)

        metrics = TokenMetrics(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            latency_ms=latency_ms,
            cache_hit=False,
            model=model,
            timestamp=datetime.now(),
        )

        self.metrics.record(metrics)
        if use_cache:
            self.cache.set(prompt, model, content, completion_tokens)
        if self.token_manager and total_tokens is not None:
            self.token_manager.record_usage(model, total_tokens, cost)

        return TokenRecyclerResult(
            content=content,
            cache_hit=False,
            metrics=metrics,
            raw_response=response,
            latency_ms=latency_ms,
        )

    def cleanup(self, max_age_hours: Optional[int] = None) -> Dict[str, Any]:
        """Clean expired cache rows, vacuum databases, and return summary."""

        removed = self.cache.clear_old(max_age_hours or DEFAULT_MAX_CACHE_AGE_HOURS)
        self._vacuum_db(self.cache.db_path)
        self._vacuum_db(self.metrics.db_path)
        return {
            "removed_entries": removed,
            "cache_db": str(self.cache.db_path),
            "metrics_db": str(self.metrics.db_path),
        }

    @staticmethod
    def _vacuum_db(db_path: Path) -> None:
        """Run SQLite VACUUM on the given database path if it exists."""
        if not db_path.exists():
            return
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("VACUUM")
        finally:
            conn.close()
