from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
SERVER = (ROOT / "demo" / "ui" / "serve_demo.py").read_text()


def test_grounded_answer_precedes_sources_in_knowledge_response():
    panel = HTML.index('id="evidencePanel"')
    answer = HTML.index('id="answerBlock"', panel)
    sources = HTML.index("Sources used", panel)
    assert answer < sources


def test_sidebar_controls_are_real_navigation():
    for target in ("workspace", "evidencePanel", "decisionPanel", "providersPanel", "provenance"):
        assert f"navigateTo('{target}'" in HTML


def test_indexing_has_visible_busy_and_success_states():
    assert "setIndexButton" in HTML
    assert "Indexing Downloads" in HTML
    assert "✓ " in HTML
    assert "/local/downloads/index/status" in HTML


def test_downloads_indexing_is_background_work():
    assert "threading.Thread" in SERVER
    assert "/local/downloads/index/status" in SERVER
    assert 'state="indexing"' in SERVER
    assert "timeout=1800" in SERVER
    assert "BrokenPipeError" in SERVER
