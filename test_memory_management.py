
from cognitive.memory import (
    initialize_memory,
    add_memory,
    search_memories,
    update_memory,
    deactivate_memory
)

initialize_memory()

print("\n=== MATE MEMORY MANAGEMENT TEST ===")

# 1. Test duplicate prevention
memory_id = add_memory(
    "test",
    "MATE can evaluate its own performance.",
    source="test"
)

duplicate_id = add_memory(
    "test",
    "MATE can evaluate its own performance.",
    source="test"
)

print("Duplicate prevention:", memory_id == duplicate_id)

# 2. Test updating
updated = update_memory(
    memory_id,
    content="MATE can evaluate and improve its performance.",
    confidence=0.95
)

print("Memory update:", updated)

# 3. Verify updated content
results = search_memories("evaluate and improve")

print("Updated memory found:", len(results) > 0)

# 4. Test deactivation
deactivated = deactivate_memory(memory_id)

print("Memory deactivation:", deactivated)

# 5. Verify inactive memory is not returned
results = search_memories("evaluate and improve")

print("Inactive memory hidden:", len(results) == 0)

print("\n=== TEST COMPLETED ===")
