"""Critic / Self-Correction Agent: quality audit gate.

Rule-based (deterministic, works on mocks) + optional LLM suggestions.
LangGraph-ready signature: run(state) -> (patch, CriticVerdict).
"""
from __future__ import annotations

from typing import Any

from agents.specs_agent import is_valid_mermaid
from core.state import AgentState
from core.traceability import traceability_findings
from schemas.critic import CriticIssue, CriticVerdict


def _issue(area: str, severity: str, message: str) -> CriticIssue:
    return CriticIssue(area=area, severity=severity, message=message)


def audit(state: AgentState) -> CriticVerdict:
    issues: list[CriticIssue] = []
    missing: list[str] = []
    suggestions: list[str] = []

    refinement = dict(state.get("refinement", {}))
    dod = dict(state.get("dod", {}))
    specs = dict(state.get("specs", {}))

    if not refinement.get("refined_ticket"):
        missing.append("refinement.refined_ticket")
        issues.append(_issue("refinement", "high", "Missing refined ticket from Step 0"))

    contracts = dod.get("contracts", [])
    if not contracts:
        missing.append("dod.contracts")
        issues.append(_issue("dod", "high", "No output contracts defined"))
    if not dod.get("dod"):
        missing.append("dod.dod")
        issues.append(_issue("dod", "high", "Empty Definition of Done"))
    if not dod.get("milestones"):
        missing.append("dod.milestones")
        issues.append(_issue("dod", "medium", "No incremental milestones"))

    prd = specs.get("prd", {})
    trd = specs.get("trd", {})
    sec = specs.get("security", {})
    if not specs:
        missing.append("specs")
        issues.append(_issue("specs", "high", "Step 2 specs not generated"))
    else:
        if not prd.get("goal"):
            missing.append("specs.prd.goal")
            issues.append(_issue("prd", "high", "PRD goal is empty"))
        if not prd.get("requirements"):
            missing.append("specs.prd.requirements")
            issues.append(_issue("prd", "medium", "PRD has no requirements"))
        if not prd.get("acceptance_criteria"):
            suggestions.append("Add PRD acceptance criteria for verifiable sign-off")
        if not trd.get("components"):
            missing.append("specs.trd.components")
            issues.append(_issue("trd", "medium", "TRD has no components"))
        mermaid = str(trd.get("mermaid_flow", ""))
        if not is_valid_mermaid(mermaid):
            missing.append("specs.trd.mermaid_flow")
            issues.append(_issue("trd", "high", "Invalid or missing Mermaid flow diagram"))
        if not sec.get("owasp_checks"):
            missing.append("specs.security.owasp_checks")
            issues.append(_issue("security", "high", "Missing OWASP assessment"))
        if not sec.get("input_sanitization"):
            suggestions.append("Document input sanitization strategy")
        if not sec.get("auth_enforcement"):
            suggestions.append("Document auth enforcement strategy")

    for finding in traceability_findings(state, require_tdd=bool(state.get("tdd"))):
        missing.append(f"traceability: {finding}")
        issues.append(_issue("traceability", "high", finding))

    high = [i for i in issues if i.severity == "high"]
    approved = not high and not missing
    return CriticVerdict(approved=approved, issues=issues, missing=missing, suggestions=suggestions)


def run(state: AgentState, use_mock: bool = True) -> tuple[dict[str, Any], CriticVerdict]:
    _ = use_mock  # deterministic audit; LLM suggestions hook lands with real LLMs
    verdict = audit(state)
    return {"critic_verdict": verdict.model_dump()}, verdict
