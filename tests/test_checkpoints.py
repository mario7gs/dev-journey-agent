import json

import pytest

from core.checkpoints import (
    CheckpointIntegrityError,
    build_checkpoint,
    load_resume_point,
    write_checkpoint,
)
from core.state import initial_state


def _context_state():
    state = initial_state("Add search")
    state["run_id"] = "run-123"
    state["code_context"] = {"status": "not_requested", "chunks": []}
    return state


def test_checkpoint_round_trip_is_versioned_and_immutable(tmp_path):
    state = _context_state()
    envelope = build_checkpoint(
        state,
        "repository_context",
        state["code_context"],
        {"demo": False, "out_dir": "docs", "use_mock_llm": True},
    )
    path = write_checkpoint(envelope, tmp_path)

    loaded = load_resume_point(tmp_path, "run-123")
    assert path.exists()
    assert loaded.schema_version == 1
    assert loaded.state == state
    assert loaded.traceability["requirements"] == []

    with pytest.raises(CheckpointIntegrityError, match="already exists"):
        write_checkpoint(envelope, tmp_path)


def test_checkpoint_loader_rejects_corrupt_json(tmp_path):
    state = _context_state()
    envelope = build_checkpoint(
        state,
        "repository_context",
        state["code_context"],
        {"demo": False, "out_dir": "docs", "use_mock_llm": True},
    )
    path = write_checkpoint(envelope, tmp_path)
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(CheckpointIntegrityError, match="Corrupted checkpoint"):
        load_resume_point(tmp_path, "run-123")


def test_checkpoint_loader_rejects_traceability_tampering(tmp_path):
    state = _context_state()
    envelope = build_checkpoint(
        state,
        "repository_context",
        state["code_context"],
        {"demo": False, "out_dir": "docs", "use_mock_llm": True},
    )
    path = write_checkpoint(envelope, tmp_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["traceability"]["requirements"] = ["REQ-999"]
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(CheckpointIntegrityError, match="traceability"):
        load_resume_point(tmp_path, "run-123")
