import json

from core.review_signals import build_run_status, github_status_state, write_run_status


def test_github_status_mapping_preserves_review_semantics():
    assert github_status_state("approved", 0) == "success"
    assert github_status_state("draft", 2) == "pending"
    assert github_status_state("needs_input", 2) == "failure"
    assert github_status_state("failed", 1) == "error"


def test_status_payload_is_safe_and_atomic(tmp_path):
    state = {
        "run_id": "run-123",
        "mode": "draft",
        "status": "draft",
        "block_reasons": ["Clarification required: data source"],
        "ticket_text": "untrusted ticket text is intentionally omitted",
    }
    path = tmp_path / "artifacts" / "run-status.json"

    payload = write_run_status(path, state, 2, {"md": tmp_path / "FEATURE_SPEC.md"})

    assert json.loads(path.read_text(encoding="utf-8")) == payload
    assert payload["github_status"] == "pending"
    assert "ticket_text" not in payload
    assert not list(path.parent.glob(".run-status.json.tmp"))


def test_build_status_converts_paths_to_strings():
    payload = build_run_status(
        {"run_id": "run-1", "mode": "blocking", "status": "approved"},
        0,
        {"md": "/tmp/FEATURE_SPEC.md"},
    )
    assert payload["output_paths"] == {"md": "/tmp/FEATURE_SPEC.md"}
