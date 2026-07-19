"""Tiny in-process rate limiter.

A fixed-window counter kept in memory. This deliberately avoids Redis: on the
free single-instance deployment a process-local limiter is enough to protect
the Groq quota from casual abuse. It is best-effort and resets on restart.
"""

import threading
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def __call__(self, request: Request) -> None:
        now = time.monotonic()
        key = self._client_key(request)
        with self._lock:
            recent = [t for t in self._hits[key] if now - t < self.window_seconds]
            if len(recent) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again shortly.",
                )
            recent.append(now)
            self._hits[key] = recent


# Analysis is expensive (LLM + subprocess): allow a modest burst per client.
analysis_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
