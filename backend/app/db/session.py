"""
Nyaya – Database session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base
from pathlib import Path

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        db_path = Path(settings.sqlite_db)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=settings.debug,
        )
        Base.metadata.create_all(bind=_engine)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def SessionLocal():
    """Convenience factory returning a new database session."""
    return get_session_factory()()
