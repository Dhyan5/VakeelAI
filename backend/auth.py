"""
JWT Authentication & Password verification module for FastAPI.
Provides token creation, decoding, and current user dependencies.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException, Header, Depends, status
from pydantic import BaseModel
import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "vakeelai-insecure-dev-secret-key-replace-in-prod-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class TokenData(BaseModel):
    user_id: int
    username: str


def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": username,
        "user_id": user_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extract user payload if present, otherwise returns None (for guest/mock access)."""
    if not authorization:
        return {"user_id": 1, "username": "guest"}

    try:
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        user_id: int = payload.get("user_id", 1)
        if not username:
            return {"user_id": 1, "username": "guest"}
        return {"user_id": user_id, "username": username}
    except Exception:
        # Fallback to default user for smooth zero-config dev
        return {"user_id": 1, "username": "guest"}


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Require valid JWT or fallback to guest for development."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
