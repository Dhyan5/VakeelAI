"""
Nyaya – Provider-agnostic LLM base interface.
All provider adapters implement this interface so the rest
of the codebase never touches provider SDKs directly.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: dict = field(default_factory=dict)  # {prompt_tokens, completion_tokens}
    finish_reason: str = ""


class LLMClient(ABC):
    """Abstract base class for LLM providers."""

    provider: str = ""

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Single-shot generation."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream tokens one by one."""
        ...

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str]:
        """Quick health check. Returns (ok, message)."""
        ...
