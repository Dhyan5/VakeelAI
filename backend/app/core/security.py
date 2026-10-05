"""
Nyaya – Security utilities: rate limiting, CORS helpers, input validation.
"""

import time
import asyncio
from collections import defaultdict
from functools import wraps
from fastapi import HTTPException, Request


class RateLimiter:
    """Simple in-memory sliding-window rate limiter."""

    def __init__(self, max_calls: int = 10, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = window_seconds
        self._calls: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        self._calls[key] = [t for t in self._calls[key] if t > window_start]
        if len(self._calls[key]) >= self.max_calls:
            return False
        self._calls[key].append(now)
        return True


# Shared limiters
key_limiter = RateLimiter(max_calls=10, window_seconds=60)
chat_limiter = RateLimiter(max_calls=30, window_seconds=60)


def rate_limit(limiter: RateLimiter):
    """Dependency that rate-limits by client IP."""
    def dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        if not limiter.check(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
    return dependency


def validate_api_key_format(key: str, provider: str) -> str | None:
    """Basic format validation. Returns error message or None."""
    if not key or len(key.strip()) < 10:
        return "API key is too short."
    key = key.strip()
    if provider == "openai" and not key.startswith("sk-"):
        return "OpenAI keys usually start with 'sk-'."
    if provider == "anthropic" and not key.startswith("sk-ant-"):
        return "Anthropic keys usually start with 'sk-ant-'."
    return None


PROVIDER_MODELS = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20241022",
    ],
    "gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-flash-latest",
        "gemini-2.0-flash",
    ],
}
