"""
Nyaya – API Key management endpoints.
Handles save, delete, test, and status. Never returns the actual key.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ApiKeyConfig
from app.core.crypto import encrypt_value, decrypt_value, mask_key
from app.core.security import (
    rate_limit, key_limiter, validate_api_key_format, PROVIDER_MODELS
)
from app.llm.factory import create_llm_client
from app.core.config import settings

router = APIRouter(prefix="/api/keys", tags=["keys"])


class KeyTestRequest(BaseModel):
    provider: str
    model: str
    api_key: str


class KeySaveRequest(BaseModel):
    provider: str
    model: str
    api_key: str


class KeyStatusResponse(BaseModel):
    configured: bool
    provider: str | None = None
    model: str | None = None
    last4: str | None = None


class ModelsResponse(BaseModel):
    providers: dict[str, list[str]]


@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """Return available providers and their models."""
    return ModelsResponse(providers=PROVIDER_MODELS)


@router.post("/test", dependencies=[Depends(rate_limit(key_limiter))])
async def test_key(req: KeyTestRequest):
    """Test an API key by making a tiny real API call."""
    # Basic validation
    err = validate_api_key_format(req.api_key, req.provider)
    if err:
        return {"ok": False, "message": err}

    try:
        client = create_llm_client(req.provider, req.api_key, req.model)
        ok, message = await client.test_connection()
        return {"ok": ok, "message": message}
    except ValueError as e:
        return {"ok": False, "message": str(e)}
    except Exception as e:
        return {"ok": False, "message": f"Unexpected error: {str(e)}"}


@router.post("", dependencies=[Depends(rate_limit(key_limiter))])
async def save_key(req: KeySaveRequest, db: Session = Depends(get_db)):
    """Save (or replace) an encrypted API key."""
    if req.provider not in PROVIDER_MODELS:
        raise HTTPException(400, f"Unknown provider: {req.provider}")

    encrypted = encrypt_value(req.api_key)
    last4 = mask_key(req.api_key)

    # Upsert: delete old, insert new
    db.query(ApiKeyConfig).delete()
    entry = ApiKeyConfig(
        id=1,
        provider=req.provider,
        model=req.model,
        encrypted_key=encrypted,
        last4=last4,
    )
    db.add(entry)
    db.commit()

    return {"ok": True, "last4": last4, "provider": req.provider, "model": req.model}


@router.delete("", dependencies=[Depends(rate_limit(key_limiter))])
async def delete_key(db: Session = Depends(get_db)):
    """Remove the stored API key."""
    db.query(ApiKeyConfig).delete()
    db.commit()
    return {"ok": True, "message": "API key deleted."}


@router.get("/status", response_model=KeyStatusResponse)
async def key_status(db: Session = Depends(get_db)):
    """Return connection status. Never returns the actual key."""
    entry = db.query(ApiKeyConfig).first()

    # Check env fallback
    if not entry:
        for provider, env_var in [
            ("anthropic", settings.anthropic_api_key),
            ("openai", settings.openai_api_key),
            ("gemini", settings.gemini_api_key),
        ]:
            if env_var:
                return KeyStatusResponse(
                    configured=True,
                    provider=provider,
                    model=PROVIDER_MODELS[provider][0],
                    last4=mask_key(env_var),
                )
        return KeyStatusResponse(configured=False)

    return KeyStatusResponse(
        configured=True,
        provider=entry.provider,
        model=entry.model,
        last4=entry.last4,
    )


def get_active_llm_client(db: Session) -> tuple:
    """
    Helper: resolve the active API key (DB first, then .env) and return
    (LLMClient, provider, model). Raises HTTPException if no key configured.
    """
    entry = db.query(ApiKeyConfig).first()

    if entry:
        api_key = decrypt_value(entry.encrypted_key)
        return create_llm_client(entry.provider, api_key, entry.model), entry.provider, entry.model

    # Fallback to .env
    for provider, env_key in [
        ("openai", settings.openai_api_key),
        ("anthropic", settings.anthropic_api_key),
        ("gemini", settings.gemini_api_key),
    ]:
        if env_key:
            model = PROVIDER_MODELS[provider][0]
            return create_llm_client(provider, env_key, model), provider, model

    raise HTTPException(
        status_code=400,
        detail="No API key configured. Please add one in Settings."
    )
