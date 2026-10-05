"""
Nyaya – Application configuration.
Loads settings from environment / .env, with sensible defaults for local dev.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ── Server ──────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_url: str = "http://localhost:5173"
    debug: bool = False

    # ── Optional pre-set API keys (.env fallback) ───────────────────────
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # ── Paths ───────────────────────────────────────────────────────────
    data_dir: str = "./data"
    chroma_dir: str = "./data/chroma"
    sqlite_db: str = "./data/nyaya.db"
    knowledge_base_dir: str = "./knowledge_base"
    upload_dir: str = "./data/uploads"
    encryption_key_file: str = "./data/.encryption_key"

    # ── Embedding ───────────────────────────────────────────────────────
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # ── Chunk settings ──────────────────────────────────────────────────
    chunk_min_tokens: int = 200
    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 50

    # ── LLM defaults ───────────────────────────────────────────────────
    default_provider: str = "openai"
    default_model: str = "gpt-4o-mini"

    def ensure_dirs(self):
        """Create required directories on startup."""
        for d in [self.data_dir, self.chroma_dir, self.upload_dir, self.knowledge_base_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)


settings = Settings()
