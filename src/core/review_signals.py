"""Machine-readable review signals for local and GitHub workflow consumers."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def github_status_state(run_status: str, exit_code: int) -> str:
    """Map a pipeline outcome to a GitHub commit-status state."""
    if run_status == "approved" and exit_code == 0:
        return "success"
    if run_status == "draft" and exit_code == 2:
        return "pending"
    if run_status == "needs_input" and exit_code == 2:
        return "failure"
    return "error"


def build_run_status(
    state: dict[str, Any],
    exit_code: int,
    output_paths: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a stable status payload without including credentials or prompts."""
    run_status = str(state.get("status", "failed"))
    return {
        "schema_version": 1,
        "run_id": str(state.get("run_id", "")),
        "mode": str(state.get("mode", "")),
        "status": run_status,
        "github_status": github_status_state(run_status, exit_code),
        "exit_code": exit_code,
        "approved": run_status == "approved",
        "block_reasons": [str(reason) for reason in state.get("block_reasons", [])],
        "output_paths": {
            str(key): os.fspath(value)
            for key, value in (output_paths or {}).items()
            if value is not None
        },
    }


def write_run_status(
    path: str | Path,
    state: dict[str, Any],
    exit_code: int,
    output_paths: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Atomically write the status payload and return it for callers/tests."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = build_run_status(state, exit_code, output_paths)
    temporary = destination.with_name(f".{destination.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return payload
