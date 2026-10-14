"""Step 1: Job Done, Output Contracts & DoD (Secure-by-Default)."""
from __future__ import annotations

from typing import Any

from config.security_guardrails import DEFAULT_DOD_SECURITY_ITEMS
from core.llm_interface import generate_structured
from core.state import AgentState
from schemas.step1_dod import DoDOutput


def build_prompt(refinement: dict[str, Any]) -> str:
    return (
        "Define output contracts (JSON/DB/HTTP), Definition of Done, "
        f"and incremental milestones from refinement:\n{refinement}\n"
        "Include secure-by-default guardrails."
    )


def _ensure_security_items(output: DoDOutput) -> DoDOutput:
    existing = {d.criterion for d in output.dod}
    missing = [s for s in DEFAULT_DOD_SECURITY_ITEMS if s not in existing]
    if not missing:
        return output
    from schemas.step1_dod import DoDItem

    return DoDOutput(
        contracts=output.contracts,
        dod=[*output.dod, *[DoDItem(criterion=m, verifiable=True) for m in missing]],
        milestones=output.milestones,
    )


def run(state: AgentState, use_mock: bool = True) -> tuple[dict[str, Any], DoDOutput]:
    refinement = dict(state.get("refinement", {}))
    if not refinement:
        raise ValueError("refinement is required (run Step 0 first)")
    prompt = build_prompt(refinement)
    output = generate_structured(prompt, DoDOutput, use_mock=use_mock)
    output = _ensure_security_items(output)
    return {"dod": output.model_dump()}, output
