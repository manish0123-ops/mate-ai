
from cognitive.memory import (
    initialize_memory,
    add_memory,
    search_memories,
    get_all_memories
)

print("\n=== MATE MEMORY TEST ===")

# 1. Initialize database
initialize_memory()
print("\n[1] Memory database initialized.")

# 2. Save test memories
memory_id = add_memory(
    category="project",
    content="MATE is my personal AI project. "
            "Its goal is to develop memory and self-reflection.",
    source="user"
)

add_memory(
    category="preference",
    content="I prefer keeping MATE's AI processing local.",
    source="user"
)

print("\n[2] Memories saved.")

# 3. Search memories
results = search_memories("MATE")

print("\n[3] Search results:")

for memory in results:
    print(f"ID: {memory['id']}")
    print(f"Category: {memory['category']}")
    print(f"Content: {memory['content']}")
    print("-" * 35)

# 4. Display all memories
all_memories = get_all_memories()

print("\n[4] Total active memories:", len(all_memories))

print("\n=== TEST COMPLETED ===")
