"""
Nyaya – Google Gemini adapter.
"""

import google.generativeai as genai
from typing import AsyncIterator
from app.llm.base import LLMClient, LLMMessage, LLMResponse


class GeminiClient(LLMClient):
    provider = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.model_name = model
        genai.configure(api_key=api_key)
        self.api_key = api_key

    def _build_contents(self, messages: list[LLMMessage]) -> tuple[str | None, list[dict]]:
        system_text = None
        contents = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m.content}]})
        return system_text, contents

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        system_text, contents = self._build_contents(messages)
        model_kwargs = {}
        if system_text:
            model_kwargs["system_instruction"] = system_text
        model = genai.GenerativeModel(self.model_name, **model_kwargs)
        config = genai.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
        resp = await model.generate_content_async(contents, generation_config=config)
        content = ""
        try:
            content = resp.text or ""
        except (ValueError, AttributeError):
            if resp.candidates:
                cand = resp.candidates[0]
                parts = getattr(cand.content, "parts", [])
                content = "".join(getattr(p, "text", "") for p in parts if hasattr(p, "text"))
        return LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider,
            usage={},
            finish_reason="stop",
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        system_text, contents = self._build_contents(messages)
        model_kwargs = {}
        if system_text:
            model_kwargs["system_instruction"] = system_text
        model = genai.GenerativeModel(self.model_name, **model_kwargs)
        config = genai.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
        resp = await model.generate_content_async(
            contents, generation_config=config, stream=True
        )
        async for chunk in resp:
            try:
                if chunk.text:
                    yield chunk.text
            except (ValueError, AttributeError):
                if chunk.candidates:
                    cand = chunk.candidates[0]
                    parts = getattr(cand.content, "parts", [])
                    txt = "".join(getattr(p, "text", "") for p in parts if hasattr(p, "text"))
                    if txt:
                        yield txt

    async def test_connection(self) -> tuple[bool, str]:
        try:
            model = genai.GenerativeModel(self.model_name)
            config = genai.GenerationConfig(max_output_tokens=5)
            resp = await model.generate_content_async(
                [{"role": "user", "parts": [{"text": "Say ok"}]}],
                generation_config=config,
            )
            return True, f"Connected to {self.model_name}"
        except Exception as e:
            err = str(e).lower()
            if "api key" in err or "401" in err or "invalid" in err:
                return False, "Invalid API key."
            if "429" in err or "quota" in err or "rate" in err:
                return False, "Rate limit or quota exceeded."
            return False, f"Connection failed: {str(e)}"
