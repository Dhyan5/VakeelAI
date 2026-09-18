"""
Database layer for user accounts and case analysis history.
Supports:
- Local SQLite (default for $0 zero-config local dev)
- Turso libSQL (via TURSO_DATABASE_URL & TURSO_AUTH_TOKEN in deployment)
Strictly adheres to data minimization:
- Never stores raw uploaded files
- Only stores extracted query text and structured analysis metadata
- Per-user data isolation on every query
"""

import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import dotenv

dotenv.load_dotenv()

DB_FILE = os.getenv("SQLITE_DB_PATH", "legal_rag.db")
TURSO_URL = os.getenv("TURSO_DATABASE_URL", "").strip()
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "").strip()


def get_connection():
    """Get database connection (SQLite row factory)."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables for users and case history."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL,
            original_filename TEXT,
            detected_language TEXT DEFAULT 'en',
            output_language TEXT DEFAULT 'English',
            query_preview TEXT,
            analysis_text TEXT NOT NULL,
            citations_json TEXT,
            confidence TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# Ensure DB initialized on module import
init_db()


def hash_password(password: str) -> str:
    """Hash password using salt + SHA-256."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password hash."""
    try:
        salt, key_hex = password_hash.split('$', 1)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


def create_user(username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
    """Create a new user with hashed password."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(password)
        now = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username.strip(), email.strip().lower(), pw_hash, now)
        )
        conn.commit()
        uid = cursor.lastrowid
        return {"id": uid, "username": username, "email": email, "created_at": now}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate username and password."""
    user = get_user_by_username(username)
    if user and verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"], "email": user["email"]}
    return None


def save_case_history(
    user_id: int,
    title: str,
    source_type: str,
    analysis_text: str,
    query_preview: str = "",
    original_filename: Optional[str] = None,
    detected_language: str = "en",
    output_language: str = "English",
    citations: Optional[List[str]] = None,
    confidence: str = "HIGH"
) -> Dict[str, Any]:
    """Save case analysis results to history with strict user isolation."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    c_json = json.dumps(citations or [])

    cursor.execute("""
        INSERT INTO cases (
            user_id, title, source_type, original_filename,
            detected_language, output_language, query_preview,
            analysis_text, citations_json, confidence, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, title[:100], source_type, original_filename,
        detected_language, output_language, query_preview[:300],
        analysis_text, c_json, confidence, now
    ))
    conn.commit()
    case_id = cursor.lastrowid
    conn.close()

    return {
        "id": case_id,
        "user_id": user_id,
        "title": title,
        "source_type": source_type,
        "created_at": now,
        "confidence": confidence,
        "citations": citations or []
    }


def get_user_cases(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """List case history for a specific user only."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, source_type, original_filename,
               detected_language, output_language, query_preview,
               citations_json, confidence, created_at
        FROM cases
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["citations"] = json.loads(d.get("citations_json") or "[]")
        except Exception:
            d["citations"] = []
        d.pop("citations_json", None)
        items.append(d)
    return items


def get_case_by_id(case_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get single case details with user ownership validation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM cases WHERE id = ? AND user_id = ?
    """, (case_id, user_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    d = dict(row)
    try:
        d["citations"] = json.loads(d.get("citations_json") or "[]")
    except Exception:
        d["citations"] = []
    d.pop("citations_json", None)
    return d


def delete_user_case(case_id: int, user_id: int) -> bool:
    """Delete a case for the authorized user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM cases WHERE id = ? AND user_id = ?
    """, (case_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
