from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_demo_generates_two_scenario_summary(tmp_path: Path) -> None:
    output = tmp_path / "portfolio-demo"
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")

    result = subprocess.run(
        ["bash", str(ROOT / "scripts/run_portfolio_demo.sh"), str(output)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (output / "DEMO_SUMMARY.html").is_file()
    summary = (output / "DEMO_SUMMARY.html").read_text(encoding="utf-8")
    assert "Two outcomes, one safe planning pipeline." in summary
    assert 'src="data:image/png;base64,' in summary
    assert "AGENT · FEATURE PLANNING COPILOT" in summary
    assert 'class="site-header"' in summary
    assert 'href="#scenarios"' in summary
    assert 'href="#evidence"' in summary
    assert "position:sticky" in summary

    approved = json.loads((output / "approved/run-status.json").read_text(encoding="utf-8"))
    needs_input = json.loads((output / "needs-input/run-status.json").read_text(encoding="utf-8"))
    assert (approved["status"], approved["github_status"], approved["exit_code"]) == (
        "approved",
        "success",
        0,
    )
    assert (needs_input["status"], needs_input["github_status"], needs_input["exit_code"]) == (
        "needs_input",
        "failure",
        2,
    )
    assert "Secret audit passed" in (output / "security-audit.txt").read_text(encoding="utf-8")
    assert (output / "approved/cost-summary.json").is_file()
    assert (output / "needs-input/cost-summary.json").is_file()
