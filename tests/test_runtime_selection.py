from decide.selection import ModelStats, SelectionPolicy, choose_model
from rag.app.store import VectorStore


def test_empirical_selection_respects_constraints():
    candidates = [
        ModelStats(
            provider="jev",
            model="jev-a",
            task_type="routing",
            samples=100,
            accuracy=0.91,
            ece=0.03,
            p95_latency_ms=30,
            cost_per_1000=0.1,
        ),
        ModelStats(
            provider="other",
            model="other-a",
            task_type="routing",
            samples=100,
            accuracy=0.95,
            ece=0.09,
            p95_latency_ms=20,
            cost_per_1000=0.1,
        ),
    ]
    chosen = choose_model(
        candidates,
        SelectionPolicy(task_type="routing", max_ece=0.05),
    )
    assert chosen.provider == "jev"


def test_document_ids_are_deterministic_and_collection_scoped():
    first = VectorStore.document_id("engineering", "same text")
    second = VectorStore.document_id("engineering", "same text")
    other = VectorStore.document_id("business", "same text")
    assert first == second
    assert first != other
