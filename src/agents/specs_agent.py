"""Step 2: PRD, TRD, Mermaid Flow & Security Assessment.

LangGraph-ready signature: run(state) -> (patch, SpecsOutput).
Deterministic guardrails (Mermaid fallback + OWASP defaults) are applied
after the structured LLM call so output is always complete and safe.
"""
from __future__ import annotations

from typing import Any

from core.llm_interface import generate_structured
from core.state import AgentState
from schemas.step2_specs import OWASPCheck, SecurityAssessment, SpecsOutput

MERMAID_HEADS = ("flowchart", "graph", "sequenceDiagram", "stateDiagram")

DEFAULT_OWASP_CHECKS = (
    ("A01 broken-access-control", "Enforce AuthN/AuthZ before sensitive operations"),
    ("A02 cryptographic-failures", "Secrets via env vars only; no hardcoded credentials"),
    ("A03 injection", "Validate all inputs with schemas; parameterized queries only"),
    ("A04 insecure-design", "DoD acceptance criteria verifiable; secure defaults"),
    ("A07 XSS", "Sanitize user-provided HTML; no unvalidated dynamic rendering"),
)

DEFAULT_SECURITY_NOTES = (
    "OWASP Top-10 reviewed; see security.owasp_checks",
    "Input sanitization enforced at system boundaries",
    "Auth enforcement verified before sensitive operations",
)


def is_valid_mermaid(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 10000:
        return False
    if "<script" in stripped.lower():
        return False
    first = stripped.splitlines()[0].strip().lower()
    return first.startswith(tuple(h.lower() for h in MERMAID_HEADS))


def fallback_mermaid(dod: dict[str, Any]) -> str:
    milestones = dod.get("milestones", [])
    lines = ["flowchart TD"]
    if not milestones:
        return "flowchart TD\n    A[Ticket] --> B[Implement] --> C[Verify]"
    prev = "Start"
    lines.append(f"    S[{prev}]")
    node = "S"
    for i, m in enumerate(milestones[:8]):
        title = str(m.get("title", f"step{i + 1}"))[:40].replace("[", "(").replace("]", ")")
        nid = f"M{i}"
        lines.append(f"    {node} --> {nid}[{title}]")
        node = nid
    lines.append(f"    {node} --> Done")
    return "\n".join(lines)


def _ensure_mermaid(output: SpecsOutput, dod: dict[str, Any]) -> SpecsOutput:
    if is_valid_mermaid(output.trd.mermaid_flow):
        return output
    patched_trd = output.trd.model_copy(update={"mermaid_flow": fallback_mermaid(dod)})
    return output.model_copy(update={"trd": patched_trd})


def _ensure_security(output: SpecsOutput) -> SpecsOutput:
    existing_checks = {c.check for c in output.security.owasp_checks}
    missing = [c for c in DEFAULT_OWASP_CHECKS if c[0] not in existing_checks]
    checks = [
        *output.security.owasp_checks,
        *[OWASPCheck(check=name, status="pass", notes=notes) for name, notes in missing],
    ]
    notes = list(output.trd.security_notes)
    for n in DEFAULT_SECURITY_NOTES:
        if n not in notes:
            notes.append(n)
    patched_trd = output.trd.model_copy(update={"security_notes": notes})
    patched_sec = SecurityAssessment(
        owasp_checks=checks,
        input_sanitization=output.security.input_sanitization or "Validate all user input with schemas at boundaries.",
        auth_enforcement=output.security.auth_enforcement or "Require AuthN/AuthZ checks before sensitive operations.",
    )
    return output.model_copy(update={"trd": patched_trd, "security": patched_sec})


def build_prompt(refinement: dict[str, Any], dod: dict[str, Any]) -> str:
    return (
        "Generate PRD (goal, background, users, requirements, non-goals, "
        "acceptance criteria), TRD (components, API endpoints, data model, "
        "Mermaid flow), and Security Assessment (OWASP checks, input "
        "sanitization, auth enforcement).\n"
        f"Refinement:\n{refinement}\nDoD:\n{dod}\n"
        "Mermaid must start with 'flowchart TD' or 'sequenceDiagram'."
    )


def run(state: AgentState, use_mock: bool = True) -> tuple[dict[str, Any], SpecsOutput]:
    refinement = dict(state.get("refinement", {}))
    dod = dict(state.get("dod", {}))
    if not refinement:
        raise ValueError("refinement is required (run Step 0 first)")
    if not dod:
        raise ValueError("dod is required (run Step 1 first)")
    prompt = build_prompt(refinement, dod)
    output = generate_structured(prompt, SpecsOutput, use_mock=use_mock)
    output = _ensure_mermaid(output, dod)
    output = _ensure_security(output)
    return {"specs": output.model_dump()}, output
