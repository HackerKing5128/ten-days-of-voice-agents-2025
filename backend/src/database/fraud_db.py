import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

# Database path (in backend/src/)
DB_PATH = Path(__file__).parent.parent / "fraud_cases.db"


def get_connection() -> sqlite3.Connection:
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_database():
    """Create the fraud_cases table if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fraud_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT NOT NULL,
            securityQuestion TEXT,
            securityAnswer TEXT,
            cardEnding TEXT,
            transactionAmount TEXT,
            transactionName TEXT,
            transactionTime TEXT,
            transactionCategory TEXT,
            transactionSource TEXT,
            transactionLocation TEXT,
            status TEXT DEFAULT 'pending_review',
            outcomeNote TEXT,
            createdAt TIMESTAMP,
            updatedAt TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def get_fraud_case(user_name: str) -> Optional[dict]:
    """Fetch pending fraud case for a user"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM fraud_cases 
        WHERE LOWER(userName) = LOWER(?) AND status = 'pending_review'
        LIMIT 1
    """,
        (user_name,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def update_case_status(case_id: int, status: str, note: str) -> bool:
    """Update case status and outcome note"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE fraud_cases 
            SET status = ?, outcomeNote = ?, updatedAt = ?
            WHERE id = ?
        """,
            (status, note, datetime.now().isoformat(), case_id),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error updating case: {e}")
        conn.close()
        return False


def verify_security_answer(user_name: str, answer: str) -> tuple[bool, Optional[dict]]:
    """Check if answer matches (case-insensitive)"""
    case = get_fraud_case(user_name)

    if not case:
        return False, None

    stored_answer = case.get("securityAnswer", "").strip().lower()
    provided_answer = answer.strip().lower()

    is_verified = stored_answer == provided_answer
    return is_verified, case


def get_all_cases() -> list[dict]:
    """Get all fraud cases (for debugging)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fraud_cases")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
