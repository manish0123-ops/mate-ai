
import sqlite3

from datetime import datetime, timezone

from cognitive.memory import get_connection


def initialize_relationships():
    """Create the memory relationships table."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source_memory_id INTEGER NOT NULL,
                target_memory_id INTEGER NOT NULL,

                relationship_type TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 1.0,

                created_at TEXT NOT NULL,

                FOREIGN KEY (source_memory_id)
                    REFERENCES memories(id),

                FOREIGN KEY (target_memory_id)
                    REFERENCES memories(id),

                UNIQUE (
                    source_memory_id,
                    target_memory_id,
                    relationship_type
                )
            )
        """)

        connection.commit()


def add_relationship(
    source_memory_id,
    target_memory_id,
    relationship_type,
    confidence=1.0
):
    """Connect two existing memories."""

    allowed_types = {
        "supports",
        "related_to",
        "updates",
        "depends_on",
        "contradicts"
    }

    if source_memory_id == target_memory_id:
        raise ValueError("A memory cannot relate to itself.")

    if relationship_type not in allowed_types:
        raise ValueError("Invalid relationship type.")

    if (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0.0 <= confidence <= 1.0
    ):
        raise ValueError("Confidence must be between 0 and 1.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        ids = connection.execute("""
            SELECT id
            FROM memories
            WHERE id IN (?, ?)
              AND is_active = 1
        """, (source_memory_id, target_memory_id)).fetchall()

        if len(ids) != 2:
            raise ValueError(
                "Both memories must exist and be active."
            )

        cursor = connection.execute("""
            INSERT OR IGNORE INTO memory_relationships
            (
                source_memory_id,
                target_memory_id,
                relationship_type,
                confidence,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            source_memory_id,
            target_memory_id,
            relationship_type,
            confidence,
            now
        ))

        connection.commit()

        return cursor.rowcount == 1


def get_relationships(memory_id):
    """Retrieve all relationships connected to a memory."""

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM memory_relationships
            WHERE source_memory_id = ?
               OR target_memory_id = ?
            ORDER BY created_at DESC
        """, (memory_id, memory_id)).fetchall()

        return [dict(row) for row in rows]
