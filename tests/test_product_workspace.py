from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
RUNBOOK = (ROOT / "docs" / "RUNBOOK.md").read_text()


def test_product_ui_runs_connected_evidence_to_decision_flow():
    for endpoint in (
        "/rag/v1/retrieve",
        "/rag/v1/query",
        "/v2/decide",
        "/v2/providers",
    ):
        assert endpoint in HTML


def test_product_ui_has_readable_live_pipeline_states():
    for label in ("Retrieve", "Answer", "Decide", "Record"):
        assert label in HTML
    for css_class in ("s1.active", "s2.active", "s3.active", "s4.active"):
        assert css_class in HTML
    assert "System One is working" in HTML
    assert "performance.now()" in HTML


def test_single_runbook_explains_stack_and_camera_flow():
    lower = RUNBOOK.lower()
    assert "single authoritative runbook" in lower
    assert "walk through the repository architecture first" in lower
    assert "knowledge provenance" in lower
    assert "connect the real downloads folder" in lower
    assert "demonstrate provider routing with the same evidence" in lower
    for cue in ("SAY", "SCREEN", "CLICK", "DO", "PAUSE", "EXPECT"):
        assert cue in RUNBOOK
