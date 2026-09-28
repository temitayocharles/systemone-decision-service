import pytest

from decide.selection import BenchmarkStore, ModelStats


def test_benchmark_store_requires_provenance(tmp_path):
    store = BenchmarkStore(str(tmp_path / "benchmarks.json"))
    with pytest.raises(ValueError):
        store.upsert(
            ModelStats(
                provider="p",
                model="m",
                task_type="routing",
                samples=10,
            )
        )


def test_benchmark_store_accepts_provenance(tmp_path):
    store = BenchmarkStore(str(tmp_path / "benchmarks.json"))
    stat = ModelStats(
        provider="p",
        model="m",
        task_type="routing",
        samples=10,
        run_id="run-1",
        dataset_sha256="a" * 64,
        created_at="2026-09-28T00:00:00+00:00",
    )
    store.upsert(stat)
    assert store.load()[0].run_id == "run-1"
