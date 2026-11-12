
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "mate_memory.db"


# Category-based importance defaults.
CATEGORY_SCORES = {
    "project_vision": 95,
    "goal": 90,
    "preference": 85,
    "instruction": 90,
    "identity": 85,
    "experience": 65,
    "knowledge": 60,
    "project": 75,
    "general": 50
}


def calculate_importance(category, content):
    """Estimate memory importance using transparent rules."""

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category cannot be empty.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Content cannot be empty.")

    category = category.strip().lower()
    content = content.strip().lower()

    score = CATEGORY_SCORES.get(category, 50)

    # Long-term value indicators
    long_term_terms = [
        "long-term", "future", "always", "goal",
        "vision", "plan", "develop", "build"
    ]

    # User preference indicators
    preference_terms = [
        "i prefer", "i want", "i need",
        "my preference", "i like"
    ]

    # Reusable information indicators
    reusable_terms = [
        "remember", "important", "project",
        "architecture", "system", "routine"
    ]

    if any(term in content for term in long_term_terms):
        score += 5

    if any(term in content for term in preference_terms):
        score += 5

    if any(term in content for term in reusable_terms):
        score += 5

    # Keep the score within 0–100.
    return max(0, min(100, score))


def update_memory_importance(memory_id):
    """Calculate and save importance for an existing memory."""

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        row = connection.execute("""
            SELECT category, content
            FROM memories
            WHERE id = ? AND is_active = 1
        """, (memory_id,)).fetchone()

        if row is None:
            return None

        score = calculate_importance(row[0], row[1])

        connection.execute("""
            UPDATE memories
            SET importance = ?
            WHERE id = ?
        """, (score, memory_id))

        connection.commit()

        return score


def update_all_memory_importance():
    """Recalculate importance for all active memories."""

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        rows = connection.execute("""
            SELECT id
            FROM memories
            WHERE is_active = 1
        """).fetchall()

    results = {}

    for row in rows:
        memory_id = row[0]
        results[memory_id] = update_memory_importance(memory_id)

    return results
