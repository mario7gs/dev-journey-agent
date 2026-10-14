#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

uv run pytest -q
uv run python scripts/security_audit.py .
uv run ruff check .
uv run mypy src config

if uv run python -c "import hatchling" >/dev/null 2>&1; then
  uv build
else
  echo "Package build skipped: hatchling is not installed in this offline environment."
  echo "CI installs the locked build backend before running uv build."
fi

uv run python - <<'PY'
from html.parser import HTMLParser
from pathlib import Path


class _Parser(HTMLParser):
    pass


for path in (Path("docs/MVP/IMPLEMENTATION_DASHBOARD.html"), Path("src/templates/case_study.html.j2")):
    _Parser().feed(path.read_text(encoding="utf-8"))
    print(f"HTML parse passed: {path}")
PY
