
import json
import sqlite3

from pathlib import Path

from cognitive.embeddings import (
    DB_PATH,
    EMBEDDING_MODEL,
    generate_embedding,
    synchronize_memory_embeddings
)

from cognitive.similarity import cosine_similarity


def semantic_search(query, limit=5, threshold=0.0):
    """Retrieve active memories using semantic similarity."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("Limit must be a positive integer.")

    if not isinstance(threshold, (int, float)) or not -1 <= threshold <= 1:
        raise ValueError("Threshold must be between -1 and 1.")

    # Ensure newly added memories also get embeddings.
    synchronize_memory_embeddings()

    query_vector = generate_embedding(query)

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        rows = connection.execute("""
            SELECT
               m.id,
               m.category,
               m.content,
               m.confidence,
               m.importance,
               e.embedding
            FROM memories AS m
            INNER JOIN memory_embeddings AS e
                ON m.id = e.memory_id
            WHERE m.is_active = 1
            AND e.model = ?
        """, (EMBEDDING_MODEL,)).fetchall()

    results = []

    for row in rows:

        memory_id, category, content, confidence, importance, stored_vector = row

        memory_vector = json.loads(stored_vector)

        similarity = cosine_similarity(
            query_vector,
            memory_vector
        )

        if similarity >= threshold:

            results.append({
                "id": memory_id,
                "category": category,
                "content": content,
                "confidence": confidence,
                "similarity": round(similarity, 4),
                "importance": importance,
                "retrieval_score": round(
                    (similarity * 0.75) + ((importance / 100) * 0.25),
                    4
                ) 
            })

    results.sort(
        key=lambda item: item["retrieval_score"],
        reverse=True
    )

    return results[:limit]


if __name__ == "__main__":

    print("MATE SEMANTIC MEMORY SEARCH")

    query = "Tell me about my private artificial intelligence project."

    results = semantic_search(query)

    for item in results:
        print("\nCategory:", item["category"])
        print("Similarity:", item["similarity"])
        print("Memory:", item["content"])
