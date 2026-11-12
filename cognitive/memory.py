
import sqlite3
import re

from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were",
    "what", "who", "where", "when", "why", "how",
    "do", "does", "did", "can", "could", "would",
    "my", "me", "i", "you", "your", "we", "our",
    "about", "tell", "show", "give", "please",
    "and", "or", "to", "of", "in", "on", "for",
    "with", "from", "it", "this", "that"
}


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_memory():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        connection.commit()


def add_memory(category, content, source="user", confidence=1.0):

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category cannot be empty.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Content cannot be empty.")

    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source cannot be empty.")

    if (
        not isinstance(confidence, (int, float))
        or not 0.0 <= confidence <= 1.0
    ):
        raise ValueError("Confidence must be between 0 and 1.")

    category = category.strip()
    content = content.strip()

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        existing = connection.execute("""
            SELECT id FROM memories
            WHERE category = ?
              AND content = ?
              AND is_active = 1
            LIMIT 1
        """, (category, content)).fetchone()

        if existing:
            return existing["id"]

        cursor = connection.execute("""
            INSERT INTO memories
            (category, content, source, confidence,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category, content, source, confidence, now, now))

        connection.commit()
        return cursor.lastrowid


def extract_keywords(text):
    """Extract meaningful words from a query."""

    words = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())

    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]


def search_memories(keyword, limit=10):
    """Search memories and rank them by keyword relevance."""

    if not isinstance(keyword, str) or not keyword.strip():
        return []

    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    keywords = extract_keywords(keyword)

    if not keywords:
        return []

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM memories
            WHERE is_active = 1
        """).fetchall()

        ranked = []

        for row in rows:

            content = row["content"].lower()
            category = row["category"].lower()

            matched_words = [
                word for word in keywords
                if word in content or word in category
            ]

            if matched_words:

                score = (
                    len(matched_words) / len(set(keywords))
                ) * 100

                # Prefer matches in the actual memory content.
                content_matches = sum(
                    1 for word in matched_words if word in content
                )

                score += content_matches * 2
                score *= row["confidence"]

                item = dict(row)
                item["relevance_score"] = round(score, 2)
                item["matched_keywords"] = matched_words

                ranked.append(item)

        ranked.sort(
            key=lambda item: (
                item["relevance_score"],
                item["updated_at"]
            ),
            reverse=True
        )

        return ranked[:limit]


def get_memories_by_category(category, limit=20):
    """Retrieve active memories belonging to a category."""

    if not isinstance(category, str) or not category.strip():
        return []

    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM memories
            WHERE is_active = 1
              AND LOWER(category) = LOWER(?)
            ORDER BY updated_at DESC
            LIMIT ?
        """, (category.strip(), limit)).fetchall()

        return [dict(row) for row in rows]


def get_all_memories(limit=100):

    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM memories
            WHERE is_active = 1
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def update_memory(
    memory_id,
    content=None,
    category=None,
    confidence=None
):
    """Update an existing active memory."""

    changes = {}
    now = datetime.now(timezone.utc).isoformat()

    if content is not None:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Content cannot be empty.")
        changes["content"] = content.strip()

    if category is not None:
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category cannot be empty.")
        changes["category"] = category.strip()

    if confidence is not None:
        if (
            not isinstance(confidence, (int, float))
            or not 0.0 <= confidence <= 1.0
        ):
            raise ValueError("Confidence must be between 0 and 1.")
        changes["confidence"] = confidence

    if not changes:
        return False

    assignments = ", ".join(
        f"{column} = ?" for column in changes
    )

    values = list(changes.values())
    values.extend([now, memory_id])

    with get_connection() as connection:

        cursor = connection.execute(
            f"""
            UPDATE memories
            SET {assignments}, updated_at = ?
            WHERE id = ? AND is_active = 1
            """,
            values
        )

        connection.commit()
        return cursor.rowcount > 0


def deactivate_memory(memory_id):
    """Deactivate a memory without deleting it."""

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        cursor = connection.execute("""
            UPDATE memories
            SET is_active = 0, updated_at = ?
            WHERE id = ? AND is_active = 1
        """, (now, memory_id))

        connection.commit()
        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize_memory()
    print("MATE Memory Engine initialized.")
    print("Database:", DB_PATH)
