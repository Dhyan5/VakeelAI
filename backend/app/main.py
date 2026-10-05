"""
Nyaya – FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import get_engine, SessionLocal
from app.db.models import Base
from app.api import keys, documents, chat, health
from app.rag.ingest import load_bm25_corpus, auto_ingest_knowledge_base

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Nyaya backend...")
    settings.ensure_dirs()
    get_engine()  # Initialize DB tables
    load_bm25_corpus()  # Load BM25 index from disk
    
    # Auto-ingest any pre-loaded knowledge base files
    try:
        db = SessionLocal()
        auto_ingest_knowledge_base(db)
        db.close()
    except Exception as e:
        logger.warning(f"Error during auto-ingest of knowledge base: {e}")

    logger.info("Nyaya backend ready.")
    yield
    # Shutdown
    logger.info("Shutting down Nyaya backend.")


app = FastAPI(
    title="Nyaya – Indian Legal AI Assistant",
    description="RAG-based legal research assistant for Indian law",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.frontend_url,
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(keys.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "name": "Nyaya",
        "description": "Indian Legal AI Assistant",
        "version": "1.0.0",
        "docs": "/docs",
    }
