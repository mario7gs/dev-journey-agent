#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$(mktemp -d -t dev-journey-real-test.XXXXXX)}"
REPO="${2:-mario7gs/dev-journey-agent}"
BRANCH="${3:-main}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN must already be exported; the runner never prompts or stores it." >&2
  exit 1
fi

mkdir -p "$OUT_DIR/approved" "$OUT_DIR/needs-input"

validate_status() {
  local status_file="$1"
  local expected_status="$2"
  local expected_github="$3"
  local expected_exit="$4"

  python3 - "$status_file" "$expected_status" "$expected_github" "$expected_exit" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

status_path = Path(sys.argv[1])
expected = {
    "status": sys.argv[2],
    "github_status": sys.argv[3],
    "exit_code": int(sys.argv[4]),
}
payload = json.loads(status_path.read_text(encoding="utf-8"))
actual = {key: payload.get(key) for key in expected}
if actual != expected:
    raise SystemExit(f"Unexpected status payload: {actual!r}; expected {expected!r}")
PY
}

run_approved() {
  local case_dir="$OUT_DIR/approved"
  local status_file="$case_dir/run-status.json"
  local actual_exit

  set +e
  USE_MOCK_LLM=true \
  PHOENIX_ENABLED=true \
  TELEMETRY_RETENTION_DAYS=14 \
  TELEMETRY_MAX_BYTES=500000 \
  MAX_RUN_COST_USD=1.00 \
  MAX_RUN_TOKENS=50000 \
  MEMORY_PATH="$case_dir/MEMORY.md" \
  CHECKPOINT_DIR="$case_dir/checkpoints" \
  TELEMETRY_PATH="$case_dir/telemetry/events.jsonl" \
  uv run python "$ROOT_DIR/src/main.py" \
    --ticket "Add a health-check endpoint" \
    --repo "$REPO" \
    --branch "$BRANCH" \
    --mode blocking \
    --out-dir "$case_dir" \
    --status-file "$status_file" >"$case_dir/console.log" 2>&1
  actual_exit=$?
  set -e

  if [[ "$actual_exit" -ne 0 ]]; then
    cat "$case_dir/console.log" >&2
    return 1
  fi
  validate_status "$status_file" approved success 0
  [[ -s "$case_dir/FEATURE_SPEC.md" ]]
  [[ -s "$case_dir/FEATURE_SPEC.html" ]]
  [[ -s "$case_dir/MEMORY.md" ]]
  [[ -d "$case_dir/checkpoints" ]]
}

run_needs_input() {
  local case_dir="$OUT_DIR/needs-input"
  local status_file="$case_dir/run-status.json"
  local actual_exit

  set +e
  env -u GITHUB_TOKEN \
  USE_MOCK_LLM=true \
  PHOENIX_ENABLED=true \
  TELEMETRY_RETENTION_DAYS=14 \
  TELEMETRY_MAX_BYTES=500000 \
  MAX_RUN_COST_USD=1.00 \
  MAX_RUN_TOKENS=50000 \
  MEMORY_PATH="$case_dir/MEMORY.md" \
  CHECKPOINT_DIR="$case_dir/checkpoints" \
  TELEMETRY_PATH="$case_dir/telemetry/events.jsonl" \
  uv run python "$ROOT_DIR/src/main.py" \
    --ticket "Improve the application" \
    --mode blocking \
    --demo \
    --out-dir "$case_dir" \
    --status-file "$status_file" >"$case_dir/console.log" 2>&1
  actual_exit=$?
  set -e

  if [[ "$actual_exit" -ne 2 ]]; then
    cat "$case_dir/console.log" >&2
    return 1
  fi
  validate_status "$status_file" needs_input failure 2
  [[ -s "$case_dir/FEATURE_SPEC.md" ]]
  [[ -s "$case_dir/FEATURE_SPEC.html" ]]
  [[ -s "$case_dir/MEMORY.md" ]]
  [[ -d "$case_dir/checkpoints" ]]
}

run_approved
run_needs_input

echo "Real test case passed."
echo "Approved evidence: $OUT_DIR/approved"
echo "Needs-input evidence: $OUT_DIR/needs-input"
