import json
from pathlib import Path

import pytest

from core.state import initial_state
from main import _refinement_block_reasons, main


def test_initial_state_defaults_to_blocking():
    state = initial_state("ticket")
    assert state["mode"] == "blocking"
    assert state["status"] == "running"


def test_high_gap_and_question_block_approval():
    reasons = _refinement_block_reasons(
        {
            "gaps": [{"area": "scope", "severity": "high", "description": "unclear"}],
            "questions": [{"question": "which source?"}],
        },
        {"status": "not_requested"},
    )
    assert len(reasons) == 2


def test_blocking_mode_exports_needs_input(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("MEMORY_PATH", str(tmp_path / "MEMORY.md"))
    monkeypatch.setenv("CHECKPOINT_DIR", str(tmp_path / "checkpoints"))
    out_dir = tmp_path / "out"
    status_file = tmp_path / "run-status.json"
    exit_code = main(
        [
            "--ticket",
            "Demo",
            "--demo",
            "--out-dir",
            str(out_dir),
            "--status-file",
            str(status_file),
        ]
    )
    assert exit_code == 2
    markdown = Path(out_dir / "FEATURE_SPEC.md").read_text(encoding="utf-8")
    assert "`needs_input`" in markdown
    assert "Clarification required" in markdown
    payload = json.loads(status_file.read_text(encoding="utf-8"))
    assert payload["status"] == "needs_input"
    assert payload["github_status"] == "failure"


def test_draft_mode_continues_but_is_not_approved(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("MEMORY_PATH", str(tmp_path / "MEMORY.md"))
    monkeypatch.setenv("CHECKPOINT_DIR", str(tmp_path / "checkpoints"))
    out_dir = tmp_path / "out"
    exit_code = main(
        ["--ticket", "Demo", "--demo", "--mode", "draft", "--out-dir", str(out_dir)]
    )
    assert exit_code == 2
    markdown = Path(out_dir / "FEATURE_SPEC.md").read_text(encoding="utf-8")
    assert "**Run status:** `draft`" in markdown
    assert "Approved: **False**" in markdown


def test_resume_continues_from_last_durable_stage_without_recalling_completed_agents(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("MEMORY_PATH", str(tmp_path / "MEMORY.md"))
    monkeypatch.setenv("CHECKPOINT_DIR", str(tmp_path / "checkpoints"))
    out_dir = tmp_path / "out"

    from agents import dod_agent, refinement_agent, specs_agent, tdd_agent

    original_tdd = tdd_agent.run

    def interrupt_after_completed_stages(*_args, **_kwargs):
        raise RuntimeError("simulated interruption")

    monkeypatch.setattr(tdd_agent, "run", interrupt_after_completed_stages)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        main(["--ticket", "Add search", "--out-dir", str(out_dir)])

    run_id = next((tmp_path / "checkpoints").iterdir()).name
    monkeypatch.setattr(tdd_agent, "run", original_tdd)

    def should_not_run(*_args, **_kwargs):
        raise AssertionError("a completed stage was called again during resume")

    monkeypatch.setattr(refinement_agent, "run", should_not_run)
    monkeypatch.setattr(dod_agent, "run", should_not_run)
    monkeypatch.setattr(specs_agent, "run", should_not_run)

    assert main(["--resume", run_id]) == 0
    assert (out_dir / "FEATURE_SPEC.md").exists()
    assert len(list((tmp_path / "checkpoints" / run_id).glob("*.json"))) == 8


def test_resume_preserves_blocking_gate(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("MEMORY_PATH", str(tmp_path / "MEMORY.md"))
    monkeypatch.setenv("CHECKPOINT_DIR", str(tmp_path / "checkpoints"))
    out_dir = tmp_path / "out"

    assert main(["--ticket", "Demo", "--demo", "--out-dir", str(out_dir)]) == 2
    run_id = next((tmp_path / "checkpoints").iterdir()).name

    assert main(["--resume", run_id]) == 2
    assert "Clarification required" in (out_dir / "FEATURE_SPEC.md").read_text(encoding="utf-8")


def test_pipeline_emits_optional_stage_telemetry(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("PHOENIX_ENABLED", "true")
    monkeypatch.setenv("TELEMETRY_PATH", str(tmp_path / "events.jsonl"))
    monkeypatch.setenv("MEMORY_PATH", str(tmp_path / "MEMORY.md"))
    monkeypatch.setenv("CHECKPOINT_DIR", str(tmp_path / "checkpoints"))

    assert main(["--ticket", "Demo", "--demo", "--out-dir", str(tmp_path / "out")]) == 2
    import json

    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert {event["stage"] for event in events if event["event"] == "stage"} >= {
        "repository_context",
        "refinement",
    }
    gate = next(event for event in events if event["event"] == "pipeline_gate")
    assert gate["status"] == "needs_input"
    assert gate["block_reasons"]
