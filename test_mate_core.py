
from cognitive.mate_core import mate

print("\n=== MATE COGNITIVE CORE TEST ===")

# Initialize all components
result = mate.initialize()

print("\n[1] Core initialized:")
print(result)

# Test memory
memory_id = mate.remember(
    "project",
    "MATE has five connected cognitive components."
)

print("\n[2] Memory saved:", memory_id)

# Test recall
memories = mate.recall("five connected cognitive components")

print("[3] Memory retrieval:", len(memories), "result(s)")

# Test capability overview
capabilities = mate.get_capability_overview()

print("[4] Capabilities:", len(capabilities))

# Test reflection
reflection_id = mate.review_task(
    "Cognitive Core Test",
    "All five engines initialize.",
    "All five engines initialized.",
    "success",
    "The integration test ran successfully.",
    lesson="The cognitive components can be initialized together."
)

print("[5] Reflection recorded:", reflection_id)

# Test evaluation history
evaluations = mate.get_evaluation_history("Memory Retrieval")

print("[6] Evaluation history:", len(evaluations))

# Test learning plans
plans = mate.get_learning_overview()

print("[7] Learning plans:", len(plans))

print("\n=== CORE TEST COMPLETED ===")
