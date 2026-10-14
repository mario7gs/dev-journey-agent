"""Secure-by-Default guardrails injected into Step 1 DoD."""
from __future__ import annotations

MAX_FILE_BYTES = 1_000_000
MAX_TICKET_CHARS = 10_000
ALLOWED_UPLOAD_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".gif", ".pdf"})
BLOCKED_PATTERNS = (
    "sk-proj-",
    "sk-live-",
    "aws_secret",
    "password=",
    "__pycache__",
)

DEFAULT_DOD_SECURITY_ITEMS = (
    "No hardcoded secrets; all secrets via environment variables",
    "All user inputs validated with schemas before processing",
    "Parameterized queries only; no SQL string concatenation",
    "User-provided HTML sanitized; no unvalidated dynamic rendering",
    "AuthN/AuthZ checks before sensitive operations",
    "Generic error messages to users; details server-side only",
)

SKIP_DIRS = frozenset(
    {"__pycache__", ".git", ".venv", "node_modules", "vendor", ".tox", "dist", "build"}
)
SKIP_SUFFIXES = (".pyc", ".pyo", ".min.js", ".map")


def sanitize_input(text: str, max_chars: int = MAX_TICKET_CHARS) -> str:
    """Trim + truncate user text. Never raises on normal input."""
    cleaned = text.strip().replace("\x00", "")
    return cleaned[:max_chars]


def is_blocked_text(text: str) -> bool:
    lowered = text.lower()
    return any(p.lower() in lowered for p in BLOCKED_PATTERNS)


def validate_upload_meta(filename: str, size_bytes: int, max_bytes: int = 5 * 1024 * 1024) -> None:
    """Raise ValueError on invalid upload metadata."""
    import os

    if size_bytes > max_bytes:
        raise ValueError(f"File too large (max {max_bytes} bytes)")
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(f"Invalid file extension: {ext}")
