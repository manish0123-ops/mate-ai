
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


def initialize_learning():
    """Create the learning plans table."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS learning_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capability TEXT NOT NULL,
                current_score REAL,
                target_score REAL,
                identified_weakness TEXT NOT NULL,
                learning_action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'proposed',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        connection.commit()


def create_learning_plan(
    capability,
    current_score,
    target_score,
    identified_weakness,
    learning_action
):
    """Create a proposed improvement plan."""

    if not isinstance(capability, str) or not capability.strip():
        raise ValueError("Capability cannot be empty.")

    if not isinstance(current_score, (int, float)):
        raise ValueError("Current score must be numeric.")

    if not isinstance(target_score, (int, float)):
        raise ValueError("Target score must be numeric.")

    if not 0 <= current_score <= 100:
        raise ValueError("Current score must be between 0 and 100.")

    if not 0 <= target_score <= 100:
        raise ValueError("Target score must be between 0 and 100.")

    if target_score <= current_score:
        raise ValueError("Target must exceed current score.")

    if not identified_weakness.strip():
        raise ValueError("Weakness description is required.")

    if not learning_action.strip():
        raise ValueError("Learning action is required.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO learning_plans (
                capability,
                current_score,
                target_score,
                identified_weakness,
                learning_action,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, 'proposed', ?, ?)
        """, (
            capability.strip(),
            current_score,
            target_score,
            identified_weakness.strip(),
            learning_action.strip(),
            now,
            now
        ))

        connection.commit()
        return cursor.lastrowid


def get_learning_plans(status=None):
    """Retrieve learning plans."""

    with get_connection() as connection:

        if status:
            rows = connection.execute("""
                SELECT *
                FROM learning_plans
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,)).fetchall()

        else:
            rows = connection.execute("""
                SELECT *
                FROM learning_plans
                ORDER BY created_at DESC
            """).fetchall()

        return [dict(row) for row in rows]


def update_learning_status(plan_id, status):
    """Update learning plan progress."""

    allowed_statuses = (
        "proposed",
        "approved",
        "in_progress",
        "completed",
        "rejected"
    )

    if status not in allowed_statuses:
        raise ValueError("Invalid learning status.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE learning_plans
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, now, plan_id))

        connection.commit()
        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize_learning()
    print("MATE Learning Engine initialized.")
    print("Database:", DB_PATH)
