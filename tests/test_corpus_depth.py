from collections import Counter
from pathlib import Path

from rag.app.chunker import chunk_directory_records


ROOT = Path(__file__).resolve().parents[1]


def _distribution(collection: str):
    records = chunk_directory_records(ROOT / "corpora" / collection)
    counts = Counter(record["source"] for record in records)
    return records, counts


def test_engineering_corpus_has_real_multi_chunk_distribution():
    records, counts = _distribution("engineering")
    assert len(counts) >= 8
    assert len(records) >= 20
    assert max(counts.values()) >= 5
    assert len(set(counts.values())) >= 3


def test_business_corpus_has_real_multi_chunk_distribution():
    records, counts = _distribution("business")
    assert len(counts) >= 8
    assert len(records) >= 20
    assert max(counts.values()) >= 5
    assert len(set(counts.values())) >= 3
