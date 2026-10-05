"""
Nyaya – SQLite database models using SQLAlchemy.
Stores: chat sessions, messages, document registry, API key settings.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean, 
    ForeignKey, create_engine, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ApiKeyConfig(Base):
    """Stored (encrypted) API key and provider settings."""
    __tablename__ = "api_key_config"

    id = Column(Integer, primary_key=True, default=1)
    provider = Column(String(50), nullable=False)  # openai | anthropic | gemini
    model = Column(String(100), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    last4 = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Document(Base):
    """Registry of ingested documents."""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True)  # UUID
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    category = Column(String(50), nullable=False)  # statute | supreme_court | high_court | rules | notification | law_commission | other
    act_name = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=False)  # SHA-256 for dedup
    file_size = Column(Integer, nullable=False)
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending | processing | ready | error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSession(Base):
    """A conversation session."""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True)  # UUID
    title = Column(String(500), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """A single chat message (user or assistant)."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)  # UUID
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # list of citation objects
    confidence = Column(Float, nullable=True)
    feedback = Column(String(10), nullable=True)  # up | down | null
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
