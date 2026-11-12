
from cognitive.self_model import (
    initialize_self_model,
    record_capability,
    get_capabilities,
    create_improvement_goal,
    get_improvement_goals,
    update_goal_status
)

print("\n=== MATE SELF-MODEL TEST ===")

# 1. Initialize
initialize_self_model()
print("\n[1] Self-model initialized.")

# 2. Record a capability
record_capability(
    name="Memory Retrieval",
    description="Ability to store and retrieve information.",
    score=80,
    evidence="Memory management tests passed."
)

print("\n[2] Capability recorded.")

# 3. Retrieve capabilities
capabilities = get_capabilities()

for item in capabilities:
    print(
        item["name"],
        "| Score:", item["score"],
        "| Evidence:", item["evidence"]
    )

# 4. Create an improvement goal
goal_id = create_improvement_goal(
    goal="Improve independent reasoning",
    reason="MATE needs stronger decision-making capabilities."
)

print("\n[3] Improvement goal created:", goal_id)

# 5. Update goal
updated = update_goal_status(goal_id, "in_progress")

print("[4] Goal status updated:", updated)

# 6. Retrieve goals
goals = get_improvement_goals()

for goal in goals:
    print(
        goal["goal"],
        "| Status:", goal["status"]
    )

print("\n=== TEST COMPLETED ===")
