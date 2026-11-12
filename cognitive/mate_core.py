
from cognitive.memory import (
    initialize_memory,
    add_memory,
    search_memories,
    get_all_memories,
    get_memories_by_category
)
from cognitive.semantic_search import semantic_search

from cognitive.self_model import (
    initialize_self_model,
    get_capabilities,
    get_improvement_goals
)

from cognitive.reflection import (
    initialize_reflection,
    record_reflection,
    get_reflections
)

from cognitive.evaluator import (
    initialize_evaluator,
    record_evaluation,
    get_evaluations
)

from cognitive.learning import (
    initialize_learning,
    create_learning_plan,
    get_learning_plans
)


class MATECore:
    """Central coordinator for MATE's cognitive components."""

    def initialize(self):
        initialize_memory()
        initialize_self_model()
        initialize_reflection()
        initialize_evaluator()
        initialize_learning()

        return {
            "status": "initialized",
            "components": [
                "Memory",
                "Self-Model",
                "Reflection",
                "Evaluation",
                "Learning"
            ]
        }

    def remember(self, category, content, source="user"):
        return add_memory(category, content, source)

    def recall(self, keyword):
        return semantic_search(keyword)
        
    def recall_category(self, category):
        return get_memories_by_category(category)

    def recall_recent(self, limit=10):
        return get_all_memories(limit)

    def get_memory_overview(self):
        return get_all_memories()

    def get_capability_overview(self):
        return get_capabilities()

    def get_goals(self):
        return get_improvement_goals()

    def review_task(
        self,
        task_name,
        expected_outcome,
        actual_outcome,
        result_status,
        evidence,
        identified_issue="",
        lesson="",
        improvement_suggestion=""
    ):
        return record_reflection(
            task_name,
            expected_outcome,
            actual_outcome,
            result_status,
            evidence,
            identified_issue,
            lesson,
            improvement_suggestion
        )

    def evaluate(
        self,
        capability,
        total_tests,
        passed_tests,
        evidence
    ):
        return record_evaluation(
            capability,
            total_tests,
            passed_tests,
            evidence
        )

    def get_evaluation_history(self, capability=None):
        return get_evaluations(capability)

    def propose_improvement(
        self,
        capability,
        current_score,
        target_score,
        weakness,
        action
    ):
        return create_learning_plan(
            capability,
            current_score,
            target_score,
            weakness,
            action
        )

    def get_learning_overview(self):
        return get_learning_plans()


mate = MATECore()


if __name__ == "__main__":
    result = mate.initialize()
    print("MATE Cognitive Core")
    print(result)
