import json
from types import SimpleNamespace

import pytest

from config.settings import Settings, load_settings
from core.llm_interface import generate_structured, register_mock
from core.telemetry import TelemetryRecorder
from schemas.step0_refinement import RefinementOutput


def test_settings_include_optional_telemetry_configuration():
    settings = load_settings(
        {
            "PHOENIX_ENABLED": "true",
            "PHOENIX_ENDPOINT": "http://phoenix:6006",
            "PHOENIX_PROJECT_NAME": "journey-tests",
            "TELEMETRY_PATH": "/tmp/journey-events.jsonl",
            "TELEMETRY_RETENTION_DAYS": "7",
            "TELEMETRY_MAX_BYTES": "1234",
            "MAX_RUN_COST_USD": "0.25",
            "MAX_RUN_TOKENS": "1000",
        }
    )
    assert settings.phoenix_enabled is True
    assert settings.phoenix_endpoint == "http://phoenix:6006"
    assert settings.phoenix_project_name == "journey-tests"
    assert settings.telemetry_path == "/tmp/journey-events.jsonl"
    assert settings.telemetry_retention_days == 7
    assert settings.telemetry_max_bytes == 1234
    assert settings.max_run_cost_usd == 0.25
    assert settings.max_run_tokens == 1000


def test_disabled_telemetry_is_a_noop(tmp_path):
    settings = Settings(phoenix_enabled=False, telemetry_path=str(tmp_path / "events.jsonl"))
    recorder = TelemetryRecorder(settings, run_id="run-1", mode="blocking")

    with recorder.stage("refinement"):
        pass
    recorder.record_event("resume", resumed_from="refinement")

    assert not (tmp_path / "events.jsonl").exists()


def test_enabled_telemetry_records_stage_traceability_and_mock_usage(tmp_path):
    settings = Settings(
        phoenix_enabled=True,
        telemetry_path=str(tmp_path / "events.jsonl"),
        phoenix_endpoint="http://phoenix:6006",
    )
    state = {
        "run_id": "run-2",
        "mode": "draft",
        "block_reasons": ["needs source"],
        "dod": {},
        "specs": {},
        "tdd": {},
    }
    recorder = TelemetryRecorder(settings, "run-2", "draft", state_provider=lambda: state)
    register_mock(
        "RefinementOutput",
        {"refined_ticket": "refined", "gaps": [], "questions": [], "assumptions": []},
    )

    with recorder.stage("refinement"):
        output = generate_structured("refine", RefinementOutput, use_mock=True)

    assert output.refined_ticket == "refined"
    event = json.loads((tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert event["event"] == "stage"
    assert event["run_id"] == "run-2"
    assert event["stage"] == "refinement"
    assert event["status"] == "ok"
    assert event["block_reasons"] == ["needs source"]
    assert event["attributes"]["final_model"] == "mock"
    assert event["attributes"]["llm_attempts"][0]["status"] == "ok"
    assert event["phoenix_endpoint"] == "http://phoenix:6006"


def test_enabled_telemetry_records_fallback_and_token_cost(tmp_path, monkeypatch):
    settings = Settings(
        phoenix_enabled=True,
        telemetry_path=str(tmp_path / "events.jsonl"),
        use_mock_llm=False,
        primary_model="primary",
        fallback_model="fallback",
        local_model="local",
    )
    recorder = TelemetryRecorder(settings, "run-3", "blocking")

    def fake_call(model, prompt, schema, settings):
        if model == "primary":
            raise RuntimeError("unavailable")
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"refined_ticket":"done","gaps":[],"questions":[],"assumptions":[]}'
                    )
                )
            ],
            usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7, total_tokens=18),
            _hidden_params={"response_cost": 0.0012},
        )

    monkeypatch.setattr("core.llm_interface._call_model", fake_call)
    with recorder.stage("refinement"):
        generate_structured("refine", RefinementOutput, use_mock=False, settings=settings)

    event = json.loads((tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert event["attributes"]["models"] == ["primary", "fallback"]
    assert event["attributes"]["fallback_attempts"] == 1
    assert event["attributes"]["final_model"] == "fallback"
    assert event["attributes"]["usage"] == {
        "input_tokens": 11,
        "output_tokens": 7,
        "total_tokens": 18,
        "cost_usd": 0.0012,
    }


def test_telemetry_redacts_secrets_and_honors_size_cap(tmp_path):
    settings = Settings(
        phoenix_enabled=True,
        telemetry_path=str(tmp_path / "events.jsonl"),
        telemetry_max_bytes=500,
    )
    recorder = TelemetryRecorder(settings, "run-secret", "blocking")
    recorder.record_event("security", secret="sk-proj-1234567890", detail="x" * 2_000)  # security-audit: allow-test-fixture

    assert recorder.retention_limit_reached is True
    assert not (tmp_path / "events.jsonl").exists()


def test_llm_budget_stops_before_next_generation(tmp_path, monkeypatch):
    settings = Settings(
        phoenix_enabled=True,
        telemetry_path=str(tmp_path / "events.jsonl"),
        use_mock_llm=False,
        primary_model="primary",
        fallback_model="",
        local_model="",
        max_run_tokens=10,
    )
    recorder = TelemetryRecorder(settings, "run-budget", "blocking")

    def fake_call(model, prompt, schema, settings):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"refined_ticket":"done","gaps":[],"questions":[],"assumptions":[]}'
                    )
                )
            ],
            usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7, total_tokens=18),
        )

    monkeypatch.setattr("core.llm_interface._call_model", fake_call)
    from core.telemetry import TelemetryBudgetExceeded

    with recorder.stage("refinement"), pytest.raises(TelemetryBudgetExceeded, match="token budget"):
        generate_structured("refine", RefinementOutput, use_mock=False, settings=settings)
