"""Append-only checkpoint log on MEMORY.md."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from config.redaction import redact_text


def read_memory(memory_path: str | Path = "MEMORY.md") -> str:
    path = Path(memory_path)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_checkpoint(
    step: str,
    status: str,
    summary: str,
    memory_path: str | Path = "MEMORY.md",
) -> str:
    """Append one checkpoint block; return the block text (immutable, no rewrite)."""
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    block = f"\n## [{ts}] {step} — {status}\n{redact_text(summary.strip())}\n"
    path = Path(memory_path)
    if not path.exists():
        path.write_text("# MEMORY.md — checkpoint log\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(block)
    return block
