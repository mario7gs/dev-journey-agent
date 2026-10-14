"""Step 3: TDD suite & implementation roadmap (Red-Green).

LangGraph-ready signature: run(state) -> (patch, TDDOutput).
Deterministic guardrails ensure the suite is always usable by a junior
developer: at least one unit + one integration test, every contract
covered, ordered implementation steps, minimum 80% coverage target.
"""
from __future__ import annotations

from typing import Any

from core.llm_interface import generate_structured
from core.state import AgentState
from schemas.step3_tdd import ImplementationStep, TDDOutput, TestCase

MIN_COVERAGE = 80

RED_GREEN_DEFAULT = (
    "RED: write each test first and watch it fail. "
    "GREEN: implement the minimal code to pass. "
    "REFACTOR: clean up while keeping the suite green."
)


def _slug(text: str) -> str:
    keep = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")[:60] or "item"


def _synthetic_tests(dod: dict[str, Any]) -> list[TestCase]:
    cases: list[TestCase] = []
    for c in dod.get("contracts", [])[:10]:
        name = str(c.get("name", "contract"))
        kind = "integration" if str(c.get("kind", "json")) in ("json", "http") else "unit"
        cases.append(
            TestCase(
                name=f"{kind}: contract {name} responds per schema",
                kind=kind,
                file=f"tests/test_{_slug(name)}.py",
                description=f"Verify contract {name} ({c.get('schema_ref', 'schema')})",
                covers=[name],
                priority="P0",
            )
        )
    for m in dod.get("milestones", [])[:10]:
        title = str(m.get("title", "milestone"))
        cases.append(
            TestCase(
                name=f"unit: milestone '{title}' acceptance",
                kind="unit",
                file=f"tests/test_{_slug(title)}.py",
                description=str(m.get("acceptance", "acceptance"))[:500] or f"Accept {title}",
                covers=[title],
                priority="P1",
            )
        )
    return cases


def _ensure_test_mix(output: TDDOutput, dod: dict[str, Any]) -> TDDOutput:
    cases = list(output.test_cases)
    kinds = {c.kind for c in cases}
    if "unit" not in kinds or "integration" not in kinds:
        existing = {(c.name, c.kind) for c in cases}
        for synth in _synthetic_tests(dod):
            if (synth.name, synth.kind) not in existing:
                cases.append(synth)
    # Cover every contract by name
    covered = {ref for c in cases for ref in c.covers}
    for c in dod.get("contracts", []):
        name = str(c.get("name", ""))
        if name and name not in covered:
            cases.append(
                TestCase(
                    name=f"integration: contract {name} covered",
                    kind="integration",
                    file=f"tests/test_{_slug(name)}.py",
                    description=f"Cover contract {name}",
                    covers=[name],
                    priority="P0",
                )
            )
    return output.model_copy(update={"test_cases": cases})


def _ensure_steps(output: TDDOutput, dod: dict[str, Any]) -> TDDOutput:
    steps = list(output.implementation_steps)
    if not steps:
        names = [c.name for c in output.test_cases[:12]]
        milestones = dod.get("milestones", [])
        if milestones:
            for i, m in enumerate(milestones[:8]):
                title = str(m.get("title", f"step {i + 1}"))
                steps.append(
                    ImplementationStep(
                        order=i + 1,
                        title=f"Implement: {title}"[:300],
                        detail=str(m.get("acceptance", ""))[:1000],
                        tests=[n for n in names if _slug(title)[:20] in _slug(n)][:3],
                        files=[],
                    )
                )
        else:
            steps.append(
                ImplementationStep(
                    order=1,
                    title="Scaffold then implement to green tests",
                    detail=RED_GREEN_DEFAULT,
                    tests=names[:5],
                    files=[],
                )
            )
    ordered = [s.model_copy(update={"order": i + 1}) for i, s in enumerate(sorted(steps, key=lambda s: s.order))]
    notes = output.red_green_notes or RED_GREEN_DEFAULT
    target = max(output.coverage_target, MIN_COVERAGE)
    return output.model_copy(
        update={"implementation_steps": ordered, "red_green_notes": notes, "coverage_target": target}
    )


def build_prompt(refinement: dict[str, Any], dod: dict[str, Any], specs: dict[str, Any]) -> str:
    goal = specs.get("prd", {}).get("goal", "")
    reqs = specs.get("prd", {}).get("requirements", [])
    return (
        "Generate a TDD suite (unit + integration, e2e where justified) and an "
        "ordered junior-friendly implementation roadmap.\n"
        f"Goal: {goal}\nRequirements: {reqs}\nDoD: {dod}\nRefinement: {refinement}\n"
        "Rules: every test has kind/file/description/covers; every contract covered; "
        "steps ordered with mapped tests; coverage_target >= 80; include red-green notes."
    )


def run(state: AgentState, use_mock: bool = True) -> tuple[dict[str, Any], TDDOutput]:
    refinement = dict(state.get("refinement", {}))
    dod = dict(state.get("dod", {}))
    specs = dict(state.get("specs", {}))
    if not dod:
        raise ValueError("dod is required (run Steps 0-1 first)")
    if not specs:
        raise ValueError("specs is required (run Step 2 first)")
    prompt = build_prompt(refinement, dod, specs)
    output = generate_structured(prompt, TDDOutput, use_mock=use_mock)
    output = _ensure_test_mix(output, dod)
    output = _ensure_steps(output, dod)
    if not output.test_cases:
        raise ValueError("tdd_agent produced no test cases even after guardrails")
    return {"tdd": output.model_dump()}, output
