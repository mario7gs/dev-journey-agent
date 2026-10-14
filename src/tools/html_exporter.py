"""Step 4: Export & Stakeholder Delivery.

Markdown and HTML rendering stay deterministic and dependency-light. Optional
portfolio exports add a browser-rendered PDF and a concise case-study deck.
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from core.state import AgentState


def _default_template_path() -> Path:
    """Locate the bundled template in both a checkout and an installed wheel."""
    return Path(__file__).resolve().parents[1] / "templates" / "spec_report.html.j2"


def _brand_mark_png_data_uri() -> str:
    """Return the approved PNG mark as a self-contained HTML image source."""
    asset = _default_template_path().parent / "assets" / "dj-mark.png"
    encoded = base64.b64encode(asset.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _get(section: dict[str, Any], key: str, default: Any = None) -> Any:
    return section.get(key, default) if isinstance(section, dict) else default


def _text(item: Any, key: str = "text") -> str:
    if isinstance(item, dict):
        return str(item.get(key, ""))
    return str(item)


def _refs(item: Any, key: str) -> str:
    if not isinstance(item, dict):
        return ""
    return ", ".join(str(value) for value in item.get(key, []) or [])


def render_markdown(state: AgentState | dict[str, Any]) -> str:
    """Render docs/FEATURE_SPEC.md from full pipeline state."""
    s = dict(state)
    refinement = _get(s, "refinement", {})
    dod = _get(s, "dod", {})
    specs = _get(s, "specs", {})
    tdd = _get(s, "tdd", {})
    critic = _get(s, "critic_verdict", {})
    prd = _get(specs, "prd", {})
    trd = _get(specs, "trd", {})
    sec = _get(specs, "security", {})
    lines: list[str] = []

    goal = _get(prd, "goal", "") or _get(refinement, "refined_ticket", "") or "Feature Spec"
    lines.append(f"# {goal}")
    lines.append("")
    lines.append(f"_Repo: `{s.get('repo_ref', '')}` · branch `{s.get('branch', 'main')}`_")
    lines.append("")
    status = s.get("status") or ("approved" if critic.get("approved") else "needs_input")
    lines.append(f"**Run status:** `{status}` · **Mode:** `{s.get('mode', 'blocking')}`")
    if s.get("run_id"):
        lines.append(f"**Run ID:** `{s['run_id']}`")
    if s.get("block_reasons"):
        lines.append("")
        lines.append("### Blocking reasons")
        for reason in s["block_reasons"]:
            lines.append(f"- {reason}")
    if s.get("errors"):
        lines.append("")
        lines.append("### Pipeline errors")
        for error in s["errors"]:
            lines.append(f"- {error}")
    lines.append("")

    lines.append("## 0. Refinement")
    lines.append("")
    lines.append(str(_get(refinement, "refined_ticket", "")))
    lines.append("")
    gaps = _get(refinement, "gaps", []) or []
    if gaps:
        lines.append("### Gaps")
        for g in gaps:
            lines.append(f"- **{g.get('area', '')}** [{g.get('severity', '')}]: {g.get('description', '')}")
        lines.append("")
    questions = _get(refinement, "questions", []) or []
    if questions:
        lines.append("### Clarifying questions")
        for q in questions:
            lines.append(f"- {q.get('question', '')} ({q.get('context', '')})")
        lines.append("")
    assumptions = _get(refinement, "assumptions", []) or []
    if assumptions:
        lines.append("### Assumptions")
        for a in assumptions:
            lines.append(f"- {a}")
        lines.append("")

    lines.append("## 1. Output Contracts & Definition of Done")
    lines.append("")
    lines.append("| ID | Kind | Name | Schema | Requirements | Status codes |")
    lines.append("|---|---|---|---|---|---|")
    for c in _get(dod, "contracts", []) or []:
        codes = ", ".join(str(x) for x in c.get("status_codes", []))
        lines.append(
            f"| {c.get('id', '')} | {c.get('kind', '')} | {c.get('name', '')} | "
            f"{c.get('schema_ref', '')} | {_refs(c, 'requirement_ids')} | {codes} |"
        )
    lines.append("")
    lines.append("### DoD")
    for d in _get(dod, "dod", []) or []:
        mark = "✓" if d.get("verifiable") else "○"
        refs = _refs(d, "requirement_ids")
        suffix = f" _(requirements: {refs})_" if refs else ""
        lines.append(f"- [{mark}] `{d.get('id', '')}` {d.get('criterion', '')}{suffix}")
    lines.append("")
    lines.append("### Milestones")
    for m in sorted(_get(dod, "milestones", []) or [], key=lambda m: m.get("order", 0)):
        refs = _refs(m, "requirement_ids")
        suffix = f" _(requirements: {refs})_" if refs else ""
        lines.append(
            f"{m.get('order', '')}. `{m.get('id', '')}` **{m.get('title', '')}** — "
            f"{m.get('acceptance', '')}{suffix}"
        )
    lines.append("")

    lines.append("## 2. PRD")
    lines.append("")
    for key in ("background",):
        if _get(prd, key):
            lines.append(f"_{_get(prd, key)}_")
            lines.append("")
    requirements = _get(prd, "requirements", []) or []
    if requirements:
        lines.append("### Requirements")
        for requirement in requirements:
            priority = f" [{requirement.get('priority')}]" if isinstance(requirement, dict) else ""
            lines.append(f"- `{requirement.get('id', '') if isinstance(requirement, dict) else ''}`{priority} {_text(requirement)}")
        lines.append("")
    non_goals = _get(prd, "non_goals", []) or []
    if non_goals:
        lines.append("### Non-goals")
        for item in non_goals:
            lines.append(f"- {_text(item)}")
        lines.append("")
    acceptance = _get(prd, "acceptance_criteria", []) or []
    if acceptance:
        lines.append("### Acceptance criteria")
        for criterion in acceptance:
            refs = _refs(criterion, "requirement_ids")
            suffix = f" _(requirements: {refs})_" if refs else ""
            lines.append(f"- `{criterion.get('id', '') if isinstance(criterion, dict) else ''}` {_text(criterion)}{suffix}")
        lines.append("")
    users = _get(prd, "users", []) or []
    if users:
        lines.append(f"**Users:** {', '.join(str(u) for u in users)}")
        lines.append("")

    lines.append("## 2b. TRD")
    lines.append("")
    comps = _get(trd, "components", []) or []
    if comps:
        lines.append("### Components")
        for c in comps:
            lines.append(f"- {c}")
        lines.append("")
    eps = _get(trd, "api_endpoints", []) or []
    if eps:
        lines.append("| Method | Path | Description |")
        lines.append("|---|---|---|")
        for e in eps:
            lines.append(f"| {e.get('method', '')} | `{e.get('path', '')}` | {e.get('description', '')} |")
        lines.append("")
    dm = _get(trd, "data_model", []) or []
    if dm:
        lines.append("### Data model")
        for d in dm:
            lines.append(f"- {d}")
        lines.append("")
    mermaid = _get(trd, "mermaid_flow", "") or ""
    if mermaid:
        lines.append("### Flow")
        lines.append("```mermaid")
        lines.append(mermaid)
        lines.append("```")
        lines.append("")

    lines.append("## 2c. Security Assessment")
    lines.append("")
    checks = _get(sec, "owasp_checks", []) or []
    if checks:
        lines.append("| ID | Check | Status | Notes |")
        lines.append("|---|---|---|---|")
        for c in checks:
            lines.append(
                f"| {c.get('id', '')} | {c.get('check', '')} | {c.get('status', '')} | {c.get('notes', '')} |"
            )
        lines.append("")
    if _get(sec, "input_sanitization"):
        lines.append(f"**Input sanitization:** {_get(sec, 'input_sanitization')}")
        lines.append("")
    if _get(sec, "auth_enforcement"):
        lines.append(f"**Auth enforcement:** {_get(sec, 'auth_enforcement')}")
        lines.append("")
    for n in _get(trd, "security_notes", []) or []:
        lines.append(f"- {n}")
    lines.append("")

    lines.append("## 3. TDD Suite & Roadmap")
    lines.append("")
    cases = _get(tdd, "test_cases", []) or []
    if cases:
        lines.append("| ID | Test | Kind | File | Requirements | Contracts | Priority |")
        lines.append("|---|---|---|---|---|---|---|")
        for t in cases:
            lines.append(
                f"| {t.get('id', '')} | {t.get('name', '')} | {t.get('kind', '')} | `{t.get('file', '')}` | "
                f"{_refs(t, 'requirement_ids')} | {_refs(t, 'contract_ids')} | {t.get('priority', '')} |"
            )
        lines.append("")
    for st in sorted(_get(tdd, "implementation_steps", []) or [], key=lambda x: x.get("order", 0)):
        tests = ", ".join(f"`{t}`" for t in st.get("tests", []))
        lines.append(f"{st.get('order', '')}. `{st.get('id', '')}` **{st.get('title', '')}**")
        if st.get("detail"):
            lines.append(f"   {st.get('detail', '')}")
        if tests:
            lines.append(f"   Tests: {tests}")
        if st.get("test_ids"):
            lines.append(f"   Test IDs: {_refs(st, 'test_ids')}")
    lines.append("")
    if _get(tdd, "red_green_notes"):
        lines.append(f"_RED/GREEN: {_get(tdd, 'red_green_notes')}_")
        lines.append("")
    if _get(tdd, "coverage_target") is not None:
        lines.append(f"**Coverage target:** ≥{_get(tdd, 'coverage_target')}%")
        lines.append("")

    lines.append("## Critic Gate")
    lines.append("")
    lines.append(f"Approved: **{critic.get('approved', False)}**")
    if critic.get("missing"):
        lines.append(f"Missing: {', '.join(str(m) for m in critic['missing'])}")
    for i in critic.get("issues", []) or []:
        lines.append(f"- [{i.get('severity', '')}] {i.get('area', '')}: {i.get('message', '')}")
    for g in critic.get("suggestions", []) or []:
        lines.append(f"- Suggestion: {g}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_template_context(state: dict[str, Any]) -> dict[str, Any]:
    s = dict(state)
    specs = s.get("specs", {}) if isinstance(s.get("specs"), dict) else {}
    prd = specs.get("prd", {}) if isinstance(specs.get("prd"), dict) else {}
    refinement = s.get("refinement", {}) if isinstance(s.get("refinement"), dict) else {}
    critic = s.get("critic_verdict", {}) if isinstance(s.get("critic_verdict"), dict) else {}
    status = s.get("status") or ("approved" if critic.get("approved") else "needs_input")
    return {
        "title": prd.get("goal") or refinement.get("refined_ticket", "Feature Spec"),
        "ticket": s.get("ticket_text", ""),
        "repo_ref": s.get("repo_ref", ""),
        "branch": s.get("branch", "main"),
        "status": status,
        "mode": s.get("mode", "blocking"),
        "run_id": s.get("run_id", ""),
        "block_reasons": s.get("block_reasons", []),
        "errors": s.get("errors", []),
        "brand_mark_png_data_uri": _brand_mark_png_data_uri(),
        "refinement": refinement,
        "dod": s.get("dod", {}),
        "prd": prd,
        "trd": specs.get("trd", {}),
        "security": specs.get("security", {}),
        "tdd": s.get("tdd", {}),
        "critic": critic,
    }


def render_report(context: dict[str, Any], template_path: str | Path | None = None) -> str:
    """Render stakeholder HTML via Jinja2. Raises FileNotFoundError if template missing."""
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    tpl = Path(template_path) if template_path else _default_template_path()
    if not tpl.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    env = Environment(
        loader=FileSystemLoader(str(tpl.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env.get_template(tpl.name).render(**context)


def write_docs(
    state: dict[str, Any],
    out_dir: str | Path = "docs",
    template_path: str | Path | None = None,
    *,
    include_pdf: bool = False,
    include_presentation: bool = False,
) -> dict[str, str]:
    """Write the requested documentation surfaces and return their paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    md = render_markdown(state)
    html = render_report(build_template_context(state), template_path)
    md_path = out / "FEATURE_SPEC.md"
    html_path = out / "FEATURE_SPEC.html"
    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    paths = {"md": str(md_path), "html": str(html_path)}
    if include_pdf:
        from tools.pdf_exporter import PDFExportError, render_pdf

        pdf_path = out / "FEATURE_SPEC.pdf"
        try:
            render_pdf(html_path, pdf_path)
            paths["pdf"] = str(pdf_path)
        except PDFExportError as exc:
            paths["pdf_error"] = str(exc)
    if include_presentation:
        from tools.presentation_exporter import render_presentation

        presentation_path = out / "FEATURE_CASE_STUDY.html"
        presentation_html = render_presentation(state)
        presentation_path.write_text(presentation_html, encoding="utf-8")
        paths["presentation"] = str(presentation_path)
        if include_pdf:
            from tools.pdf_exporter import PDFExportError, render_pdf

            presentation_pdf_path = out / "FEATURE_CASE_STUDY.pdf"
            try:
                render_pdf(presentation_path, presentation_pdf_path)
                paths["presentation_pdf"] = str(presentation_pdf_path)
            except PDFExportError as exc:
                paths["presentation_pdf_error"] = str(exc)
    return paths
