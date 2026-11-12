
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


def initialize_self_model():
    """Create MATE's self-model tables."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                score REAL,
                evidence TEXT,
                evaluated_at TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS improvement_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        connection.commit()


def record_capability(name, description, score, evidence):
    """Record a capability assessment supported by evidence."""

    if not name.strip():
        raise ValueError("Capability name cannot be empty.")

    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    if not evidence.strip():
        raise ValueError("Evidence is required.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO capabilities
            (name, description, score, evidence, evaluated_at)
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(name) DO UPDATE SET
                description = excluded.description,
                score = excluded.score,
                evidence = excluded.evidence,
                evaluated_at = excluded.evaluated_at
        """, (
            name.strip(),
            description.strip(),
            score,
            evidence.strip(),
            now
        ))

        connection.commit()


def get_capabilities():
    """Retrieve MATE's current capability profile."""

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM capabilities
            ORDER BY name
        """).fetchall()

        return [dict(row) for row in rows]


def create_improvement_goal(goal, reason):
    """Add a new improvement objective."""

    if not goal.strip():
        raise ValueError("Goal cannot be empty.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO improvement_goals
            (goal, reason, status, created_at)
            VALUES (?, ?, 'pending', ?)
        """, (
            goal.strip(),
            reason.strip(),
            now
        ))

        connection.commit()
        return cursor.lastrowid


def get_improvement_goals(status=None):
    """Retrieve improvement objectives."""

    with get_connection() as connection:

        if status:
            rows = connection.execute("""
                SELECT *
                FROM improvement_goals
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,)).fetchall()

        else:
            rows = connection.execute("""
                SELECT *
                FROM improvement_goals
                ORDER BY created_at DESC
            """).fetchall()

        return [dict(row) for row in rows]


def update_goal_status(goal_id, status):
    """Update the progress of an improvement objective."""

    allowed_statuses = (
        "pending",
        "in_progress",
        "completed",
        "rejected"
    )

    if status not in allowed_statuses:
        raise ValueError("Invalid goal status.")

    completed_at = None

    if status == "completed":
        completed_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        cursor = connection.execute("""
            UPDATE improvement_goals
            SET status = ?, completed_at = ?
            WHERE id = ?
        """, (
            status,
            completed_at,
            goal_id
        ))

        connection.commit()
        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize_self_model()

    print("MATE Self-Model Engine initialized.")
    print("Database:", DB_PATH)
