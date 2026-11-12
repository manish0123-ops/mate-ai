
from cognitive.mate_core import mate

print("\n=== MATE SMART MEMORY TEST ===")

mate.initialize()

# Store a specific project memory
mate.remember(
    "project",
    "MATE is my personal AI project designed to develop persistent memory, self-reflection and independent reasoning."
)

mate.remember(
    "preference",
    "I prefer keeping MATE's AI processing local and private."
)

# Test semantic-style keyword retrieval
results = mate.recall(
    "What do you know about my MATE project?"
)

print("\n[1] Project search results:")

for item in results:
    print(
        "Category:", item["category"],
        "| Score:", item["relevance_score"],
        "| Content:", item["content"]
    )

# Test category retrieval
preferences = mate.recall_category("preference")

print("\n[2] Preference memories:", len(preferences))

# Test recent memories
recent = mate.recall_recent(5)

print("[3] Recent memories:", len(recent))

print("\n=== TEST COMPLETED ===")
