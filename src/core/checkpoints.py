"""Durable, versioned pipeline checkpoints.

Machine-readable checkpoints live separately from the append-only ``MEMORY.md``
audit log.  Each completed pipeline stage creates exactly one JSON snapshot for
its run, written via ``os.replace`` so a process interruption cannot leave a
partially-written checkpoint at the final path.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from config.redaction import redact_value
from core.state import AgentState
from schemas.critic import CriticVerdict
from schemas.step0_refinement import RefinementOutput
from schemas.step1_dod import DoDOutput
from schemas.step2_specs import SpecsOutput
from schemas.step3_tdd import TDDOutput

CHECKPOINT_SCHEMA_VERSION = 1

# The number is deliberately encoded in the filename and document. It makes a
# partially completed run unambiguous while still allowing it to be resumed.
STAGES = (
    "repository_context",
    "refinement",
    "dod",
    "specs",
    "critic_pre_tdd",
    "tdd",
    "critic_final",
    "export",
)
_STAGE_INDEX = {name: index for index, name in enumerate(STAGES, start=1)}


class CheckpointError(RuntimeError):
    """Base error for checkpoint persistence and loading."""


class CheckpointCompatibilityError(CheckpointError):
    """A checkpoint belongs to an incompatible version or execution mode."""


class CheckpointIntegrityError(CheckpointError):
    """A checkpoint is malformed, incomplete, or out of sequence."""


class CheckpointEnvelope(BaseModel):
    """Versioned persisted representation of one completed pipeline stage."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    run_id: str = Field(min_length=1)
    stage: str
    stage_index: int = Field(ge=1)
    mode: Literal["blocking", "draft"]
    created_at: datetime
    run_config: dict[str, Any]
    state: dict[str, Any]
    stage_output: dict[str, Any]
    traceability: dict[str, list[str]]


def stage_index(stage: str) -> int:
    """Return the canonical stage index or raise a compatibility error."""
    try:
        return _STAGE_INDEX[stage]
    except KeyError as exc:
        raise CheckpointCompatibilityError(f"Unknown checkpoint stage: {stage}") from exc


def traceability_snapshot(state: AgentState | dict[str, Any]) -> dict[str, list[str]]:
    """Capture stable IDs separately so resume compatibility is inspectable."""
    source = dict(state)
    dod = source.get("dod", {}) or {}
    specs = source.get("specs", {}) or {}
    tdd = source.get("tdd", {}) or {}
    prd = specs.get("prd", {}) if isinstance(specs, dict) else {}
    security = specs.get("security", {}) if isinstance(specs, dict) else {}

    def ids(items: Any) -> list[str]:
        return [str(item["id"]) for item in items or [] if isinstance(item, dict) and item.get("id")]

    return {
        "contracts": ids(dod.get("contracts", [])),
        "requirements": ids(prd.get("requirements", [])),
        "acceptance_criteria": ids(prd.get("acceptance_criteria", [])),
        "security_checks": ids(security.get("owasp_checks", [])),
        "tests": ids(tdd.get("test_cases", [])),
        "implementation_steps": ids(tdd.get("implementation_steps", [])),
    }


def _validate_state(state: dict[str, Any], stage: str) -> None:
    """Validate all completed structured outputs before they are persisted/read."""
    if not state.get("run_id"):
        raise CheckpointIntegrityError("Checkpoint state is missing run_id")
    if state.get("mode") not in ("blocking", "draft"):
        raise CheckpointIntegrityError("Checkpoint state has an invalid execution mode")
    try:
        if state.get("refinement"):
            RefinementOutput.model_validate(state["refinement"])
        if state.get("dod"):
            DoDOutput.model_validate(state["dod"])
        if state.get("specs"):
            SpecsOutput.model_validate(state["specs"])
        if state.get("tdd"):
            TDDOutput.model_validate(state["tdd"])
        if state.get("critic_verdict"):
            CriticVerdict.model_validate(state["critic_verdict"])
    except ValidationError as exc:
        raise CheckpointIntegrityError(f"Checkpoint contains invalid stage output: {exc}") from exc

    required_key = {
        "repository_context": "code_context",
        "refinement": "refinement",
        "dod": "dod",
        "specs": "specs",
        "critic_pre_tdd": "critic_verdict",
        "tdd": "tdd",
        "critic_final": "critic_verdict",
    }.get(stage)
    if required_key and not state.get(required_key):
        raise CheckpointIntegrityError(
            f"Checkpoint for {stage} is incomplete: state.{required_key} is missing"
        )


def build_checkpoint(
    state: AgentState | dict[str, Any],
    stage: str,
    stage_output: dict[str, Any],
    run_config: dict[str, Any],
) -> CheckpointEnvelope:
    """Validate and construct a checkpoint envelope for a completed stage."""
    source = dict(state)
    index = stage_index(stage)
    _validate_state(source, stage)
    if not isinstance(stage_output, dict):
        raise CheckpointIntegrityError("Checkpoint stage_output must be an object")
    persisted_state = redact_value(source)
    persisted_output = redact_value(stage_output)
    persisted_config = redact_value(dict(run_config))
    return CheckpointEnvelope(
        schema_version=1,
        run_id=str(source["run_id"]),
        stage=stage,
        stage_index=index,
        mode=source["mode"],
        created_at=datetime.now(UTC),
        run_config=persisted_config,
        state=persisted_state,
        stage_output=persisted_output,
        traceability=traceability_snapshot(persisted_state),
    )


def checkpoint_path(checkpoint_dir: str | Path, run_id: str, stage: str) -> Path:
    """Return the canonical on-disk path for a run stage."""
    return Path(checkpoint_dir) / run_id / f"{stage_index(stage):02d}-{stage}.json"


def write_checkpoint(envelope: CheckpointEnvelope, checkpoint_dir: str | Path) -> Path:
    """Atomically write a new checkpoint and return its final path.

    A stage is immutable once written. This prevents a resumed process from
    silently changing the validated result it was supposed to reuse.
    """
    target = checkpoint_path(checkpoint_dir, envelope.run_id, envelope.stage)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise CheckpointIntegrityError(f"Checkpoint already exists: {target}")

    payload = envelope.model_dump(mode="json")
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise
    return target


def _load_one(path: Path) -> CheckpointEnvelope:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        envelope = CheckpointEnvelope.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise CheckpointIntegrityError(f"Corrupted checkpoint {path}: {exc}") from exc
    if envelope.stage_index != stage_index(envelope.stage):
        raise CheckpointIntegrityError(f"Checkpoint has an invalid stage index: {path}")
    _validate_state(envelope.state, envelope.stage)
    if envelope.state.get("run_id") != envelope.run_id:
        raise CheckpointIntegrityError(f"Checkpoint run_id does not match state: {path}")
    if envelope.state.get("mode") != envelope.mode:
        raise CheckpointIntegrityError(f"Checkpoint mode does not match state: {path}")
    if envelope.traceability != traceability_snapshot(envelope.state):
        raise CheckpointIntegrityError(f"Checkpoint traceability does not match state: {path}")
    return envelope


def load_run_checkpoints(checkpoint_dir: str | Path, run_id: str) -> list[CheckpointEnvelope]:
    """Load and verify every checkpoint in a run in chronological order."""
    run_dir = Path(checkpoint_dir) / run_id
    if not run_dir.is_dir():
        raise CheckpointIntegrityError(f"No checkpoints found for run: {run_id}")
    paths = sorted(run_dir.glob("*.json"))
    if not paths:
        raise CheckpointIntegrityError(f"No checkpoints found for run: {run_id}")
    checkpoints = [_load_one(path) for path in paths]
    indexes = [checkpoint.stage_index for checkpoint in checkpoints]
    if indexes != list(range(1, len(indexes) + 1)):
        raise CheckpointIntegrityError("Checkpoint stages are missing, duplicated, or out of order")
    if any(checkpoint.run_id != run_id for checkpoint in checkpoints):
        raise CheckpointIntegrityError("Checkpoint directory contains a different run_id")
    first = checkpoints[0]
    if any(checkpoint.mode != first.mode for checkpoint in checkpoints):
        raise CheckpointCompatibilityError("Checkpoint run has inconsistent execution modes")
    if any(checkpoint.run_config != first.run_config for checkpoint in checkpoints):
        raise CheckpointCompatibilityError("Checkpoint run has inconsistent runtime configuration")
    return checkpoints


def load_resume_point(checkpoint_dir: str | Path, run_id: str) -> CheckpointEnvelope:
    """Return the last valid durable state for ``--resume``."""
    return load_run_checkpoints(checkpoint_dir, run_id)[-1]
