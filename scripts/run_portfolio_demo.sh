#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$ROOT_DIR/artifacts/demo}"
APPROVED_DIR="$OUT_DIR/approved"
NEEDS_INPUT_DIR="$OUT_DIR/needs-input"

mkdir -p "$APPROVED_DIR" "$NEEDS_INPUT_DIR"

run_case() {
  local name="$1"
  local expected_exit="$2"
  local ticket="$3"
  local mode="$4"
  shift 4
  local case_dir="$OUT_DIR/$name"
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
    --ticket "$ticket" \
    --mode "$mode" \
    --out-dir "$case_dir" \
    --status-file "$status_file" \
    "$@" >"$case_dir/console.log" 2>&1
  actual_exit=$?
  set -e

  if [[ "$actual_exit" -ne "$expected_exit" ]]; then
    echo "Scenario $name returned $actual_exit; expected $expected_exit." >&2
    cat "$case_dir/console.log" >&2
    return 1
  fi

  [[ -s "$status_file" ]]
  [[ -s "$case_dir/FEATURE_SPEC.md" ]]
  [[ -s "$case_dir/FEATURE_SPEC.html" ]]
  [[ -s "$case_dir/MEMORY.md" ]]
  [[ -s "$case_dir/telemetry/events.jsonl" ]]
  [[ -d "$case_dir/checkpoints" ]]
}

run_case "approved" 0 "Add a health-check endpoint" blocking
run_case "needs-input" 2 "Demo" blocking --demo

for case_dir in "$APPROVED_DIR" "$NEEDS_INPUT_DIR"; do
  uv run python "$ROOT_DIR/scripts/cost_report.py" \
    --input "$case_dir/telemetry/events.jsonl" \
    --output "$case_dir/cost-summary.json" \
    --max-run-cost-usd 1.00 \
    --max-run-tokens 50000 \
    --max-bytes 500000 \
    --retention-days 14 >"$case_dir/cost-report.log"
done

security_output="$(uv run python "$ROOT_DIR/scripts/security_audit.py" "$ROOT_DIR" 2>&1)"
printf '%s\n' "$security_output" >"$OUT_DIR/security-audit.txt"
if ! grep -q "Secret audit passed" "$OUT_DIR/security-audit.txt"; then
  cat "$OUT_DIR/security-audit.txt" >&2
  exit 1
fi

python3 - "$OUT_DIR" "$OUT_DIR/DEMO_SUMMARY.html" "$ROOT_DIR" <<'PY'
from __future__ import annotations

import base64
import html
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
summary_path = Path(sys.argv[2]).resolve()
repo_root = Path(sys.argv[3]).resolve()
logo_path = repo_root / "src" / "templates" / "assets" / "dj-mark.png"
logo_data = base64.b64encode(logo_path.read_bytes()).decode("ascii")

scenarios = (
    ("Approved plan", root / "approved", "approved", "success", 0),
    ("Needs-input safety gate", root / "needs-input", "needs_input", "failure", 2),
)

def link_rows(directory: Path) -> str:
    rows = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.name == "console.log":
            continue
        relative = path.relative_to(root).as_posix()
        rows.append(
            f'<li><a href="{html.escape(relative)}">{html.escape(relative)}</a></li>'
        )
    return "\n".join(rows)

cards = []
for title, directory, expected_status, expected_github, expected_exit in scenarios:
    payload = json.loads((directory / "run-status.json").read_text(encoding="utf-8"))
    actual_status = payload.get("status", "unknown")
    actual_github = payload.get("github_status", "unknown")
    actual_exit = payload.get("exit_code", "unknown")
    cards.append(
        f"""
        <article class="card">
          <p class="eyebrow">Scenario</p>
          <h2>{html.escape(title)}</h2>
          <p><span class="badge">status: {html.escape(str(actual_status))}</span>
             <span class="badge">GitHub signal: {html.escape(str(actual_github))}</span>
             <span class="badge">exit: {html.escape(str(actual_exit))}</span></p>
          <p>Expected: <code>{html.escape(expected_status)}</code> /
             <code>{html.escape(expected_github)}</code> /
             <code>{expected_exit}</code></p>
          <details><summary>Generated evidence</summary><ul>{link_rows(directory)}</ul></details>
        </article>
        """
    )

summary_html = (
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dev Journey Agent · Portfolio demo summary</title>
  <style>
    :root { --ink:#0b1220; --ink-soft:#1e293b; --slate:#475569; --muted:#64748b; --mist:#f4f7fb; --paper:#fff; --indigo:#3157d5; --indigo-soft:#e8edff; --teal:#0f8b8d; --teal-soft:#ddf3f2; --gold:#c89b3c; --line:#d8e0ec; }
    * { box-sizing:border-box; } html { scroll-behavior:smooth; } body { margin:0; color:var(--ink); background:var(--mist); font:16px/1.55 Inter,system-ui,sans-serif; }
    header.site-header { position:sticky; top:0; z-index:20; border-bottom:1px solid #ffffff24; box-shadow:0 8px 24px #0b122029; background:linear-gradient(135deg,var(--ink),#163f52); }
    .site-header-inner { max-width:1200px; margin:0 auto; padding:.78rem 1rem; display:flex; flex-direction:column; align-items:flex-start; gap:1rem; }
    .site-brand { display:flex; align-items:center; gap:.7rem; color:var(--paper); text-decoration:none; min-width:max-content; }
    .site-brand img { width:2.8rem; height:2.8rem; display:block; } .site-brand span span { display:block; }
    .brand-name { font-size:.74rem; font-weight:800; letter-spacing:.16em; line-height:1.2; } .brand-subtitle { margin-top:.2rem; color:#ffffffb0; font-size:.58rem; letter-spacing:.1em; }
    .site-nav { display:flex; align-items:center; justify-content:flex-start; gap:.35rem; flex-wrap:wrap; width:100%; } .site-nav a { color:var(--paper); text-decoration:none; padding:.38rem .62rem; border:1px solid #ffffff40; border-radius:999px; font-size:.76rem; font-weight:750; line-height:1.1; } .site-nav a:hover,.site-nav a:focus-visible { background:#ffffff24; border-color:#ffffff8c; }
    .hero { padding:2.4rem max(1.2rem,calc((100vw - 960px)/2)); color:white; background:linear-gradient(135deg,var(--ink),#163f52); }
    main { max-width:960px; margin:0 auto; padding:1.2rem; } h1 { margin:0; max-width:720px; font-size:clamp(2rem,5vw,3.5rem); line-height:1.05; }
    h2 { margin:.2rem 0 .7rem; } .lead { max-width:700px; color:#dce7ff; } .eyebrow { color:#55c6c4; font-size:.72rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
    .grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; } .card { margin:1rem 0; padding:1.2rem; border:1px solid var(--line); border-radius:14px; background:var(--paper); box-shadow:0 8px 24px #0f172a0b; }
    .badge { display:inline-block; margin:.15rem .25rem .15rem 0; padding:.2rem .55rem; border-radius:999px; color:#294aa7; background:#e8edff; font-size:.8rem; font-weight:700; }
    code { padding:.1rem .3rem; border-radius:4px; color:#294aa7; background:#e8edff; } a { color:var(--indigo); } li + li { margin-top:.25rem; }
    .callout { padding:.9rem 1rem; border-left:3px solid var(--teal); background:#ddf3f2; } footer { color:var(--muted); font-size:.85rem; }
    section[id] { scroll-margin-top:5.8rem; } @media (max-width:720px) { .site-header-inner { align-items:flex-start; flex-direction:column; } .site-nav { justify-content:flex-start; } .grid { grid-template-columns:1fr; } }
    @media print { .site-header { display:none; } }
  </style>
</head>
<body>
  <header class="site-header" aria-label="Demo navigation"><div class="site-header-inner"><a class="site-brand" href="#overview" aria-label="Dev Journey Agent overview"><img src="data:image/png;base64,__LOGO_DATA__" alt="Dev Journey Agent mark"><span><span class="brand-name">DEV JOURNEY</span><span class="brand-subtitle">AGENT · FEATURE PLANNING COPILOT</span></span></a><nav class="site-nav" aria-label="Demo sections"><a href="#overview">Overview</a><a href="#scenarios">Scenarios</a><a href="#evidence">Evidence</a></nav></div></header>
  <section class="hero" id="overview"><p class="eyebrow">Portfolio evidence</p><h1>Two outcomes, one safe planning pipeline.</h1><p class="lead">A deterministic, credential-free demonstration of the approved path and the needs-input safety gate.</p></section>
  <main>
    <p class="callout"><strong>Validation:</strong> both expected scenarios completed, generated their evidence bundles, passed the security audit, and stayed within the configured mock budget.</p>
    <section class="grid" id="scenarios">"""
    + "\n".join(cards)
    + """</section>
    <article class="card" id="evidence"><h2>Shared evidence</h2><ul>
      <li><a href="security-audit.txt">security-audit.txt</a> — source-tree secret audit result</li>
      <li><a href="approved/cost-summary.json">approved/cost-summary.json</a> — approved scenario budget evidence</li>
      <li><a href="needs-input/cost-summary.json">needs-input/cost-summary.json</a> — safety-gate budget evidence</li>
    </ul></article>
    <footer>Generated by <code>scripts/run_portfolio_demo.sh</code>. MCP and provider integrations are intentionally outside this milestone.</footer>
  </main>
</body>
</html>
"""
)
summary_path.write_text(summary_html.replace("__LOGO_DATA__", logo_data), encoding="utf-8")
PY

echo "Portfolio demo passed. Summary: $OUT_DIR/DEMO_SUMMARY.html"
