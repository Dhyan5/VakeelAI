"""
Nyaya – LLM factory: creates the right client from provider + key.
"""

from app.llm.base import LLMClient
from app.llm.openai_client import OpenAIClient
from app.llm.anthropic_client import AnthropicClient
from app.llm.gemini_client import GeminiClient


def create_llm_client(provider: str, api_key: str, model: str | None = None) -> LLMClient:
    """Instantiate the correct LLM adapter."""
    provider = provider.lower().strip()

    defaults = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-sonnet-4-20250514",
        "gemini": "gemini-2.5-flash",
    }

    model = model or defaults.get(provider, "")

    if provider == "openai":
        return OpenAIClient(api_key=api_key, model=model)
    elif provider == "anthropic":
        return AnthropicClient(api_key=api_key, model=model)
    elif provider == "gemini":
        return GeminiClient(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
