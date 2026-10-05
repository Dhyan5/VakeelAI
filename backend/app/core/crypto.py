"""
Nyaya – Encryption utilities for API key storage.
Uses Fernet symmetric encryption with a machine-generated key
stored outside the repo in a local file.
"""

import os
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from app.core.config import settings

_fernet_instance: Fernet | None = None


def _get_or_create_encryption_key() -> bytes:
    """Load or generate the Fernet key from a local file."""
    key_path = Path(settings.encryption_key_file)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    if key_path.exists():
        return key_path.read_bytes().strip()

    key = Fernet.generate_key()
    key_path.write_bytes(key)
    # Restrict permissions (best-effort on Windows)
    try:
        os.chmod(key_path, 0o600)
    except OSError:
        pass
    return key


def get_fernet() -> Fernet:
    """Return a cached Fernet instance."""
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(_get_or_create_encryption_key())
    return _fernet_instance


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string and return the ciphertext as a URL-safe base64 string."""
    return get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a URL-safe base64 ciphertext string back to plaintext."""
    return get_fernet().decrypt(ciphertext.encode()).decode()


def mask_key(key: str) -> str:
    """Return a masked version showing only the last 4 characters."""
    if len(key) <= 4:
        return "****"
    return f"{'*' * 4}...{key[-4:]}"
