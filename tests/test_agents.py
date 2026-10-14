from core.llm_interface import register_mock
from core.state import initial_state


def test_refinement_agent_mocked():
    from agents.refinement_agent import run

    register_mock(
        "RefinementOutput",
        {
            "refined_ticket": "refined mock ticket",
            "gaps": [],
            "questions": [],
            "assumptions": ["assume X"],
        },
    )
    state = initial_state("vague ticket")
    patch, out = run(state, use_mock=True)
    assert out.refined_ticket.startswith("refined")
    assert "refinement" in patch


def test_dod_agent_injects_security():
    from agents.dod_agent import run

    register_mock(
        "DoDOutput",
        {
            "contracts": [{"kind": "json", "name": "r", "schema_ref": "S", "status_codes": [200]}],
            "dod": [{"criterion": "works", "verifiable": True}],
            "milestones": [{"order": 1, "title": "m1", "acceptance": "done"}],
        },
    )
    state = initial_state("t")
    state["refinement"] = {"refined_ticket": "r"}
    patch, out = run(state, use_mock=True)
    criteria = {d.criterion for d in out.dod}
    assert any("secrets" in c.lower() for c in criteria)
    assert "dod" in patch
