
from cognitive.learning import (
    initialize_learning,
    create_learning_plan,
    get_learning_plans,
    update_learning_status
)

print("\n=== MATE LEARNING ENGINE TEST ===")

# 1. Initialize
initialize_learning()
print("[1] Learning database initialized.")

# 2. Create improvement plan
plan_id = create_learning_plan(
    capability="Memory Retrieval",
    current_score=80,
    target_score=95,
    identified_weakness="Two memory retrieval tests failed.",
    learning_action="Improve keyword matching and test complex queries."
)

print("[2] Learning plan created:", plan_id)

# 3. Retrieve plans
plans = get_learning_plans()

print("\n[3] Learning plans:")

for plan in plans:
    print(
        "Capability:", plan["capability"],
        "| Current:", plan["current_score"],
        "| Target:", plan["target_score"],
        "| Status:", plan["status"]
    )

# 4. Approve plan for testing
updated = update_learning_status(plan_id, "approved")

print("\n[4] Plan approved:", updated)

print("\n=== TEST COMPLETED ===")
