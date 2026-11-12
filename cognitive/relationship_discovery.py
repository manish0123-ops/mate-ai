
import json
import urllib.request
import urllib.error

from cognitive.semantic_search import semantic_search


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

ALLOWED_RELATIONSHIPS = {
    "supports",
    "related_to",
    "updates",
    "depends_on",
    "contradicts"
}


def classify_relationship(memory_a, memory_b):
    """Ask local Ollama to classify two memories."""

    prompt = f"""
You are MATE's memory relationship analyzer.

Analyze these two memories.

MEMORY A:
{memory_a}

MEMORY B:
{memory_b}


Choose exactly one relationship based on the meaning of the memories.

supports:
Memory A provides a reason, evidence, or foundation for Memory B,
or Memory B provides a reason, evidence, or foundation for Memory A.

related_to:
The memories share a topic but neither directly supports,
updates, depends on, or contradicts the other.

updates:
One memory provides newer, corrected, or more specific
information that revises the other.

depends_on:
One memory requires the other as a prerequisite or foundation.

contradicts:
The memories express incompatible claims or preferences.

unrelated:
There is no meaningful conceptual relationship.

IMPORTANT:
1. Compare all five relationship types before deciding.
2. Prefer a specific relationship over related_to when justified.
3. Do not classify memories as supports merely because
   they describe the same project.
4. Do not classify different levels of detail as updates
   unless one genuinely revises the other.
5. Do not invent facts or infer chronology without evidence.
6. If uncertain, choose related_to or unrelated.


Return JSON only:
{{
    "relationship": "related_to",
    "confidence": 0.0,
    "reason": "Brief explanation"
}}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:
            result = json.loads(response.read().decode("utf-8"))

        content = result["message"]["content"]
        classification = json.loads(content)

        relationship = classification.get("relationship")
        confidence = classification.get("confidence")
        reason = classification.get("reason")

        if relationship not in ALLOWED_RELATIONSHIPS | {"unrelated"}:
            raise ValueError("Invalid relationship returned by AI.")

        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or not 0.50 <= confidence <= 1
        ):
           raise ValueError(
                f"Relationship suggestion rejected: "
                f"model confidence was {confidence}. "
                "Minimum required confidence is 0.50."
            )

        if not isinstance(reason, str):
            raise ValueError("Invalid explanation returned by AI.")

        return {
            "relationship": relationship,
            "confidence": float(confidence),
            "reason": reason
        }

    except (
        urllib.error.URLError,
        TimeoutError
    ) as error:
        raise RuntimeError(
            "Could not connect to local Ollama."
        ) from error


def suggest_relationships(memory_id, limit=5):
    """Find and classify possible memory relationships."""

    if (
        not isinstance(memory_id, int)
        or isinstance(memory_id, bool)
        or memory_id <= 0
    ):
        raise ValueError("Memory ID must be a positive integer.")

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or limit <= 0
    ):
        raise ValueError("Limit must be a positive integer.")

    candidates = semantic_search(
        get_memory_content(memory_id),
        limit=limit + 1
    )

    suggestions = []

    for candidate in candidates:

        if candidate["id"] == memory_id:
            continue

        classification = classify_relationship(
            get_memory_content(memory_id),
            candidate["content"]
        )

        if classification["relationship"] == "unrelated":
            continue

        suggestions.append({
            "source_memory_id": memory_id,
            "target_memory_id": candidate["id"],
            "source_content": get_memory_content(memory_id),
            "target_content": candidate["content"],
            **classification
        })

    return suggestions


def get_memory_content(memory_id):
    """Retrieve one active memory."""

    from cognitive.memory import get_all_memories

    for memory in get_all_memories(limit=10000):
        if memory["id"] == memory_id:
            return memory["content"]

    raise ValueError("Active memory not found.")

def approve_relationship(suggestion):
    """Save a reviewed relationship after explicit approval."""

    from cognitive.memory_relationships import add_relationship

    if not isinstance(suggestion, dict):
        raise ValueError("Suggestion must be a dictionary.")

    source_id = suggestion.get("source_memory_id")
    target_id = suggestion.get("target_memory_id")
    relationship = suggestion.get("relationship")
    confidence = suggestion.get("confidence")

    if relationship not in ALLOWED_RELATIONSHIPS:
        raise ValueError("Invalid relationship type.")

    if (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0 <= confidence <= 1
    ):
        raise ValueError("Invalid confidence.")

    if confidence < 0.60:
        raise ValueError("Suggestion confidence is too low.")

    return add_relationship(
        source_id,
        target_id,
        relationship,
        confidence
    )
