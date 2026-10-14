import pytest

from agents.tdd_agent import run as run_tdd
from core.llm_interface import register_mock
from core.state import initial_state


def _seeded_state():
    register_mock(
        "TDDOutput",
        {
            "test_cases": [],
            "implementation_steps": [],
            "red_green_notes": "",
            "coverage_target": 0,
        },
    )
    state = initial_state("ticket")
    state["refinement"] = {"refined_ticket": "refined"}
    state["dod"] = {
        "contracts": [
            {"kind": "json", "name": "search-response", "schema_ref": "S", "status_codes": [200]}
        ],
        "dod": [{"criterion": "works", "verifiable": True}],
        "milestones": [
            {"order": 1, "title": "scaffold", "acceptance": "tests pass"},
            {"order": 2, "title": "implement", "acceptance": "dod verified"},
        ],
    }
    state["specs"] = {
        "prd": {"goal": "deliver search", "requirements": ["ranked"]},
        "trd": {"components": ["api"]},
        "security": {"owasp_checks": [{"check": "x", "status": "pass"}]},
    }
    return state


def test_tdd_agent_guardrails_fill_suite():
    state = _seeded_state()
    patch, out = run_tdd(state, use_mock=True)
    kinds = {c.kind for c in out.test_cases}
    assert "unit" in kinds and "integration" in kinds
    assert out.coverage_target >= 80
    assert out.red_green_notes != ""
    assert [s.order for s in out.implementation_steps] == list(
        range(1, len(out.implementation_steps) + 1)
    )
    assert "tdd" in patch


def test_tdd_covers_every_contract():
    state = _seeded_state()
    _, out = run_tdd(state, use_mock=True)
    covered = {ref for c in out.test_cases for ref in c.covers}
    assert "search-response" in covered


def test_tdd_generates_a_test_for_each_milestone():
    state = _seeded_state()
    _, out = run_tdd(state, use_mock=True)
    names = {case.name for case in out.test_cases}
    assert any("scaffold" in name for name in names)
    assert any("implement" in name for name in names)


def test_tdd_requires_prior_steps():
    with pytest.raises(ValueError):
        run_tdd(initial_state("t"), use_mock=True)
    st = initial_state("t")
    st["dod"] = {"contracts": [], "dod": [], "milestones": []}
    with pytest.raises(ValueError):
        run_tdd(st, use_mock=True)
