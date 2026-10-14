from core.memory_manager import append_checkpoint, read_memory


def test_memory_roundtrip(tmp_path):
    mem = tmp_path / "MEMORY.md"
    block = append_checkpoint("Step0-test", "done", "summary one", memory_path=mem)
    assert "Step0-test" in block
    content = read_memory(mem)
    assert "summary one" in content
    append_checkpoint("Step1-test", "done", "summary two", memory_path=mem)
    content2 = read_memory(mem)
    assert "summary one" in content2 and "summary two" in content2


def test_read_missing_returns_empty(tmp_path):
    assert read_memory(tmp_path / "nope.md") == ""


def test_memory_audit_redacts_credentials(tmp_path):
    mem = tmp_path / "MEMORY.md"
    append_checkpoint("security", "done", "token=ghp_1234567890", memory_path=mem)

    content = read_memory(mem)
    assert "ghp_1234567890" not in content
    assert "token=[REDACTED]" in content
