from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from scripts import run_local_skill

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "run_local_skill.py"


def test_local_skill_wrapper_returns_structured_approved_response(tmp_path: Path) -> None:
    output_dir = tmp_path / "approved"
    request = {
        "schema_version": 1,
        "ticket": "Add a health-check endpoint",
        "mode": "blocking",
        "out_dir": str(output_dir),
    }
    result = subprocess.run(
        [sys.executable, str(WRAPPER)],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "USE_MOCK_LLM": "true",
            "PHOENIX_ENABLED": "true",
        },
        check=False,
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["schema_version"] == 1
    assert response["status"] == "approved"
    assert response["github_status"] == "success"
    assert response["exit_code"] == 0
    assert response["approved"] is True
    assert response["artifact_dir"] == str(output_dir)
    assert Path(response["console_log"]).is_file()
    assert Path(response["output_paths"]["md"]).is_file()
    assert Path(response["output_paths"]["html"]).is_file()
    assert (output_dir / "run-status.json").is_file()
    assert (output_dir / "MEMORY.md").is_file()
    assert (output_dir / "checkpoints").is_dir()
    assert (output_dir / "telemetry" / "events.jsonl").is_file()


def test_local_skill_wrapper_rejects_invalid_request_without_writing(tmp_path: Path) -> None:
    output_dir = tmp_path / "should-not-exist"
    result = subprocess.run(
        [sys.executable, str(WRAPPER)],
        input=json.dumps(
            {"schema_version": 1, "ticket": "test", "mode": "unsafe", "out_dir": str(output_dir)}
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    response = json.loads(result.stdout)
    assert response["status"] == "invalid_request"
    assert not output_dir.exists()


def test_local_skill_wrapper_preserves_needs_input_exit_and_redacts_log(
    monkeypatch, tmp_path: Path
) -> None:
    output_dir = tmp_path / "needs-input"

    def fake_run(*args, **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "run-status.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "run_id": "run-1",
                    "status": "needs_input",
                    "approved": False,
                    "exit_code": 2,
                    "block_reasons": ["clarification required"],
                    "output_paths": {},
                }
            ),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=2, stdout="token=sk-proj-visible-secret", stderr="")

    monkeypatch.setattr(run_local_skill.subprocess, "run", fake_run)
    code, response = run_local_skill._run(
        {"ticket": "clarify scope", "mode": "blocking"}, output_dir
    )

    assert code == 2
    assert response["status"] == "needs_input"
    assert response["exit_code"] == 2
    console_log = (output_dir / "console.log").read_text(encoding="utf-8")
    assert "sk-proj-visible-secret" not in console_log
    assert "[REDACTED]" in console_log


def test_resume_without_mode_does_not_override_checkpoint_mode(tmp_path: Path) -> None:
    command = run_local_skill._build_command(
        {"resume": "run-1", "out_dir": str(tmp_path)}, tmp_path
    )

    assert command[-2:] == ["--resume", "run-1"]
    assert "--mode" not in command
