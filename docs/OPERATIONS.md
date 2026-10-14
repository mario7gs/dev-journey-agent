# Operations and release notes

## Configuration and privacy

Mock execution is the default and makes no provider calls. Real execution can
use the configured LiteLLM model chain and requires credentials supplied
through environment variables. Secrets are read from process configuration and
are never written to generated Markdown, HTML, presentation files, checkpoints,
or telemetry events.

Repository context is read-only. Checkpoints, memory, and optional telemetry
are written locally under the configured paths; add those paths to deployment
storage policy before sharing an artifact bundle.

Persisted checkpoint state, audit summaries, telemetry JSONL, and Phoenix span
attributes pass through credential redaction before they are written or sent.
Set `MAX_RUN_COST_USD` and `MAX_RUN_TOKENS` to enforce per-run provider limits;
zero disables the corresponding limit. `TELEMETRY_MAX_BYTES` bounds local JSONL
growth, while the GitHub workflow stores redacted checkpoints, memory, and
telemetry under the planning artifact with a 14-day retention policy. The CI
secret audit rejects recognizable private keys, provider tokens, AWS access
keys, and high-entropy credential assignments in source-controlled text.

## Failure recovery

The pipeline writes an atomic checkpoint after each completed stage. If a run is
interrupted, resume it with `--resume <run-id>` using the same model mode and
configuration. Completed model stages are reused.

Blocking mode stops when refinement or critic evidence is incomplete. Draft mode
continues for exploration but exits with a provisional status. PDF rendering is
optional at runtime: if a local Chromium-compatible browser is unavailable, the
Markdown, stakeholder HTML, and case-study HTML remain available and the CLI
prints the renderer warning.

## Cost controls

- Keep `USE_MOCK_LLM=true` for tests, demos, and local UI review.
- Set `LLM_TIMEOUT_SECONDS` and repository context budgets before real runs.
- Enable telemetry only when latency, token, or provider-cost evidence is needed.
- Review local JSONL telemetry before exporting it outside the development environment.
- Generate a redacted usage report with `scripts/cost_report.py`; it aggregates
  stage usage and reports `within_budget`, `exceeded`, or `not_configured`.
- The workflow writes `cost-summary.json` and the same report to the Actions
  job summary. A configured token or cost overage fails the planning job.

## Retention and purge

GitHub planning artifacts expire automatically after 14 days. Local checkpoint
runs are retained according to `TELEMETRY_RETENTION_DAYS` (14 days by default)
when an operator runs the explicit maintenance command:

```bash
uv run python scripts/prune_artifacts.py \
  --root .dev-journey/checkpoints \
  --retention-days 14
```

The command is dry-run by default and only inspects immediate child run
directories. Add `--apply` after reviewing the candidates. This keeps purge
scope explicit and avoids deleting unrelated repository data.

## Release checks

The CI workflow runs the same checks locally with:

```bash
bash scripts/verify.sh
```

## GitHub review signals

The manual `Dev Journey plan` workflow writes `artifacts/plan/run-status.json`
and publishes the `dev-journey/plan` commit status. Approved plans are marked
successful, draft plans are pending human review, and needs-input plans are
marked failed until their clarification questions are resolved. Issue and pull
request comments are opt-in inputs and require the workflow's issue-write
permission. The workflow performs no source-code edits, merges, or deployments.

The deterministic portfolio fixture is generated with:

```bash
bash scripts/run_demo.sh
```
