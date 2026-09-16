"""
SQLite database for user accounts and case history.

SQLite is used because:
- Built into Python stdlib (zero dependencies)
- Zero configuration/setup
- Perfect for single-user or low-concurrency scenarios
- Stores user accounts and case metadata (not the RAG index itself)

Schema:
- users: id, username, email, hashed_password, created_at
- cases: id, user_id, title, content_type, content, language, created_at, analysis_result
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import secrets

DB_PATH = "legal_rag.db"


def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    # Cases table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            created_at TEXT NOT NULL,
            analysis_result TEXT,
           FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, pwd_hash = password_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False


def create_user(username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
    """Create a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)
        created_at = datetime.utcnow().isoformat()

        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, created_at)
        )
        conn.commit()

        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "created_at": created_at
        }
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user and return their info."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ? AND is_active = 1",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(password, row['password_hash']):
        return {
            "id": row['id'],
            "username": row['username'],
            "email": row['email']
        }
    return None


def create_case(
    user_id: int,
    title: str,
    content_type: str,
    content: str,
    language: str = "en"
) -> Optional[Dict[str, Any]]:
    """Create a new case record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        created_at = datetime.utcnow().isoformat()

        cursor.execute(
            "INSERT INTO cases (user_id, title, content_type, content, language, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, title, content_type, content, language, created_at)
        )
        conn.commit()

        case_id = cursor.lastrowid
        return {
            "id": case_id,
            "user_id": user_id,
            "title": title,
            "content_type": content_type,
            "language": language,
            "created_at": created_at,
            "analysis_result": None
        }
    finally:
        conn.close()


def update_case_analysis(case_id: int, analysis_result: str) -> bool:
    """Update the analysis result for a case."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE cases SET analysis_result = ? WHERE id = ?",
        (analysis_result, case_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def get_user_cases(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all cases for a user, newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM cases WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_case(user_id: int, case_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific case by ID (with user ownership check)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM cases WHERE id = ? AND user_id = ?",
        (case_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def delete_case(user_id: int, case_id: int) -> bool:
    """Delete a case (with user ownership check)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cases WHERE id = ? AND user_id = ?",
        (case_id, user_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
