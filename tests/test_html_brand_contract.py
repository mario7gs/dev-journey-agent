from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTATION_HTML = (
    PROJECT_ROOT / "docs" / "BRAND_GUIDELINES.html",
    PROJECT_ROOT / "docs" / "MVP" / "FEATURE_SPEC.html",
    PROJECT_ROOT / "docs" / "MVP" / "GITHUB_AGENT_ROADMAP.html",
    PROJECT_ROOT / "docs" / "MVP" / "IMPLEMENTATION_DASHBOARD.html",
    PROJECT_ROOT / "docs" / "MVP" / "USER_JOURNEY.html",
)


def test_documentation_html_uses_the_frozen_navigation_contract() -> None:
    for path in DOCUMENTATION_HTML:
        html = path.read_text(encoding="utf-8")
        assert 'class="site-header"' in html, path
        assert 'class="site-nav"' in html, path
        assert "position: sticky" in html, path
        assert "DEV JOURNEY" in html, path
        assert "AGENT · FEATURE PLANNING COPILOT" in html, path

        nav_match = re.search(
            r'<nav class="site-nav".*?</nav>', html, flags=re.DOTALL
        )
        assert nav_match, path
        for anchor in re.findall(r'href="#([^"]+)"', nav_match.group(0)):
            assert re.search(rf'id="{re.escape(anchor)}"', html), (
                path,
                anchor,
            )
