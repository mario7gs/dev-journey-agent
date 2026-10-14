from config.redaction import REDACTED, redact_text, redact_value


def test_redacts_common_credentials_and_url_auth():
    text = "token=sk-proj-1234567890 password=hunter2 https://alice:secret@example.com"

    safe = redact_text(text)

    assert "sk-proj-1234567890" not in safe
    assert "password=[REDACTED]" in safe
    assert "alice:secret@" not in safe
    assert REDACTED in safe


def test_redacts_sensitive_mapping_keys_recursively():
    safe = redact_value({"api_key": "visible-secret", "nested": ["ghp_1234567890"]})

    assert safe["api_key"] == REDACTED
    assert safe["nested"] == [REDACTED]
