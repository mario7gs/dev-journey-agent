from pathlib import Path

from scripts.security_audit import scan_paths, scan_text


def test_security_audit_ignores_short_test_fixtures(tmp_path):
    fixture = tmp_path / "fixture.txt"
    fixture.write_text("token=sk-proj-1234567890\ngithub_token=visible-token\n", encoding="utf-8")

    assert scan_paths([fixture]) == []


def test_security_audit_finds_provider_tokens_and_live_assignments(tmp_path):
    fixture = tmp_path / "leak.txt"
    fixture.write_text(
        "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456\n"  # security-audit: allow-test-fixture
        "github_token=ghp_abcdefghijklmnopqrstuvwxyz123456\n",  # security-audit: allow-test-fixture
        encoding="utf-8",
    )

    findings = scan_paths([fixture])

    assert {finding.kind for finding in findings} == {"provider-token", "credential-assignment"}


def test_security_audit_skips_generated_and_binary_directories(tmp_path):
    generated = tmp_path / "dist"
    generated.mkdir()
    (generated / "secret.txt").write_text(
        "token=sk-proj-abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8"  # security-audit: allow-test-fixture
    )
    (tmp_path / "image.png").write_bytes(b"token=sk-proj-abcdefghijklmnopqrstuvwxyz123456")  # security-audit: allow-test-fixture

    assert scan_paths([tmp_path]) == []


def test_security_audit_reports_private_key_line():
    private_key = "before\n-----BEGIN RSA PRIVATE KEY-----\n"  # security-audit: allow-test-fixture
    findings = scan_text(private_key, Path("secret.pem"))

    assert findings[0].line == 2
    assert findings[0].kind == "private-key"
