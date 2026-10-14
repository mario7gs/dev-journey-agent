from agents.critic_agent import run as run_critic
from agents.specs_agent import fallback_mermaid, is_valid_mermaid
from agents.specs_agent import run as run_specs
from core.llm_interface import register_mock
from core.state import initial_state
from core.traceability import apply_traceability, traceability_findings


def _seeded_state():
    register_mock(
        "SpecsOutput",
        {
            "prd": {
                "goal": "deliver search",
                "background": "users lost",
                "users": ["trader"],
                "requirements": ["ranked results"],
                "non_goals": [],
                "acceptance_criteria": ["top-5 relevant"],
            },
            "trd": {
                "components": ["api"],
                "api_endpoints": [],
                "data_model": [],
                "mermaid_flow": "",
                "security_notes": [],
            },
            "security": {"owasp_checks": [], "input_sanitization": "", "auth_enforcement": ""},
        },
    )
    state = initial_state("ticket")
    state["refinement"] = {"refined_ticket": "refined"}
    state["dod"] = {
        "contracts": [],
        "dod": [],
        "milestones": [{"title": "scaffold"}, {"title": "implement"}],
    }
    return state


def test_mermaid_validation():
    assert is_valid_mermaid("flowchart TD\n    A-->B") is True
    assert is_valid_mermaid("sequenceDiagram\n    A->>B: hi") is True
    assert is_valid_mermaid("just text") is False
    assert is_valid_mermaid("<script>alert(1)</script>") is False


def test_specs_agent_injects_mermaid_and_security():
    state = _seeded_state()
    patch, out = run_specs(state, use_mock=True)
    assert is_valid_mermaid(out.trd.mermaid_flow)
    assert len(out.security.owasp_checks) >= 5
    assert out.security.input_sanitization != ""
    assert out.security.auth_enforcement != ""
    assert "specs" in patch


def test_fallback_mermaid_from_milestones():
    chart = fallback_mermaid({"milestones": [{"title": "alpha"}, {"title": "beta"}]})
    assert chart.startswith("flowchart TD")
    assert "alpha" in chart and "beta" in chart


def test_critic_approves_complete_state():
    state = _seeded_state()
    patch, _specs = run_specs(state, use_mock=True)
    state.update(patch)
    # complete the dod surface the critic requires
    state["dod"] = {
        "contracts": [{"kind": "json", "name": "search-response", "schema_ref": "S"}],
        "dod": [{"criterion": "x"}],
        "milestones": [{"order": 1, "title": "m", "acceptance": "done"}],
    }
    state.update(apply_traceability(state))
    _, verdict = run_critic(state)
    assert verdict.approved is True
    assert verdict.missing == []


def test_traceability_links_requirements_contracts_and_acceptance():
    state = _seeded_state()
    state["dod"] = {
        "contracts": [{"kind": "json", "name": "search-response", "schema_ref": "S"}],
        "dod": [{"criterion": "x"}],
        "milestones": [{"order": 1, "title": "m", "acceptance": "done"}],
    }
    patch, _specs = run_specs(state, use_mock=True)
    state.update(patch)
    state.update(apply_traceability(state))

    requirement = state["specs"]["prd"]["requirements"][0]
    contract = state["dod"]["contracts"][0]
    criterion = state["specs"]["prd"]["acceptance_criteria"][0]
    assert requirement["id"] == "REQ-001"
    assert contract["id"] == "CON-001"
    assert contract["requirement_ids"] == ["REQ-001"]
    assert criterion["id"] == "ACC-001"
    assert criterion["requirement_ids"] == ["REQ-001"]
    assert traceability_findings(state) == []


def test_traceability_reports_uncovered_contract():
    state = _seeded_state()
    state["dod"] = {
        "contracts": [{"kind": "json", "name": "search-response", "schema_ref": "S"}],
        "dod": [{"criterion": "x"}],
        "milestones": [{"order": 1, "title": "m", "acceptance": "done"}],
    }
    patch, _specs = run_specs(state, use_mock=True)
    state.update(patch)
    state.update(apply_traceability(state))
    state["tdd"] = {
        "test_cases": [
            {
                "id": "TEST-001",
                "name": "unit: requirement",
                "requirement_ids": ["REQ-001"],
                "contract_ids": [],
            }
        ],
        "implementation_steps": [],
        "coverage_target": 80,
    }
    assert any("has no covering test" in item for item in traceability_findings(state, require_tdd=True))


def test_critic_rejects_empty_state():
    state = initial_state("ticket")
    _, verdict = run_critic(state)
    assert verdict.approved is False
    assert len(verdict.missing) > 0
    assert any(i.severity == "high" for i in verdict.issues)


def test_specs_requires_prior_steps():
    import pytest

    with pytest.raises(ValueError):
        run_specs(initial_state("t"), use_mock=True)
