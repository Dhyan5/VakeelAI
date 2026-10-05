"""
Nyaya – Anthropic (Claude) adapter.
"""

import anthropic
from typing import AsyncIterator
from app.llm.base import LLMClient, LLMMessage, LLMResponse


class AnthropicClient(LLMClient):
    provider = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    def _split_messages(self, messages: list[LLMMessage]) -> tuple[str, list[dict]]:
        """Anthropic uses a separate system param instead of a system message."""
        system = ""
        chat = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat.append({"role": m.role, "content": m.content})
        return system, chat

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        system, chat = self._split_messages(messages)
        kwargs = dict(
            model=self.model,
            messages=chat,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if system:
            kwargs["system"] = system
        resp = await self.client.messages.create(**kwargs)
        content = "".join(b.text for b in resp.content if b.type == "text")
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider,
            usage={
                "prompt_tokens": resp.usage.input_tokens,
                "completion_tokens": resp.usage.output_tokens,
            },
            finish_reason=resp.stop_reason or "",
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        system, chat = self._split_messages(messages)
        kwargs = dict(
            model=self.model,
            messages=chat,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if system:
            kwargs["system"] = system

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def test_connection(self) -> tuple[bool, str]:
        try:
            resp = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'ok'"}],
                max_tokens=5,
            )
            return True, f"Connected to {self.model}"
        except anthropic.AuthenticationError:
            return False, "Invalid API key."
        except anthropic.RateLimitError:
            return False, "Rate limit exceeded or no credits."
        except anthropic.APIConnectionError:
            return False, "Cannot reach Anthropic. Check your network."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
