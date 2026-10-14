"""Fail when source-controlled files contain recognizable live credentials."""
from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    kind: str


_BINARY_SUFFIXES = {
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pyc",
    ".svg",
    ".woff",
    ".woff2",
}
_EXCLUDED_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "build", "dist"}
_TOKEN_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN [^-]+ PRIVATE KEY-----")),
    ("provider-token", re.compile(r"\b(?:sk-(?:proj|live)-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
)
_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|authorization|client[_-]?secret|"
    r"github[_-]?token|password|passwd|secret)\b\s*[:=]\s*['\"]?([^\s,'\"]+)"
)
_PLACEHOLDERS = {"", "example", "test", "testing", "dummy", "fake", "sample", "changeme", "redacted", "visible-secret", "visible-token"}


def _entropy(value: str) -> float:
    counts = {character: value.count(character) for character in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def _looks_live(value: str) -> bool:
    clean = value.strip().strip("`$()")
    if clean.lower() in _PLACEHOLDERS or len(clean) < 16:
        return False
    return _entropy(clean) >= 3.0 or any(character.isdigit() for character in clean)


def scan_text(text: str, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if "tests" in path.parts and "security-audit: allow-test-fixture" in line:
            continue
        for kind, pattern in _TOKEN_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path, line_number, kind))
        assignment = _ASSIGNMENT_PATTERN.search(line)
        if assignment and _looks_live(assignment.group(1)):
            findings.append(Finding(path, line_number, "credential-assignment"))
    return findings


def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() in _BINARY_SUFFIXES:
            continue
        if any(part in _EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return files


def scan_paths(paths: list[str | Path]) -> list[Finding]:
    """Scan files or directory trees, skipping generated/binary content."""
    findings: list[Finding] = []
    for raw_path in paths:
        path = Path(raw_path)
        candidates = _iter_files(path) if path.is_dir() else [path]
        for candidate in candidates:
            try:
                findings.extend(scan_text(candidate.read_text(encoding="utf-8"), candidate))
            except (OSError, UnicodeDecodeError):
                continue
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to scan")
    args = parser.parse_args(argv)
    findings = scan_paths(args.paths)
    if findings:
        for finding in findings:
            print(f"{finding.path}:{finding.line}: possible {finding.kind}")
        print("Secret audit failed: remove the credential or replace it with a documented placeholder.")
        return 1
    print("Secret audit passed: no recognizable live credentials found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
