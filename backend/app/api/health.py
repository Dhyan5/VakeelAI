"""
Nyaya – Health check endpoint.
"""

from fastapi import APIRouter
import chromadb
from app.core.config import settings
from pathlib import Path

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health():
    """Basic health check."""
    chroma_ok = Path(settings.chroma_dir).exists()
    db_ok = Path(settings.sqlite_db).exists()
    return {
        "status": "ok",
        "chroma": "ready" if chroma_ok else "not initialized",
        "database": "ready" if db_ok else "not initialized",
    }
