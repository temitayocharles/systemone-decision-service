from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
MAIN = (ROOT / "rag" / "app" / "main.py").read_text()
PIPELINE = (ROOT / "rag" / "app" / "pipeline.py").read_text()


def test_rag_exposes_read_only_collection_provenance():
    assert '@app.get("/v1/provenance/{collection}")' in MAIN
    for key in (
        '"documents"',
        '"document_count"',
        '"expected_chunks"',
        '"indexed_records"',
        '"embedding"',
        '"vector_store"',
        '"stages"',
    ):
        assert key in PIPELINE


def test_ui_renders_observable_knowledge_lineage():
    assert "/rag/v1/provenance/" in HTML
    for label in (
        "Source documents",
        "Chunk",
        "Embed",
        "Chroma",
        "Retrieved",
        "Grounded answer",
        "Decision",
    ):
        assert label in HTML
    assert "observable knowledge lineage" in HTML
    assert "does not claim visibility into model-internal reasoning" in HTML


def test_live_query_extends_provenance_graph():
    assert 'document.getElementById("pvRetrieved")' in HTML
    assert 'document.getElementById("pvAnswer")' in HTML
    assert 'document.getElementById("pvDecision")' in HTML
