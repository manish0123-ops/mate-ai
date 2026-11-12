
from cognitive.reflection import (
    initialize_reflection,
    record_reflection,
    get_reflections,
    get_reflections_by_status,
    mark_reflection_reviewed
)

print("\n=== MATE REFLECTION ENGINE TEST ===")

initialize_reflection()
print("[1] Reflection database initialized.")

reflection_id = record_reflection(
    task_name="Memory Retrieval",
    expected_outcome="Retrieve the correct saved memory.",
    actual_outcome="The correct memory was retrieved.",
    result_status="success",
    evidence="Memory management test completed successfully.",
    identified_issue="No issue identified.",
    lesson="Memory retrieval is functioning correctly.",
    improvement_suggestion="Test retrieval with more complex queries."
)

print("[2] Reflection recorded:", reflection_id)

reflections = get_reflections()

print("\n[3] Stored reflections:")

for item in reflections:
    print(
        "Task:", item["task_name"],
        "| Result:", item["result_status"],
        "| Lesson:", item["lesson"]
    )

successful = get_reflections_by_status("success")
print("\n[4] Successful reflections:", len(successful))

reviewed = mark_reflection_reviewed(reflection_id)
print("[5] Reflection marked reviewed:", reviewed)

print("\n=== TEST COMPLETED ===")
