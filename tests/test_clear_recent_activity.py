from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()


def test_recent_activity_can_be_cleared_locally():
    assert "Clear activity" in HTML
    assert 'function clearActivity(){localStorage.removeItem("so_activity")' in HTML
    assert "Recent activity cleared from this browser session." in HTML


def test_clear_activity_does_not_call_runtime_or_rag():
    start = HTML.index("function clearActivity()")
    end = HTML.index("function resetQueryProvenance", start)
    block = HTML[start:end]
    assert "fetch(" not in block
    assert "/v2/" not in block
    assert "/rag/" not in block


def test_recent_activity_labels_scope_explicitly():
    assert "Browser session only · runtime telemetry is unaffected" in HTML
    assert 'if(btn)btn.disabled=!rows.length' in HTML
