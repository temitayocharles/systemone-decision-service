from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()


def test_sidebar_is_collapsible_and_persistent():
    for token in (
        "sidebar-collapsed",
        "toggleSidebar()",
        "applySidebarState",
        'localStorage.setItem("so_sidebar_collapsed"',
        'localStorage.getItem("so_sidebar_collapsed")',
        'aria-expanded="true"',
    ):
        assert token in HTML


def test_collapsed_sidebar_keeps_navigation_accessible():
    assert ".app.sidebar-collapsed{grid-template-columns:72px 1fr}" in HTML
    assert "nav-icon" in HTML
    for label in ("Workspace", "Evidence", "Decisions", "Providers", "Provenance"):
        assert f'title="{label}"' in HTML


def test_camera_facing_microcopy_is_not_sub_9px():
    # The polished UI should not regress to 8px microtext in camera-facing surfaces.
    assert "font-size:8px" not in HTML
    # Core evidence/provider/activity supporting text should be at least 10px.
    for selector in (
        ".prov-node span{font-size:10px",
        ".prov-doc{",
        ".provider small{display:block;color:var(--muted);font-size:10px",
        ".event p{margin:2px 0 0;color:var(--muted);font-size:10px",
        ".compare table{width:100%;border-collapse:collapse;font-size:10px",
    ):
        assert selector in HTML
