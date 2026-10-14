#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$ROOT_DIR/artifacts/demo}"
mkdir -p "$OUT_DIR"

set +e
USE_MOCK_LLM=true \
MEMORY_PATH="$OUT_DIR/MEMORY.md" \
CHECKPOINT_DIR="$OUT_DIR/checkpoints" \
TELEMETRY_PATH="$OUT_DIR/telemetry/events.jsonl" \
uv run python "$ROOT_DIR/src/main.py" \
  --ticket "Demo" \
  --demo \
  --mode draft \
  --out-dir "$OUT_DIR"
status=$?
set -e

# The fixed demo intentionally contains unresolved questions, so draft mode
# exits with 2 while still producing a reviewable artifact set.
if [[ "$status" -ne 2 ]]; then
  exit "$status"
fi

echo "Demo artifact written to $OUT_DIR"
printf '%s\n' \
  "$OUT_DIR/FEATURE_SPEC.md" \
  "$OUT_DIR/FEATURE_SPEC.html" \
  "$OUT_DIR/FEATURE_CASE_STUDY.html"
