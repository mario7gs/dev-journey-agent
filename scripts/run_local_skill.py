#!/usr/bin/env python3
"""Provider-neutral local invocation contract for Dev-Journey-Agent.

The wrapper intentionally stays at the edge of the system. It accepts one JSON
request, delegates to the existing CLI without a shell, and emits one concise
JSON response. It does not implement planning, call a provider, or write to
GitHub directly.

Example::

    echo '{"ticket":"Add a health-check endpoint","mode":"blocking"}' \
      | uv run python scripts/run_local_skill.py
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from config.redaction import redact_text

REQUEST_SCHEMA_VERSION = 1
ALLOWED_KEYS = frozenset(
    {"schema_version", "ticket", "repo", "branch", "mode", "out_dir", "resume"}
)
MAX_TICKET_CHARS = 10_000
DEFAULT_BRANCH = "main"
DEFAULT_MODE = "blocking"


class SkillRequestError(ValueError):
    """Raised when a local skill request is invalid."""


def _project_root() -> Path:
    return PROJECT_ROOT


def _read_request(raw: str) -> dict[str, Any]:
    try:
        request = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SkillRequestError(f"request must be valid JSON: {exc.msg}") from exc
    if not isinstance(request, dict):
        raise SkillRequestError("request must be a JSON object")

    unknown = sorted(set(request) - ALLOWED_KEYS)
    if unknown:
        raise SkillRequestError(f"unsupported request fields: {', '.join(unknown)}")

    schema_version = request.get("schema_version", REQUEST_SCHEMA_VERSION)
    if schema_version != REQUEST_SCHEMA_VERSION:
        raise SkillRequestError(
            f"unsupported schema_version {schema_version!r}; expected {REQUEST_SCHEMA_VERSION}"
        )

    resume = request.get("resume")
    if resume is not None and (not isinstance(resume, str) or not resume.strip()):
        raise SkillRequestError("resume must be a non-empty string when provided")

    ticket = request.get("ticket")
    if resume is None:
        if not isinstance(ticket, str) or not ticket.strip():
            raise SkillRequestError("ticket is required unless resume is supplied")
        if len(ticket) > MAX_TICKET_CHARS:
            raise SkillRequestError(f"ticket exceeds the {MAX_TICKET_CHARS}-character limit")
        if "\x00" in ticket:
            raise SkillRequestError("ticket must not contain NUL characters")
    elif ticket is not None and not isinstance(ticket, str):
        raise SkillRequestError("ticket must be a string when provided")

    for field in ("repo", "branch", "out_dir"):
        value = request.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise SkillRequestError(f"{field} must be a non-empty string when provided")

    mode = request.get("mode", DEFAULT_MODE)
    if mode not in ("blocking", "draft"):
        raise SkillRequestError("mode must be 'blocking' or 'draft'")

    if resume is not None and request.get("out_dir") is None:
        raise SkillRequestError("out_dir is required when resuming a wrapper run")
    if resume is not None:
        conflicting = sorted(field for field in ("ticket", "repo", "branch") if field in request)
        if conflicting:
            raise SkillRequestError(
                "resume requests may only include resume, out_dir, mode, and schema_version"
            )

    return request


def _resolve_output_dir(request: dict[str, Any]) -> Path:
    root = _project_root()
    raw_out_dir = request.get("out_dir")
    if raw_out_dir is None:
        raw_out_dir = os.path.join("artifacts", "skill-runs", uuid4().hex)
    candidate = Path(str(raw_out_dir)).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    output_dir = candidate.resolve()
    if output_dir == output_dir.parent or output_dir == root:
        raise SkillRequestError("out_dir must identify a dedicated artifact directory")
    try:
        relative = output_dir.relative_to(root)
    except ValueError:
        relative = None
    if relative is not None and ".git" in relative.parts:
        raise SkillRequestError("out_dir cannot be inside .git")
    return output_dir


def _build_command(request: dict[str, Any], output_dir: Path) -> list[str]:
    command = [sys.executable, str(_project_root() / "src" / "main.py")]
    resume = request.get("resume")
    if resume is not None:
        command.extend(["--resume", str(resume)])
        if "mode" in request:
            command.extend(["--mode", str(request["mode"])])
        return command

    command.extend(["--ticket", str(request["ticket"])])
    if request.get("repo") is not None:
        command.extend(["--repo", str(request["repo"])])
    command.extend(["--branch", str(request.get("branch", DEFAULT_BRANCH))])
    command.extend(["--mode", str(request.get("mode", DEFAULT_MODE))])
    command.extend(["--out-dir", str(output_dir)])
    command.extend(["--status-file", str(output_dir / "run-status.json")])
    return command


def _run(request: dict[str, Any], output_dir: Path) -> tuple[int, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    # Keep wrapper state isolated from the caller's default MEMORY.md and
    # .dev-journey paths. Credentials, if intentionally configured, are only
    # consumed by the delegated CLI and are never added to the response.
    environment["MEMORY_PATH"] = str(output_dir / "MEMORY.md")
    environment["CHECKPOINT_DIR"] = str(output_dir / "checkpoints")
    environment["TELEMETRY_PATH"] = str(output_dir / "telemetry" / "events.jsonl")
    existing_pythonpath = environment.get("PYTHONPATH", "")
    pythonpath_entries = [str(_project_root()), str(_project_root() / "src")]
    if existing_pythonpath:
        pythonpath_entries.append(existing_pythonpath)
    environment["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)

    try:
        completed = subprocess.run(
            _build_command(request, output_dir),
            cwd=_project_root(),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        message = redact_text(f"unable to start delegated CLI: {exc}")
        return 1, {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "status": "failed",
            "exit_code": 1,
            "error": message,
        }

    console_log = output_dir / "console.log"
    console_log.write_text(
        redact_text(completed.stdout + completed.stderr), encoding="utf-8"
    )
    status_path = output_dir / "run-status.json"
    if not status_path.is_file():
        message = redact_text(
            f"delegated CLI did not produce {status_path.name}; process exit {completed.returncode}"
        )
        return 1, {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "status": "failed",
            "exit_code": 1,
            "error": message,
            "console_log": str(console_log),
        }

    try:
        pipeline_status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        message = redact_text(f"invalid delegated status file: {exc}")
        return 1, {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "status": "failed",
            "exit_code": 1,
            "error": message,
            "console_log": str(console_log),
        }

    response = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "run_id": pipeline_status.get("run_id", ""),
        "status": pipeline_status.get("status", "failed"),
        "github_status": pipeline_status.get("github_status", ""),
        "approved": bool(pipeline_status.get("approved", False)),
        "exit_code": int(pipeline_status.get("exit_code", completed.returncode)),
        "block_reasons": pipeline_status.get("block_reasons", []),
        "output_paths": pipeline_status.get("output_paths", {}),
        "artifact_dir": str(output_dir),
        "console_log": str(console_log),
    }
    return completed.returncode, response


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Invoke Dev-Journey-Agent through a provider-neutral JSON contract"
    )
    parser.add_argument(
        "--request-file",
        type=Path,
        help="Read the JSON request from a file instead of stdin",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        raw_request = (
            args.request_file.read_text(encoding="utf-8")
            if args.request_file is not None
            else sys.stdin.read()
        )
        request = _read_request(raw_request)
        output_dir = _resolve_output_dir(request)
        process_exit, response = _run(request, output_dir)
    except (OSError, SkillRequestError) as exc:
        response = {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "status": "invalid_request",
            "exit_code": 1,
            "error": redact_text(str(exc)),
        }
        process_exit = 1

    print(json.dumps(response, indent=2, sort_keys=True))
    return process_exit


if __name__ == "__main__":
    raise SystemExit(main())
