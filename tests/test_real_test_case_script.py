from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_real_test_case_runner_requires_a_preexported_token(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment.pop("GITHUB_TOKEN", None)
    output = tmp_path / "real-test"

    result = subprocess.run(
        ["bash", str(ROOT / "scripts/run_real_test_case.sh"), str(output)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "GITHUB_TOKEN must already be exported" in result.stderr
    assert not output.exists()
