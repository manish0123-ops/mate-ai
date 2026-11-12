
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from cognitive.embeddings import DB_PATH, EMBEDDING_MODEL
from cognitive.similarity import cosine_similarity
import json


def find_similar_memories(memory_id, threshold=0.80):
    """Find memories semantically similar to a selected memory."""

    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1.")

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        rows = connection.execute("""
            SELECT
                m.id,
                m.category,
                m.content,
                m.confidence,
                m.importance,
                e.embedding
            FROM memories m
            JOIN memory_embeddings e
                ON m.id = e.memory_id
            WHERE m.is_active = 1
            AND e.model = ?
            AND m.id != ?
        """, (EMBEDDING_MODEL, memory_id)).fetchall()

        selected = connection.execute("""
            SELECT id, category, content
            FROM memories
            WHERE id = ? AND is_active = 1
        """, (memory_id,)).fetchone()

    if selected is None:
        raise ValueError("Selected memory does not exist or is inactive.")

    selected_vector = None

    with sqlite3.connect(DB_PATH, timeout=10) as connection:
        row = connection.execute("""
            SELECT embedding
            FROM memory_embeddings
            WHERE memory_id = ? AND model = ?
        """, (memory_id, EMBEDDING_MODEL)).fetchone()

    if row is None:
        raise ValueError("Selected memory has no embedding.")

    selected_vector = json.loads(row[0])

    results = []

    for item in rows:

        vector = json.loads(item[5])

        score = cosine_similarity(selected_vector, vector)

        if score >= threshold:
            results.append({
                "id": item[0],
                "category": item[1],
                "content": item[2],
                "confidence": item[3],
                "importance": item[4],
                "similarity": round(score, 4)
            })

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results


def create_consolidated_memory(category, content, source_ids):
    """Create a new consolidated memory without changing originals."""

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category cannot be empty.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Content cannot be empty.")

    if not isinstance(source_ids, list) or not source_ids:
        raise ValueError("Source memory IDs are required.")

    if any(
        not isinstance(memory_id, int) or isinstance(memory_id, bool)
        for memory_id in source_ids
    ):
        raise ValueError("Every source ID must be an integer.")

    source_ids = list(dict.fromkeys(source_ids))

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        placeholders = ",".join("?" for _ in source_ids)

        rows = connection.execute(
            f"""
            SELECT id, importance, confidence
            FROM memories
            WHERE id IN ({placeholders})
            AND is_active = 1
            """,
            source_ids
        ).fetchall()

        if len(rows) != len(source_ids):
            raise ValueError(
                "One or more source memories are missing or inactive."
            )

        importance = max(row[1] for row in rows)
        confidence = min(row[2] for row in rows)

        cursor = connection.execute("""
            INSERT INTO memories (
                category,
                content,
                source,
                confidence,
                created_at,
                updated_at,
                is_active,
                importance
            )
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            category.strip(),
            content.strip(),
            "consolidation",
            confidence,
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
            importance
        ))

        new_memory_id = cursor.lastrowid

        connection.commit()

    return new_memory_id

def initialize_consolidation_tracking():
    """Create a table recording the origin of consolidated memories."""

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS memory_consolidation_sources (
                consolidated_memory_id INTEGER NOT NULL,
                source_memory_id INTEGER NOT NULL,
                PRIMARY KEY (
                    consolidated_memory_id,
                    source_memory_id
                )
            )
        """)

        connection.commit()


def link_consolidated_sources(consolidated_id, source_ids):
    """Record which original memories contributed to a new memory."""

    if not isinstance(source_ids, list) or not source_ids:
        raise ValueError("Source IDs are required.")

    source_ids = list(dict.fromkeys(source_ids))

    if any(
        not isinstance(item, int) or isinstance(item, bool)
        for item in source_ids
    ):
        raise ValueError("Source IDs must be integers.")

    if consolidated_id in source_ids:
        raise ValueError("A memory cannot be its own source.")

    initialize_consolidation_tracking()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        new_memory = connection.execute("""
            SELECT id
            FROM memories
            WHERE id = ? AND is_active = 1
        """, (consolidated_id,)).fetchone()

        if new_memory is None:
            raise ValueError("Consolidated memory does not exist.")

        placeholders = ",".join("?" for _ in source_ids)

        sources = connection.execute(
            f"""
            SELECT id
            FROM memories
            WHERE id IN ({placeholders})
            AND is_active = 1
            """,
            source_ids
        ).fetchall()

        if len(sources) != len(source_ids):
            raise ValueError("One or more source memories are unavailable.")

        connection.executemany("""
            INSERT OR IGNORE INTO memory_consolidation_sources (
                consolidated_memory_id,
                source_memory_id
            )
            VALUES (?, ?)
        """, [
            (consolidated_id, source_id)
            for source_id in source_ids
        ])

        connection.commit()

    return True


def get_consolidation_sources(consolidated_id):
    """Retrieve the original memories behind a consolidated memory."""

    initialize_consolidation_tracking()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        rows = connection.execute("""
            SELECT
                m.id,
                m.category,
                m.content
            FROM memory_consolidation_sources s
            JOIN memories m
                ON m.id = s.source_memory_id
            WHERE s.consolidated_memory_id = ?
            ORDER BY m.id
        """, (consolidated_id,)).fetchall()

    return [
        {
            "id": row[0],
            "category": row[1],
            "content": row[2]
        }
        for row in rows
    ]

def rollback_consolidation(consolidated_id):
    """Deactivate a consolidated memory and preserve its originals."""

    initialize_consolidation_tracking()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.execute("PRAGMA foreign_keys = ON")

        sources = connection.execute("""
            SELECT source_memory_id
            FROM memory_consolidation_sources
            WHERE consolidated_memory_id = ?
        """, (consolidated_id,)).fetchall()

        if not sources:
            raise ValueError(
                "No source records found. Cannot safely rollback."
            )

        consolidated = connection.execute("""
            SELECT is_active
            FROM memories
            WHERE id = ?
        """, (consolidated_id,)).fetchone()

        if consolidated is None:
            raise ValueError("Consolidated memory does not exist.")

        if consolidated[0] == 0:
            return False

        connection.execute("""
            UPDATE memories
            SET is_active = 0
            WHERE id = ?
        """, (consolidated_id,))

        connection.execute("""
            DELETE FROM memory_embeddings
            WHERE memory_id = ?
        """, (consolidated_id,))

        connection.commit()

    return True
