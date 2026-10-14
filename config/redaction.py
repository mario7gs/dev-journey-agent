"""Best-effort redaction for persisted and exported diagnostic data."""
from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"

_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [^-]+ PRIVATE KEY-----[\s\S]+?-----END [^-]+ PRIVATE KEY-----"),
    re.compile(r"\b(?:sk-(?:proj|live)-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]{10,})\b"),
    re.compile(r"(?i)(\b(?:api[_-]?key|access[_-]?token|auth(?:orization)?|password|passwd|secret|client[_-]?secret)\b\s*[:=]\s*)([^\s,;]+)"),
    re.compile(r"(?i)(https?://)([^/\s:@]+):([^@\s]+)@"),
)
_SENSITIVE_KEYS = re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|authorization|password|passwd|secret|private[_-]?key)")


def redact_text(value: str) -> str:
    """Redact recognizable credentials while preserving surrounding context."""
    redacted = value
    for pattern in _SECRET_PATTERNS:
        if pattern.groups >= 2 and "https?" not in pattern.pattern:
            redacted = pattern.sub(lambda match: f"{match.group(1)}{REDACTED}", redacted)
        elif "https?" in pattern.pattern:
            redacted = pattern.sub(lambda match: f"{match.group(1)}{REDACTED}:{REDACTED}@", redacted)
        else:
            redacted = pattern.sub(REDACTED, redacted)
    return redacted


def redact_value(value: Any) -> Any:
    """Recursively redact strings and values stored under sensitive keys."""
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        result: dict[Any, Any] = {}
        for key, item in value.items():
            result[key] = REDACTED if _SENSITIVE_KEYS.search(str(key)) else redact_value(item)
        return result
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    return value
