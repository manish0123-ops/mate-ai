
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_reflection():
    """Create the task reflection table."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS task_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                expected_outcome TEXT NOT NULL,
                actual_outcome TEXT NOT NULL,
                result_status TEXT NOT NULL,
                identified_issue TEXT,
                lesson TEXT,
                improvement_suggestion TEXT,
                evidence TEXT NOT NULL,
                created_at TEXT NOT NULL,
                reviewed INTEGER DEFAULT 0
            )
        """)

        connection.commit()


def record_reflection(
    task_name,
    expected_outcome,
    actual_outcome,
    result_status,
    evidence,
    identified_issue="",
    lesson="",
    improvement_suggestion=""
):
    """Store an evidence-supported task reflection."""

    allowed_statuses = (
        "success",
        "partial",
        "failure",
        "unknown"
    )

    required = [
        task_name,
        expected_outcome,
        actual_outcome,
        evidence
    ]

    if not all(
        isinstance(value, str) and value.strip()
        for value in required
    ):
        raise ValueError("Required fields cannot be empty.")

    if result_status not in allowed_statuses:
        raise ValueError("Invalid result status.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO task_reflections (
                task_name,
                expected_outcome,
                actual_outcome,
                result_status,
                identified_issue,
                lesson,
                improvement_suggestion,
                evidence,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_name.strip(),
            expected_outcome.strip(),
            actual_outcome.strip(),
            result_status,
            identified_issue.strip(),
            lesson.strip(),
            improvement_suggestion.strip(),
            evidence.strip(),
            now
        ))

        connection.commit()
        return cursor.lastrowid


def get_reflections(limit=20):
    """Retrieve recent task reflections."""

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM task_reflections
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def get_reflections_by_status(status):
    """Retrieve reflections filtered by result."""

    allowed_statuses = (
        "success",
        "partial",
        "failure",
        "unknown"
    )

    if status not in allowed_statuses:
        raise ValueError("Invalid result status.")

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM task_reflections
            WHERE result_status = ?
            ORDER BY created_at DESC
        """, (status,)).fetchall()

        return [dict(row) for row in rows]


def mark_reflection_reviewed(reflection_id):
    """Mark a reflection as reviewed."""

    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE task_reflections
            SET reviewed = 1
            WHERE id = ?
        """, (reflection_id,))

        connection.commit()
        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize_reflection()
    print("MATE Reflection Engine initialized.")
    print("Database:", DB_PATH)
