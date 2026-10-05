"""
Nyaya – OpenAI adapter.
"""

import openai
from typing import AsyncIterator
from app.llm.base import LLMClient, LLMMessage, LLMResponse


class OpenAIClient(LLMClient):
    provider = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)

    def _to_messages(self, messages: list[LLMMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=self._to_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=self.model,
            provider=self.provider,
            usage={
                "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
            finish_reason=choice.finish_reason or "",
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=self._to_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def test_connection(self) -> tuple[bool, str]:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'ok'"}],
                max_tokens=5,
            )
            return True, f"Connected to {self.model}"
        except openai.AuthenticationError:
            return False, "Invalid API key."
        except openai.RateLimitError:
            return False, "Rate limit exceeded or no credits."
        except openai.APIConnectionError:
            return False, "Cannot reach OpenAI. Check your network."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
