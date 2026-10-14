"""Render a concise, portfolio-oriented case-study presentation."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.html_exporter import _brand_mark_png_data_uri


def _default_template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "case_study.html.j2"


def build_presentation_context(state: dict[str, Any]) -> dict[str, Any]:
    """Build a small, stable context for the presentation template."""
    specs = state.get("specs", {}) if isinstance(state.get("specs"), dict) else {}
    prd = specs.get("prd", {}) if isinstance(specs.get("prd"), dict) else {}
    refinement = state.get("refinement", {}) if isinstance(state.get("refinement"), dict) else {}
    dod = state.get("dod", {}) if isinstance(state.get("dod"), dict) else {}
    tdd = state.get("tdd", {}) if isinstance(state.get("tdd"), dict) else {}
    critic = state.get("critic_verdict", {}) if isinstance(state.get("critic_verdict"), dict) else {}
    requirements = prd.get("requirements", []) or []
    dod_items = dod.get("dod", []) or []
    milestones = sorted(dod.get("milestones", []) or [], key=lambda item: item.get("order", 0))
    test_cases = tdd.get("test_cases", []) or []
    status = state.get("status") or ("approved" if critic.get("approved") else "needs_input")
    return {
        "title": prd.get("goal") or refinement.get("refined_ticket", "Feature case study"),
        "ticket": state.get("ticket_text", ""),
        "repo_ref": state.get("repo_ref", ""),
        "branch": state.get("branch", "main"),
        "status": status,
        "mode": state.get("mode", "blocking"),
        "run_id": state.get("run_id", ""),
        "brand_mark_png_data_uri": _brand_mark_png_data_uri(),
        "refined_ticket": refinement.get("refined_ticket", ""),
        "requirements": requirements,
        "dod_items": dod_items,
        "milestones": milestones,
        "test_count": len(test_cases),
        "implementation_count": len(tdd.get("implementation_steps", []) or []),
        "coverage_target": tdd.get("coverage_target", 0),
        "approved": bool(critic.get("approved", False)),
        "block_reasons": state.get("block_reasons", []) or [],
    }


def render_presentation(
    state: dict[str, Any], template_path: str | Path | None = None
) -> str:
    """Render the presentation HTML using the shared brand mark."""
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    tpl = Path(template_path) if template_path else _default_template_path()
    if not tpl.exists():
        raise FileNotFoundError(f"Template not found: {tpl}")
    env = Environment(
        loader=FileSystemLoader(str(tpl.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env.get_template(tpl.name).render(**build_presentation_context(state))
