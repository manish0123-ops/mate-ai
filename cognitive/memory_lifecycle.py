
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


def initialize_lifecycle():
    """Create memory version history storage."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS memory_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                previous_content TEXT NOT NULL,
                previous_category TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT
            )
        """)

        connection.commit()

    return True


def get_memory_history(memory_id):
    """Retrieve previous versions of a memory."""

    initialize_lifecycle()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        rows = connection.execute("""
            SELECT
                id,
                memory_id,
                previous_content,
                previous_category,
                changed_at,
                change_reason
            FROM memory_history
            WHERE memory_id = ?
            ORDER BY id DESC
        """, (memory_id,)).fetchall()

    return [
        {
            "history_id": row[0],
            "memory_id": row[1],
            "previous_content": row[2],
            "previous_category": row[3],
            "changed_at": row[4],
            "change_reason": row[5]
        }
        for row in rows
    ]

def update_memory_safely(
    memory_id,
    new_content=None,
    new_category=None,
    reason="User-approved memory update"
):
    """Save the previous version before updating a memory."""

    initialize_lifecycle()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.row_factory = sqlite3.Row

        memory = connection.execute("""
            SELECT id, content, category
            FROM memories
            WHERE id = ? AND is_active = 1
        """, (memory_id,)).fetchone()

        if memory is None:
            raise ValueError("Active memory not found.")

        content = (
            new_content.strip()
            if isinstance(new_content, str) and new_content.strip()
            else memory["content"]
        )

        category = (
            new_category.strip()
            if isinstance(new_category, str) and new_category.strip()
            else memory["category"]
        )

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Update reason cannot be empty.")

        if (
            content == memory["content"]
            and category == memory["category"]
        ):
            return False

        now = datetime.now(timezone.utc).isoformat()

        # Preserve the old version first.
        connection.execute("""
            INSERT INTO memory_history (
                memory_id,
                previous_content,
                previous_category,
                changed_at,
                change_reason
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            memory_id,
            memory["content"],
            memory["category"],
            now,
            reason.strip()
        ))

        # Update the active memory.
        connection.execute("""
            UPDATE memories
            SET content = ?,
                category = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            content,
            category,
            now,
            memory_id
        ))

        # Remove stale embedding so it can be regenerated.
        connection.execute("""
            DELETE FROM memory_embeddings
            WHERE memory_id = ?
        """, (memory_id,))

        connection.commit()

    return True

def restore_memory_version(memory_id, history_id):
    """Restore a previous memory version safely."""

    initialize_lifecycle()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.row_factory = sqlite3.Row

        current = connection.execute("""
            SELECT id, content, category
            FROM memories
            WHERE id = ? AND is_active = 1
        """, (memory_id,)).fetchone()

        if current is None:
            raise ValueError("Active memory not found.")

        previous = connection.execute("""
            SELECT previous_content, previous_category
            FROM memory_history
            WHERE id = ? AND memory_id = ?
        """, (history_id, memory_id)).fetchone()

        if previous is None:
            raise ValueError("Requested history version not found.")

        now = datetime.now(timezone.utc).isoformat()

        # Preserve the current version before restoring.
        connection.execute("""
            INSERT INTO memory_history (
                memory_id,
                previous_content,
                previous_category,
                changed_at,
                change_reason
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            memory_id,
            current["content"],
            current["category"],
            now,
            f"Restored from history record {history_id}"
        ))

        # Restore the selected previous version.
        connection.execute("""
            UPDATE memories
            SET content = ?,
                category = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            previous["previous_content"],
            previous["previous_category"],
            now,
            memory_id
        ))

        # Remove the outdated embedding.
        connection.execute("""
            DELETE FROM memory_embeddings
            WHERE memory_id = ?
        """, (memory_id,))

        connection.commit()

    return True
