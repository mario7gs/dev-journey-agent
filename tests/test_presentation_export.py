from tools.presentation_exporter import build_presentation_context, render_presentation


def test_presentation_contains_accessible_case_study_sections():
    state = {
        "ticket_text": "vague ticket",
        "repo_ref": "owner/repo",
        "branch": "main",
        "mode": "blocking",
        "status": "approved",
        "refinement": {"refined_ticket": "refined goal"},
        "dod": {"dod": [{"criterion": "works"}], "milestones": []},
        "specs": {"prd": {"goal": "deliver search", "requirements": ["ranked"]}},
        "tdd": {"test_cases": [{}], "implementation_steps": [{}], "coverage_target": 80},
        "critic_verdict": {"approved": True},
    }

    html = render_presentation(state)

    assert '<html lang="en">' in html
    assert 'aria-labelledby="slide-title"' in html
    assert "deliver search" in html
    assert "PDF-ready" in html
    assert 'src="data:image/png;base64,' in html


def test_presentation_context_counts_delivery_evidence():
    context = build_presentation_context(
        {
            "specs": {"prd": {"requirements": ["one", "two"]}},
            "dod": {"dod": [{"criterion": "works"}]},
            "tdd": {"test_cases": [{}, {}], "implementation_steps": [{}], "coverage_target": 90},
            "critic_verdict": {"approved": False},
        }
    )

    assert context["requirements"] == ["one", "two"]
    assert len(context["dod_items"]) == 1
    assert context["test_count"] == 2
    assert context["implementation_count"] == 1
    assert context["coverage_target"] == 90
