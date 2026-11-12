
import sqlite3
import uuid

from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_evaluator():
    """Create or update the evaluation database schema."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                capability TEXT NOT NULL,
                total_tests INTEGER NOT NULL,
                passed_tests INTEGER NOT NULL,
                accuracy REAL NOT NULL,
                evidence TEXT NOT NULL,
                evaluated_at TEXT NOT NULL
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(evaluations)"
            ).fetchall()
        }

        if "run_id" not in columns:
            connection.execute("""
                ALTER TABLE evaluations
                ADD COLUMN run_id TEXT
            """)

        connection.commit()


def record_evaluation(
    capability,
    total_tests,
    passed_tests,
    evidence,
    run_id=None
):
    """Save an evaluation with a unique run identifier."""

    if not isinstance(capability, str) or not capability.strip():
        raise ValueError("Capability name cannot be empty.")

    if (
        not isinstance(total_tests, int)
        or isinstance(total_tests, bool)
        or total_tests <= 0
    ):
        raise ValueError("Total tests must be a positive integer.")

    if (
        not isinstance(passed_tests, int)
        or isinstance(passed_tests, bool)
    ):
        raise ValueError("Passed tests must be an integer.")

    if not 0 <= passed_tests <= total_tests:
        raise ValueError("Invalid number of passed tests.")

    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError("Evidence is required.")

    if run_id is None:
        run_id = str(uuid.uuid4())

    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("Run ID cannot be empty.")

    accuracy = (passed_tests / total_tests) * 100
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO evaluations (
                run_id,
                capability,
                total_tests,
                passed_tests,
                accuracy,
                evidence,
                evaluated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id.strip(),
            capability.strip(),
            total_tests,
            passed_tests,
            accuracy,
            evidence.strip(),
            now
        ))

        connection.commit()

        return cursor.lastrowid


def get_evaluations(capability=None):

    with get_connection() as connection:

        if capability:
            rows = connection.execute("""
                SELECT *
                FROM evaluations
                WHERE capability = ?
                ORDER BY evaluated_at DESC, id DESC
            """, (capability,)).fetchall()

        else:
            rows = connection.execute("""
                SELECT *
                FROM evaluations
                ORDER BY evaluated_at DESC, id DESC
            """).fetchall()

        return [dict(row) for row in rows]


def get_average_accuracy(capability):

    with get_connection() as connection:

        row = connection.execute("""
            SELECT AVG(accuracy) AS average
            FROM evaluations
            WHERE capability = ?
        """, (capability,)).fetchone()

        return row["average"] or 0.0


if __name__ == "__main__":
    initialize_evaluator()

    print("MATE Evaluation Engine initialized.")
    print("Database:", DB_PATH)
