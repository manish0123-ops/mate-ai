
import json
import urllib.request
import urllib.error


OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text):
    """Generate a local embedding using Ollama."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text cannot be empty.")

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text.strip()
    }

    request = urllib.request.Request(
        OLLAMA_EMBED_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        embeddings = result.get("embeddings")

        if not embeddings or not embeddings[0]:
            raise RuntimeError("Ollama returned an empty embedding.")

        return embeddings[0]

    except urllib.error.URLError as error:
        raise RuntimeError(
            "Could not connect to local Ollama."
        ) from error


if __name__ == "__main__":
    sample = "MATE is my private AI assistant."

    vector = generate_embedding(sample)

    print("Embedding model:", EMBEDDING_MODEL)
    print("Vector dimensions:", len(vector))
    print("First five values:", vector[:5])
    print("Embedding generation successful.")


import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


def initialize_embedding_storage():
    """Create a separate table for storing memory embeddings."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS memory_embeddings (
                memory_id INTEGER PRIMARY KEY,
                embedding TEXT NOT NULL,
                model TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (memory_id)
                    REFERENCES memories(id)
            )
        """)

        connection.commit()


if __name__ == "__main__":
    initialize_embedding_storage()
    print("MATE embedding storage initialized.")
    print("Database:", DB_PATH)


def synchronize_memory_embeddings():
    """Generate embeddings for memories that do not have one."""

    import json
    from datetime import datetime, timezone

    initialize_embedding_storage()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.row_factory = sqlite3.Row

        memories = connection.execute("""
            SELECT id, content
            FROM memories
            WHERE is_active = 1
            AND id NOT IN (
                SELECT memory_id FROM memory_embeddings
            )
        """).fetchall()

        created = 0
        failed = 0

        for memory in memories:

            try:
                vector = generate_embedding(memory["content"])

                connection.execute("""
                    INSERT INTO memory_embeddings (
                        memory_id,
                        embedding,
                        model,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    memory["id"],
                    json.dumps(vector),
                    EMBEDDING_MODEL,
                    datetime.now(timezone.utc).isoformat()
                ))

                connection.commit()
                created += 1

            except Exception as error:
                print(
                    f"Embedding failed for memory "
                    f"{memory['id']}: {error}"
                )
                failed += 1

    return {
        "created": created,
        "failed": failed
    }
