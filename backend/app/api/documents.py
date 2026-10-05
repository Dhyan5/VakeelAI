"""
Nyaya – Document upload and management endpoints.
"""

import uuid
import asyncio
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Document
from app.rag.ingest import ingest_document, delete_document, get_progress, get_document_count, get_total_chunks

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".html", ".htm"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form("other"),
    act_name: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload and ingest a legal document."""
    # Validate extension
    import pathlib
    ext = pathlib.Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Read file
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    if len(file_bytes) == 0:
        raise HTTPException(400, "Empty file.")

    job_id = str(uuid.uuid4())

    # Run ingestion in background
    def _ingest():
        from app.db.session import get_session_factory
        session = get_session_factory()()
        try:
            ingest_document(
                file_path=file.filename or "upload",
                file_bytes=file_bytes,
                original_filename=file.filename or "upload",
                category=category,
                act_name=act_name,
                year=year,
                db=session,
                job_id=job_id,
            )
        finally:
            session.close()

    background_tasks.add_task(_ingest)

    return {"ok": True, "job_id": job_id, "message": "Ingestion started."}


@router.get("")
async def list_documents(db: Session = Depends(get_db)):
    """List all ingested documents."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return {
        "documents": [
            {
                "id": d.id,
                "filename": d.original_filename,
                "category": d.category,
                "act_name": d.act_name,
                "year": d.year,
                "chunk_count": d.chunk_count,
                "status": d.status,
                "error_message": d.error_message,
                "file_size": d.file_size,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ],
        "total_documents": len(docs),
        "total_chunks": get_total_chunks(),
    }


@router.delete("/{doc_id}")
async def remove_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete a document and its chunks."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found.")
    delete_document(doc_id, db)
    return {"ok": True, "message": "Document deleted."}


@router.get("/progress/{job_id}")
async def ingest_progress(job_id: str):
    """Get ingestion progress for a job."""
    return get_progress(job_id)


@router.get("/stats")
async def document_stats(db: Session = Depends(get_db)):
    """Get document statistics."""
    return {
        "total_documents": get_document_count(db),
        "total_chunks": get_total_chunks(),
    }
