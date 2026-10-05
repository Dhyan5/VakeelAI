"""
Nyaya – Chat API with SSE streaming.
"""

import uuid
import json
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ChatSession, ChatMessage
from app.api.keys import get_active_llm_client
from app.rag.generator import stream_answer, generate_answer
from app.rag.retriever import get_chunk_by_id
from app.core.security import rate_limit, chat_limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    language: str = "en"
    stream: bool = True


class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str  # "up" | "down"


# ── Chat ───────────────────────────────────────────────────────────────────

@router.post("/chat", dependencies=[Depends(rate_limit(chat_limiter))])
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint. Returns SSE stream or JSON."""
    # Get LLM client
    llm, provider, model = get_active_llm_client(db)

    # Get or create session
    session_id = req.session_id or str(uuid.uuid4())
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        session = ChatSession(id=session_id, title=req.query[:100])
        db.add(session)
        db.commit()

    # Get recent history (last 6 turns = 12 messages)
    recent_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(12)
        .all()
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in reversed(recent_messages)
    ]

    # Save user message
    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=req.query,
    )
    db.add(user_msg)
    db.commit()

    if req.stream:
        return StreamingResponse(
            _stream_sse(req.query, llm, history, session_id, req.language, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-Id": session_id,
            },
        )
    else:
        # Non-streaming
        result = await generate_answer(req.query, llm, history, req.language)

        # Save assistant message
        assistant_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"],
            confidence=result.get("confidence", 0),
        )
        db.add(assistant_msg)
        session.updated_at = datetime.utcnow()
        db.commit()

        return {
            "session_id": session_id,
            "message_id": assistant_msg.id,
            **result,
        }


async def _stream_sse(query, llm, history, session_id, language, db):
    """Generator for SSE events."""
    full_answer = ""
    citations = []
    assistant_msg_id = str(uuid.uuid4())

    try:
        async for event in stream_answer(query, llm, history, language):
            event_type = event.get("type", "")
            data = event.get("data", "")

            if event_type == "meta":
                citations = data.get("citations", [])
                yield f"event: meta\ndata: {json.dumps({**data, 'session_id': session_id, 'message_id': assistant_msg_id})}\n\n"
            elif event_type == "token":
                full_answer += data
                yield f"event: token\ndata: {json.dumps({'token': data})}\n\n"
            elif event_type == "done":
                yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'message_id': assistant_msg_id})}\n\n"

        # Save assistant message after streaming
        from app.db.session import get_session_factory
        save_session = get_session_factory()()
        try:
            assistant_msg = ChatMessage(
                id=assistant_msg_id,
                session_id=session_id,
                role="assistant",
                content=full_answer,
                citations=citations,
            )
            save_session.add(assistant_msg)
            chat_session = save_session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if chat_session:
                chat_session.updated_at = datetime.utcnow()
            save_session.commit()
        finally:
            save_session.close()

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "auth" in error_msg.lower():
            error_msg = "API key is invalid or expired. Please update it in Settings."
        elif "429" in error_msg or "rate" in error_msg.lower() or "quota" in error_msg.lower():
            error_msg = "Rate limit or quota exceeded. Please try again later or check your API plan."
        else:
            error_msg = f"An error occurred: {error_msg}"

        yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"


# ── Sessions ───────────────────────────────────────────────────────────────

@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    """List chat sessions."""
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).limit(50).all()
    return {
        "sessions": [
            {
                "id": s.id,
                "title": s.title,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in sessions
        ]
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Get messages for a session."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return {
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "citations": m.citations,
                "confidence": m.confidence,
                "feedback": m.feedback,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found.")
    db.delete(session)
    db.commit()
    return {"ok": True}


@router.delete("/sessions")
async def clear_all_sessions(db: Session = Depends(get_db)):
    """Delete all chat sessions."""
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.commit()
    return {"ok": True}


# ── Sources ────────────────────────────────────────────────────────────────

@router.get("/sources/{chunk_id}")
async def get_source(chunk_id: str):
    """Get a source passage by chunk ID."""
    chunk = get_chunk_by_id(chunk_id)
    if not chunk:
        raise HTTPException(404, "Source not found.")
    return chunk


# ── Feedback ───────────────────────────────────────────────────────────────

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit thumbs up/down feedback for a message."""
    msg = db.query(ChatMessage).filter(ChatMessage.id == req.message_id).first()
    if not msg:
        raise HTTPException(404, "Message not found.")
    msg.feedback = req.feedback
    db.commit()
    return {"ok": True}
