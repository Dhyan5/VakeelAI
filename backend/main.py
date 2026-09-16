"""
FastAPI backend for the Legal RAG platform.

Endpoints:
- POST /api/auth/register - Register a new user
- POST /api/auth/login - Login and get JWT token
- POST /api/case/analyze - Analyze a legal case
- GET /api/case/list - List user's cases
- GET /api/case/{id} - Get a specific case
- DELETE /api/case/{id} - Delete a case

Uses SQLite for user/case storage and NumPy for RAG index.
"""

import os
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt

import dotenv

dotenv.load_dotenv()

from db import (
    init_db, create_user, authenticate_user, create_case,
    get_user_cases, get_case, delete_case, update_case_analysis
)
from rag_service import get_rag_service
from generation import get_generation_service


# Initialize DB
init_db()

# FastAPI app
app = FastAPI(title="LegalRAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class CaseAnalyze(BaseModel):
    query: str
    output_language: str = "English"
    file_content: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET", "default-secret-change-in-production")
ALGORITHM = "HS256"


def create_jwt_token(username: str) -> str:
    """Create a JWT token for a user."""
    return jwt.encode({"sub": username}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(authorization: str = Header(None)) -> str:
    """Verify JWT token and return username."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub", "")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Auth endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Register a new user."""
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password required")

    result = create_user(user.username, user.email, user.password)
    if not result:
        raise HTTPException(status_code=409, detail="User already exists")

    return result


@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login and return JWT token."""
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password required")

    user_info = authenticate_user(user.username, user.password)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(user_info["username"])
    return {"access_token": token, "token_type": "bearer"}


# Case endpoints
@app.get("/api/case/list")
async def list_cases(current_user: str = Depends(verify_token)):
    """List user's cases."""
    # In a real app, we'd look up user_id from JWT
    # For now, we use a simple mapping
    return get_user_cases(user_id=1)  # Default to user_id=1


@app.post("/api/case/analyze")
async def analyze_case(
    case: CaseAnalyze,
    current_user: str = Depends(verify_token)
):
    """Analyze a legal case."""
    # Get RAG service
    rag_service = get_rag_service()
    if not rag_service:
        raise HTTPException(
            status_code=503,
            detail="RAG service not initialized. Check GROQ_API_KEY."
        )

    # Get or create case
    title = case.query[:50] + "..." if len(case.query) > 50 else case.query

    # Create case record
    case_data = create_case(
        user_id=1,  # Default user
        title=title,
        content_type="text",
        content=case.query if not case.file_content else case.file_content,
        language=case.output_language
    )

    # Run analysis
    result = rag_service.analyze_case(
        user_query=case.query,
        output_language=case.output_language
    )

    # Update case with analysis
    update_case_analysis(case_data["id"], result["analysis"])

    # Remove raw_response from output
    output = {k: v for k, v in result.items() if k != "raw_response"}
    output["case_id"] = case_data["id"]

    return output


@app.get("/api/case/{case_id}")
async def get_case_detail(
    case_id: int,
    current_user: str = Depends(verify_token)
):
    """Get a specific case."""
    result = get_case(user_id=1, case_id=case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Case not found")
    return result


@app.delete("/api/case/{case_id}")
async def delete_case_endpoint(
    case_id: int,
    current_user: str = Depends(verify_token)
):
    """Delete a case."""
    if not delete_case(user_id=1, case_id=case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"message": "Case deleted"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "LegalRAG"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
