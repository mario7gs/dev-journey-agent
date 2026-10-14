"""Deterministic IDs and cross-stage references for generated planning artifacts."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.state import AgentState
from schemas.step1_dod import DoDOutput
from schemas.step2_specs import SpecsOutput
from schemas.step3_tdd import TDDOutput


def _stable_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index:03d}"


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _valid_refs(values: Iterable[str], allowed: set[str]) -> list[str]:
    return _unique(value for value in values if value in allowed)


def apply_traceability(state: AgentState | dict[str, Any]) -> dict[str, Any]:
    """Return a state patch with deterministic IDs and conservative links.

    Existing free-text fields remain intact for backwards-compatible exports.
    References are inferred only when the relationship is unambiguous, such as
    a single requirement or a test explicitly naming a contract.
    """
    source = dict(state)
    patch: dict[str, Any] = {}

    dod_model = DoDOutput.model_validate(source["dod"]) if source.get("dod") else None
    if dod_model is not None:
        contracts = [
            item.model_copy(update={"id": _stable_id("CON", i)})
            for i, item in enumerate(dod_model.contracts, start=1)
        ]
        dod_items = [
            item.model_copy(update={"id": _stable_id("DOD", i)})
            for i, item in enumerate(dod_model.dod, start=1)
        ]
        milestones = [
            item.model_copy(update={"id": _stable_id("MILE", i)})
            for i, item in enumerate(dod_model.milestones, start=1)
        ]
        dod_model = DoDOutput(contracts=contracts, dod=dod_items, milestones=milestones)

    specs_model = SpecsOutput.model_validate(source["specs"]) if source.get("specs") else None
    if specs_model is not None:
        requirements = [
            item.model_copy(update={"id": _stable_id("REQ", i)})
            for i, item in enumerate(specs_model.prd.requirements, start=1)
        ]
        requirement_ids = {item.id for item in requirements}
        acceptance = []
        for i, item in enumerate(specs_model.prd.acceptance_criteria, start=1):
            refs = _valid_refs(item.requirement_ids, requirement_ids)
            if not refs and len(requirements) == 1:
                refs = [requirements[0].id]
            acceptance.append(
                item.model_copy(update={"id": _stable_id("ACC", i), "requirement_ids": refs})
            )
        prd = specs_model.prd.model_copy(
            update={"requirements": requirements, "acceptance_criteria": acceptance}
        )
        security_checks = [
            item.model_copy(update={"id": _stable_id("SEC", i)})
            for i, item in enumerate(specs_model.security.owasp_checks, start=1)
        ]
        security = specs_model.security.model_copy(update={"owasp_checks": security_checks})
        specs_model = specs_model.model_copy(update={"prd": prd, "security": security})

        if dod_model is not None:
            contracts = []
            for item in dod_model.contracts:
                refs = _valid_refs(item.requirement_ids, requirement_ids)
                if not refs and len(requirements) == 1:
                    refs = [requirements[0].id]
                contracts.append(item.model_copy(update={"requirement_ids": refs}))
            milestones = []
            for item in dod_model.milestones:
                refs = _valid_refs(item.requirement_ids, requirement_ids)
                if not refs and len(requirements) == 1:
                    refs = [requirements[0].id]
                milestones.append(item.model_copy(update={"requirement_ids": refs}))
            dod_model = dod_model.model_copy(update={"contracts": contracts, "milestones": milestones})

    tdd_model = TDDOutput.model_validate(source["tdd"]) if source.get("tdd") else None
    if tdd_model is not None:
        requirements = specs_model.prd.requirements if specs_model is not None else []
        acceptance = specs_model.prd.acceptance_criteria if specs_model is not None else []
        contracts = dod_model.contracts if dod_model is not None else []
        requirement_ids = {item.id for item in requirements}
        acceptance_ids = {item.id for item in acceptance}
        contract_by_ref = {item.id: item.id for item in contracts}
        contract_by_ref.update({item.name: item.id for item in contracts})
        req_by_ref = {item.id: item.id for item in requirements}
        req_by_ref.update({item.text: item.id for item in requirements})
        acc_by_ref = {item.id: item.id for item in acceptance}
        acc_by_ref.update({item.text: item.id for item in acceptance})

        tests = []
        for i, item in enumerate(tdd_model.test_cases, start=1):
            contract_refs = [contract_by_ref[ref] for ref in item.covers if ref in contract_by_ref]
            requirement_refs = [req_by_ref[ref] for ref in item.covers if ref in req_by_ref]
            acceptance_refs = [acc_by_ref[ref] for ref in item.covers if ref in acc_by_ref]
            if not requirement_refs and len(requirements) == 1:
                requirement_refs = [requirements[0].id]
            tests.append(
                item.model_copy(
                    update={
                        "id": _stable_id("TEST", i),
                        "contract_ids": _unique([*item.contract_ids, *contract_refs]),
                        "requirement_ids": _valid_refs(
                            [*item.requirement_ids, *requirement_refs], requirement_ids
                        ),
                        "acceptance_criteria_ids": _valid_refs(
                            [*item.acceptance_criteria_ids, *acceptance_refs], acceptance_ids
                        ),
                    }
                )
            )
        test_by_ref = {item.id: item.id for item in tests}
        test_by_ref.update({item.name: item.id for item in tests})
        steps = []
        for i, item in enumerate(tdd_model.implementation_steps, start=1):
            test_refs = [test_by_ref[ref] for ref in item.tests if ref in test_by_ref]
            linked_tests = [test for test in tests if test.id in test_refs]
            req_refs = _unique(
                [*item.requirement_ids, *(ref for test in linked_tests for ref in test.requirement_ids)]
            )
            steps.append(
                item.model_copy(
                    update={
                        "id": _stable_id("STEP", i),
                        "test_ids": _unique([*item.test_ids, *test_refs]),
                        "requirement_ids": _valid_refs(req_refs, requirement_ids),
                    }
                )
            )
        tdd_model = tdd_model.model_copy(update={"test_cases": tests, "implementation_steps": steps})

    if dod_model is not None:
        patch["dod"] = dod_model.model_dump()
    if specs_model is not None:
        patch["specs"] = specs_model.model_dump()
    if tdd_model is not None:
        patch["tdd"] = tdd_model.model_dump()
    return patch


def _check_ids(items: list[dict[str, Any]], prefix: str, label: str) -> list[str]:
    findings: list[str] = []
    ids = [item.get("id", "") for item in items]
    if any(not item_id for item_id in ids):
        findings.append(f"{label} contains an item without a stable ID")
    if len(ids) != len(set(ids)):
        findings.append(f"{label} contains duplicate IDs")
    if any(item_id and not item_id.startswith(f"{prefix}-") for item_id in ids):
        findings.append(f"{label} contains an ID with the wrong prefix")
    return findings


def traceability_findings(state: AgentState | dict[str, Any], require_tdd: bool = False) -> list[str]:
    """Return human-readable consistency findings; empty means traceable."""
    source = dict(state)
    dod = source.get("dod", {}) or {}
    specs = source.get("specs", {}) or {}
    tdd = source.get("tdd", {}) or {}
    findings: list[str] = []

    contracts = list(dod.get("contracts", []))
    dod_items = list(dod.get("dod", []))
    milestones = list(dod.get("milestones", []))
    prd = specs.get("prd", {}) if isinstance(specs, dict) else {}
    requirements = [
        item if isinstance(item, dict) else {"text": str(item)}
        for item in list(prd.get("requirements", []))
    ]
    acceptance = [
        item if isinstance(item, dict) else {"text": str(item)}
        for item in list(prd.get("acceptance_criteria", []))
    ]
    security = specs.get("security", {}) if isinstance(specs, dict) else {}
    security_checks = list(security.get("owasp_checks", []))
    tests = list(tdd.get("test_cases", []))
    steps = list(tdd.get("implementation_steps", []))

    findings.extend(_check_ids(contracts, "CON", "Contracts"))
    findings.extend(_check_ids(dod_items, "DOD", "DoD items"))
    findings.extend(_check_ids(milestones, "MILE", "Milestones"))
    findings.extend(_check_ids(requirements, "REQ", "Requirements"))
    findings.extend(_check_ids(acceptance, "ACC", "Acceptance criteria"))
    findings.extend(_check_ids(security_checks, "SEC", "Security checks"))
    if require_tdd or tests or steps:
        findings.extend(_check_ids(tests, "TEST", "Tests"))
        findings.extend(_check_ids(steps, "STEP", "Implementation steps"))

    requirement_ids = {item.get("id") for item in requirements}
    contract_ids = {item.get("id") for item in contracts}
    acceptance_ids = {item.get("id") for item in acceptance}
    test_ids = {item.get("id") for item in tests}

    covered_requirements = {
        ref for item in acceptance for ref in item.get("requirement_ids", []) if ref in requirement_ids
    }
    for requirement_id in requirement_ids - covered_requirements:
        if requirement_id:
            findings.append(f"Requirement {requirement_id} has no acceptance criterion")

    for contract in contracts:
        if requirement_ids and not set(contract.get("requirement_ids", [])) & requirement_ids:
            findings.append(f"Contract {contract.get('id', contract.get('name', 'unknown'))} is not linked to a requirement")

    for test in tests:
        if not (
            set(test.get("requirement_ids", [])) & requirement_ids
            or set(test.get("contract_ids", [])) & contract_ids
            or set(test.get("acceptance_criteria_ids", [])) & acceptance_ids
        ):
            findings.append(f"Test {test.get('id', test.get('name', 'unknown'))} has no traceability reference")

    if tests:
        covered_contracts = {
            ref for test in tests for ref in test.get("contract_ids", []) if ref in contract_ids
        }
        for contract_id in contract_ids - covered_contracts:
            if contract_id:
                findings.append(f"Contract {contract_id} has no covering test")

    if steps and tests:
        for step in steps:
            if not set(step.get("test_ids", [])) & test_ids:
                findings.append(f"Implementation step {step.get('id', step.get('title', 'unknown'))} has no mapped test")

    return findings
