from pathlib import Path

from tools.html_exporter import build_template_context, render_markdown, render_report, write_docs


def _full_state():
    return {
        "ticket_text": "vague ticket",
        "repo_ref": "owner/repo",
        "branch": "main",
        "refinement": {
            "refined_ticket": "refined goal",
            "gaps": [{"area": "scope", "severity": "high", "description": "undef"}],
            "questions": [{"question": "which source?", "context": "scope"}],
            "assumptions": ["assume public"],
        },
        "dod": {
            "contracts": [
                {"kind": "json", "name": "resp", "schema_ref": "S", "status_codes": [200]}
            ],
            "dod": [{"criterion": "works", "verifiable": True}],
            "milestones": [{"order": 1, "title": "scaffold", "acceptance": "tests pass"}],
        },
        "specs": {
            "prd": {
                "goal": "deliver search",
                "background": "lost users",
                "users": ["trader"],
                "requirements": ["ranked"],
                "non_goals": [],
                "acceptance_criteria": ["top-5"],
            },
            "trd": {
                "components": ["api"],
                "api_endpoints": [{"method": "GET", "path": "/api/search", "description": "s"}],
                "data_model": ["Embedding"],
                "mermaid_flow": "flowchart TD\n    A-->B",
                "security_notes": ["note"],
            },
            "security": {
                "owasp_checks": [{"check": "A03", "status": "pass", "notes": "ok"}],
                "input_sanitization": "schemas",
                "auth_enforcement": "checks",
            },
        },
        "tdd": {
            "test_cases": [
                {
                    "name": "unit: x",
                    "kind": "unit",
                    "file": "tests/test_x.py",
                    "description": "d",
                    "covers": ["resp"],
                    "priority": "P0",
                }
            ],
            "implementation_steps": [
                {"order": 1, "title": "scaffold", "detail": "d", "tests": ["unit: x"], "files": []}
            ],
            "red_green_notes": "RED GREEN",
            "coverage_target": 80,
        },
        "critic_verdict": {"approved": True, "issues": [], "missing": [], "suggestions": []},
    }


def test_markdown_contains_all_sections():
    md = render_markdown(_full_state())
    for section in (
        "## 0. Refinement",
        "## 1. Output Contracts",
        "## 2. PRD",
        "## 2b. TRD",
        "## 2c. Security",
        "## 3. TDD Suite",
        "## Critic Gate",
        "```mermaid",
    ):
        assert section in md


def test_html_renders_title_and_goal():
    html = render_report(build_template_context(_full_state()))
    assert "deliver search" in html
    assert "APPROVED" in html


def test_html_uses_dev_journey_brand_system():
    html = render_report(build_template_context(_full_state()))
    assert "DEV JOURNEY" in html
    assert "FEATURE PLANNING COPILOT" in html
    assert "--dj-indigo: #3157d5" in html
    assert "Evidence-driven stakeholder report" in html


def test_html_uses_self_contained_png_brand_mark():
    html = render_report(build_template_context(_full_state()))
    assert 'src="data:image/png;base64,' in html
    assert ".svg" not in html
    assert "<svg" not in html


def test_write_docs_creates_files(tmp_path):
    paths = write_docs(_full_state(), out_dir=tmp_path / "docs")
    import pathlib

    assert pathlib.Path(paths["md"]).exists()
    assert pathlib.Path(paths["html"]).exists()
    assert "deliver search" in pathlib.Path(paths["md"]).read_text()


def test_write_docs_creates_presentation_when_requested(tmp_path):
    paths = write_docs(_full_state(), out_dir=tmp_path / "docs", include_presentation=True)

    assert Path(paths["presentation"]).exists()
    assert "case study" in Path(paths["presentation"]).read_text().lower()
