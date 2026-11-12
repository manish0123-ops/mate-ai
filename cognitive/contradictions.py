import json
import urllib.request
import urllib.error
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


def initialize_contradictions():
    """Create storage for potential memory contradictions."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS memory_contradictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                existing_memory_id INTEGER NOT NULL,
                new_content TEXT NOT NULL,
                new_category TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                resolved_at TEXT
            )
        """)

        connection.commit()

    return True


def record_contradiction(
    existing_memory_id,
    new_content,
    new_category,
    reason
):
    """Record a potential contradiction without changing memories."""

    if not isinstance(existing_memory_id, int) or isinstance(
        existing_memory_id, bool
    ):
        raise ValueError("Existing memory ID must be an integer.")

    if not isinstance(new_content, str) or not new_content.strip():
        raise ValueError("New content cannot be empty.")

    if not isinstance(new_category, str) or not new_category.strip():
        raise ValueError("Category cannot be empty.")

    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Contradiction reason cannot be empty.")

    initialize_contradictions()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        existing = connection.execute("""
            SELECT id
            FROM memories
            WHERE id = ? AND is_active = 1
        """, (existing_memory_id,)).fetchone()

        if existing is None:
            raise ValueError("Existing active memory not found.")

        cursor = connection.execute("""
            INSERT INTO memory_contradictions (
                existing_memory_id,
                new_content,
                new_category,
                reason,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (
            existing_memory_id,
            new_content.strip(),
            new_category.strip(),
            reason.strip(),
            datetime.now(timezone.utc).isoformat()
        ))

        connection.commit()

        return cursor.lastrowid


def get_pending_contradictions():
    """Retrieve unresolved contradiction records."""

    initialize_contradictions()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        rows = connection.execute("""
            SELECT *
            FROM memory_contradictions
            WHERE status = 'pending'
            ORDER BY id DESC
        """).fetchall()

    return rows

def resolve_contradiction(contradiction_id, decision):
    """Resolve a contradiction after an explicit user decision."""

    allowed_decisions = {
        "accepted",
        "rejected",
        "contextual"
    }

    if decision not in allowed_decisions:
        raise ValueError(
            "Decision must be accepted, rejected, or contextual."
        )

    initialize_contradictions()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        row = connection.execute("""
            SELECT status
            FROM memory_contradictions
            WHERE id = ?
        """, (contradiction_id,)).fetchone()

        if row is None:
            raise ValueError("Contradiction record not found.")

        if row[0] != "pending":
            raise ValueError("Contradiction has already been resolved.")

        connection.execute("""
            UPDATE memory_contradictions
            SET status = ?,
                resolved_at = ?
            WHERE id = ?
        """, (
            decision,
            datetime.now(timezone.utc).isoformat(),
            contradiction_id
        ))

        connection.commit()

    return True

def detect_contradiction(existing_content, new_content):
    """Use local Ollama to classify two statements."""

    if not existing_content.strip() or not new_content.strip():
        raise ValueError("Both statements are required.")

    payload = {
        "model": "llama3.2:3b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a memory consistency evaluator. "
                    "Compare two statements and determine their relationship. "
                    "Return JSON only with these fields: "
                    "relationship and reason. "
                    "relationship must be one of: "
                    "contradiction, compatible, contextual, uncertain. "
                    "A changed preference is not automatically a contradiction. "
                    "Different contexts or time periods may be compatible. "
                    "Do not assume either statement is true."
                )
            },
            {
                "role": "user",
                "content": (
                    "EXISTING MEMORY:\n"
                    + existing_content
                    + "\n\nNEW INFORMATION:\n"
                    + new_content
                )
            }
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0
        }
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = json.loads(result["message"]["content"])

        relationship = answer.get("relationship")
        reason = answer.get("reason")

        allowed = {
            "contradiction",
            "compatible",
            "contextual",
            "uncertain"
        }

        if relationship not in allowed or not isinstance(reason, str):
            raise ValueError("Invalid evaluator response.")

        return {
            "relationship": relationship,
            "reason": reason
        }

    except (
        urllib.error.URLError,
        KeyError,
        json.JSONDecodeError,
        TimeoutError
    ) as error:
        raise RuntimeError(
            "Local contradiction evaluation failed."
        ) from error

def check_new_information(new_content, new_category):
    """Compare new information against related active memories."""

    from cognitive.semantic_search import semantic_search

    if not isinstance(new_content, str) or not new_content.strip():
        raise ValueError("New information cannot be empty.")

    if not isinstance(new_category, str) or not new_category.strip():
        raise ValueError("Category cannot be empty.")

    candidates = semantic_search(new_content, limit=5)

    results = []

    for memory in candidates:

        # Avoid comparing unrelated categories.
        if memory["category"] != new_category:
            continue

        evaluation = detect_contradiction(
            memory["content"],
            new_content
        )

        result = {
            "existing_memory_id": memory["id"],
            "relationship": evaluation["relationship"],
            "reason": evaluation["reason"]
        }

        if evaluation["relationship"] == "contradiction":

            contradiction_id = record_contradiction(
                memory["id"],
                new_content,
                new_category,
                evaluation["reason"]
            )

            result["contradiction_id"] = contradiction_id

        results.append(result)

    return results

def initialize_conflict_groups():
    """Create storage for grouped contradiction reviews."""

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS contradiction_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                new_content TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                resolved_at TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS contradiction_group_items (
                group_id INTEGER NOT NULL,
                contradiction_id INTEGER NOT NULL UNIQUE,
                PRIMARY KEY (group_id, contradiction_id)
            )
        """)

        connection.commit()

    return True

def create_conflict_group(contradiction_ids):
    """Group related pending contradictions into one review."""

    if not isinstance(contradiction_ids, list) or not contradiction_ids:
        raise ValueError("Contradiction IDs are required.")

    if any(
        not isinstance(item, int) or isinstance(item, bool)
        for item in contradiction_ids
    ):
        raise ValueError("Contradiction IDs must be integers.")

    contradiction_ids = list(dict.fromkeys(contradiction_ids))

    initialize_conflict_groups()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        placeholders = ",".join("?" for _ in contradiction_ids)

        rows = connection.execute(
            f"""
            SELECT id, new_content, new_category
            FROM memory_contradictions
            WHERE id IN ({placeholders})
            AND status = 'pending'
            """,
            contradiction_ids
        ).fetchall()

        if len(rows) != len(contradiction_ids):
            raise ValueError(
                "All contradiction records must be pending."
            )

        contents = {row[1] for row in rows}
        categories = {row[2] for row in rows}

        if len(contents) != 1 or len(categories) != 1:
            raise ValueError(
                "Contradictions must concern the same new information."
            )

        cursor = connection.execute("""
            INSERT INTO contradiction_groups (
                new_content,
                category,
                status,
                created_at
            )
            VALUES (?, ?, 'pending', ?)
        """, (
            rows[0][1],
            rows[0][2],
            datetime.now(timezone.utc).isoformat()
        ))

        group_id = cursor.lastrowid

        connection.executemany("""
            INSERT INTO contradiction_group_items (
                group_id,
                contradiction_id
            )
            VALUES (?, ?)
        """, [
            (group_id, contradiction_id)
            for contradiction_id in contradiction_ids
        ])

        connection.commit()

    return group_id
def get_conflict_group(group_id):
    """Return a conflict group and all its linked contradictions."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        group = conn.execute(
            """
            SELECT *
            FROM contradiction_groups
            WHERE id = ?
            """,
            (group_id,)
        ).fetchone()

        if group is None:
            return None

        contradictions = conn.execute(
            """
            SELECT c.*
            FROM memory_contradictions c
            JOIN contradiction_group_items g
                ON c.id = g.contradiction_id
            WHERE g.group_id = ?
            ORDER BY c.id
            """,
            (group_id,)
        ).fetchall()

        return {
            "group": dict(group),
            "contradictions": [dict(item) for item in contradictions]
        }

    finally:
        conn.close()


def resolve_conflict_group(group_id, decision):
    """Resolve a group and all linked contradictions atomically."""

    allowed_decisions = {"accepted", "rejected", "contextual"}

    if decision not in allowed_decisions:
        raise ValueError("Invalid conflict resolution decision.")

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("BEGIN IMMEDIATE")

        group = conn.execute(
            """
            SELECT status
            FROM contradiction_groups
            WHERE id = ?
            """,
            (group_id,)
        ).fetchone()

        if group is None:
            raise ValueError("Conflict group not found.")

        if group[0] != "pending":
            raise ValueError("Conflict group is already resolved.")

        contradiction_ids = conn.execute(
            """
            SELECT contradiction_id
            FROM contradiction_group_items
            WHERE group_id = ?
            """,
            (group_id,)
        ).fetchall()

        if not contradiction_ids:
            raise ValueError("Conflict group has no contradictions.")

        ids = [item[0] for item in contradiction_ids]
        placeholders = ",".join("?" for _ in ids)

        pending_count = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM memory_contradictions
            WHERE id IN ({placeholders})
              AND status = 'pending'
            """,
            ids
        ).fetchone()[0]

        if pending_count != len(ids):
            raise ValueError(
                "Not all contradictions in this group are pending."
            )

        now = datetime.now(timezone.utc).isoformat()

        conn.execute(
            f"""
            UPDATE memory_contradictions
            SET status = ?, resolved_at = ?
            WHERE id IN ({placeholders})
            """,
            [decision, now] + ids
        )

        conn.execute(
            """
            UPDATE contradiction_groups
            SET status = ?, resolved_at = ?
            WHERE id = ?
            """,
            (decision, now, group_id)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()