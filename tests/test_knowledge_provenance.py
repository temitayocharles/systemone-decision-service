from pathlib import Path

from rag.app.pipeline import RAGPipeline


class FakeStore:
    host = "chroma"
    port = 8000
    mode = "remote"

    def collection_count(self, name):
        return 3


class FakeEmbedding:
    provider = "ollama"
    model = "nomic-embed-text"


def test_provenance_reports_actual_collection_lineage(
    tmp_path: Path,
    monkeypatch,
):
    corpus = tmp_path / "engineering"
    corpus.mkdir()
    (corpus / "a.md").write_text(
        "# A\n\nAlpha runbook.",
        encoding="utf-8",
    )
    (corpus / "b.md").write_text(
        "# B\n\nBeta runbook.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "rag.app.pipeline.get_collection_dir",
        lambda name: corpus,
    )

    pipeline = object.__new__(RAGPipeline)
    pipeline.store = FakeStore()
    pipeline.embedding_client = FakeEmbedding()

    result = pipeline.provenance("engineering")

    assert result["collection"] == "engineering"
    assert result["document_count"] == 2
    assert result["expected_chunks"] == 2
    assert result["indexed_records"] == 3
    assert result["indexed"] is True
    assert result["embedding"]["model"] == "nomic-embed-text"
    assert {d["source"] for d in result["documents"]} == {
        "a.md",
        "b.md",
    }
