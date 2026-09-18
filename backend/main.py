"""
FastAPI application for VakeelAI Legal RAG Platform.
Production endpoints:
- POST /api/case/submit        Submit plain text case description
- POST /api/case/upload        Upload PDF / DOCX / Scanned image
- POST /api/case/analyze       Run full RAG analysis
- GET  /api/case/stream        Stream real-time analysis tokens
- GET  /api/case/history       List case history for current user
- GET  /api/case/{case_id}     Retrieve case details
- DELETE /api/case/{case_id}   Delete case from history
- POST /api/auth/register      Register new account
- POST /api/auth/login         Login and acquire JWT
- GET  /api/health             Health check endpoint
"""

import os
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import dotenv

dotenv.load_dotenv()

from .db import (
    init_db, create_user, authenticate_user,
    save_case_history, get_user_cases, get_case_by_id, delete_user_case
)
from .auth import create_access_token, get_current_user, get_current_user_optional
from .rag_service import get_rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler: initialize DB and verify RAG index on startup."""
    init_db()
    # Initialize RAG service and auto-rebuild index if missing
    try:
        service = get_rag_service()
        print(f"[FastAPI] VakeelAI backend initialized. Indexed chunks: {len(service.retrieval_engine)}")
    except Exception as e:
        print(f"[FastAPI] Warning initializing RAG service: {e}")
    yield


app = FastAPI(
    title="VakeelAI Legal RAG API",
    description="Multilingual Legal Research & Analysis Assistant for Indian Law (Kannada, Hindi, English)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# Allows localhost (dev) and deployed Vercel frontend domains
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
if FRONTEND_ORIGIN and FRONTEND_ORIGIN != "*":
    allowed_origins.append(FRONTEND_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if FRONTEND_ORIGIN == "*" else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request & Response Models
class CaseSubmitRequest(BaseModel):
    query: str
    output_language: Optional[str] = "English"


class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


# Auth Endpoints
@app.post("/api/auth/register")
async def register(req: UserRegisterRequest):
    """Register a new user."""
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    user = create_user(req.username, req.email, req.password)
    if not user:
        raise HTTPException(status_code=409, detail="Username or email already registered.")

    token = create_access_token(user["id"], user["username"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]}
    }


@app.post("/api/auth/login")
async def login(req: UserLoginRequest):
    """Login and receive JWT."""
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_access_token(user["id"], user["username"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


# Case Ingestion & Analysis Endpoints
@app.post("/api/case/submit")
async def submit_case_text(
    req: CaseSubmitRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """Submit a text case and receive structured legal analysis."""
    rag = get_rag_service()
    result = rag.analyze_case(
        user_query=req.query,
        output_language=req.output_language
    )

    # Save to user history
    uid = current_user.get("user_id", 1)
    title = req.query.strip().split("\n")[0][:60]
    saved = save_case_history(
        user_id=uid,
        title=title or "Legal Inquiry",
        source_type="text",
        analysis_text=result.get("analysis", ""),
        query_preview=req.query,
        detected_language=result.get("detected_language", "en"),
        output_language=result.get("output_language", "English"),
        citations=result.get("citations", []),
        confidence=result.get("confidence", "HIGH")
    )
    result["case_id"] = saved["id"]
    return result


@app.post("/api/case/upload")
async def upload_case_file(
    file: UploadFile = File(...),
    output_language: str = Form("English"),
    current_user: dict = Depends(get_current_user_optional)
):
    """Upload a case document (.pdf, .docx, .png, .jpg, .txt) and analyze."""
    # Validate extension
    allowed_exts = {".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: PDF, DOCX, TXT, PNG, JPG."
        )

    # Read into memory (discarded after analysis per DPDP minimization)
    content = await file.read()
    rag = get_rag_service()

    result = rag.analyze_document(
        file_bytes=content,
        filename=file.filename,
        output_language=output_language
    )

    # Save to history
    uid = current_user.get("user_id", 1)
    title = f"Document: {file.filename}"
    saved = save_case_history(
        user_id=uid,
        title=title,
        source_type="file",
        original_filename=file.filename,
        analysis_text=result.get("analysis", ""),
        query_preview=result.get("extracted_text_preview", ""),
        detected_language=result.get("detected_language", "en"),
        output_language=result.get("output_language", "English"),
        citations=result.get("citations", []),
        confidence=result.get("confidence", "HIGH")
    )
    result["case_id"] = saved["id"]
    return result


@app.post("/api/case/analyze")
async def analyze_case_generic(
    req: CaseSubmitRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """Endpoint for direct analysis queries."""
    return await submit_case_text(req, current_user)


@app.get("/api/case/stream")
async def stream_analysis_endpoint(
    query: str = Query(...),
    output_language: str = Query("English")
):
    """Server-Sent Event streaming endpoint for progressive text generation."""
    rag = get_rag_service()

    def event_stream():
        for chunk in rag.stream_analysis(query, output_language=output_language):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Case History Endpoints
@app.get("/api/case/history")
@app.get("/api/case/list")
async def list_cases(current_user: dict = Depends(get_current_user)):
    """Retrieve case history for the authenticated user."""
    uid = current_user.get("user_id", 1)
    return get_user_cases(user_id=uid)


@app.get("/api/case/{case_id}")
async def get_case_detail(case_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieve specific case record by ID."""
    uid = current_user.get("user_id", 1)
    case_record = get_case_by_id(case_id=case_id, user_id=uid)
    if not case_record:
        raise HTTPException(status_code=404, detail="Case record not found.")
    return case_record


@app.delete("/api/case/{case_id}")
async def delete_case(case_id: int, current_user: dict = Depends(get_current_user)):
    """Delete case record permanently from history."""
    uid = current_user.get("user_id", 1)
    success = delete_user_case(case_id=case_id, user_id=uid)
    if not success:
        raise HTTPException(status_code=404, detail="Case record not found or unauthorized.")
    return {"message": "Case data deleted successfully.", "case_id": case_id}


# Health Check
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    rag = get_rag_service()
    return {
        "status": "ok",
        "service": "VakeelAI Legal RAG",
        "indexed_chunks": len(rag.retrieval_engine),
        "groq_configured": bool(rag.generation_service.client),
        "languages_supported": ["en", "hi", "kn"]
    }
