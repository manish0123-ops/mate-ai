
from cognitive.evaluator import (
    initialize_evaluator,
    record_evaluation,
    get_evaluations,
    get_average_accuracy
)

print("\n=== MATE EVALUATION ENGINE TEST ===")

initialize_evaluator()
print("[1] Evaluation database initialized.")

evaluation_id = record_evaluation(
    capability="Memory Retrieval",
    total_tests=10,
    passed_tests=8,
    evidence="8 out of 10 predefined memory retrieval tests passed."
)

print("[2] Evaluation recorded:", evaluation_id)

results = get_evaluations("Memory Retrieval")

print("\n[3] Evaluation results:")

for item in results:
    print(
        "Capability:", item["capability"],
        "| Accuracy:", round(item["accuracy"], 2), "%",
        "| Passed:", item["passed_tests"],
        "/", item["total_tests"]
    )

average = get_average_accuracy("Memory Retrieval")

print("\n[4] Average accuracy:", round(average, 2), "%")

print("\n=== TEST COMPLETED ===")
