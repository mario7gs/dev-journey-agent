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
