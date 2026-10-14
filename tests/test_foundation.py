import pytest

from config.security_guardrails import (
    is_blocked_text,
    sanitize_input,
    validate_upload_meta,
)
from config.settings import load_settings


def test_settings_defaults_mock():
    s = load_settings({})
    assert s.use_mock_llm is True
    assert s.primary_model == "gpt-4o"


def test_settings_env_override():
    s = load_settings({"USE_MOCK_LLM": "false", "PRIMARY_MODEL": "x"})
    assert s.use_mock_llm is False
    assert s.primary_model == "x"


def test_guardrails():
    assert sanitize_input("  hi  ") == "hi"
    assert is_blocked_text("sk-proj-abc") is True
    assert is_blocked_text("clean") is False
    with pytest.raises(ValueError):
        validate_upload_meta("evil.exe", 10)
    with pytest.raises(ValueError):
        validate_upload_meta("a.png", 10**9)
    validate_upload_meta("a.png", 10)


def test_missing_template_raises(tmp_path):
    from tools.html_exporter import render_report

    with pytest.raises(FileNotFoundError):
        render_report({}, template_path=str(tmp_path / "nope.j2"))
