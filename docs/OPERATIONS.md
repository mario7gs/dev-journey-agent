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

## Real test-case evidence

The first end-to-end external validation is recorded in
[`docs/MVP/REAL_TEST_CASE_REPORT.md`](MVP/REAL_TEST_CASE_REPORT.md). It covers
one read-only approved run against `mario7gs/dev-journey-agent@main` and one
credential-free ambiguous-ticket run that correctly stops with `needs_input`
and exit code `2`.

The real-repository case used the deterministic mock model, so it produced no
provider cost. Keep the GitHub credential in the local process environment
only; do not place it in a command, source file, checkpoint, telemetry event,
or generated artifact. Prefer a fine-grained read-only token scoped to the
target repository for future manual validation. The agent performs no source,
issue, pull-request, merge, or deployment mutation during this workflow.

For repeatable validation, use the repository runner after exporting the token
locally:

```bash
export GITHUB_TOKEN
bash scripts/run_real_test_case.sh /tmp/dev-journey-real-test
```

It validates the approved real-repository outcome and the credential-free
needs-input outcome separately. The runner never prompts for, prints, or
persists the token and fails before creating artifacts when the variable is
missing.

## Delivery-hardening handoff

Part 1 of the delivery-hardening stage is complete: the credential-free
approved and needs-input scenarios were rerun, their separate bundles and
`DEMO_SUMMARY.html` evidence index were refreshed, and the frozen branded HTML
contract was verified. The release suite is green, including tests, secret
audit, type checking, and HTML parsing.

Part 2 is implemented: it adds the six-section HTML portfolio deck at
`artifacts/portfolio/DEV_JOURNEY_PORTFOLIO_DECK.html` and the publication kit at
`docs/PORTFOLIO_PUBLICATION_KIT.md`, including LinkedIn copy, a GitHub README
insert, screenshot captions, a walkthrough, and a claim-to-evidence map.

PDF visual QA and the package build were attempted. Chrome and Firefox both
crash before rendering in the current sandbox, and `uv build` cannot fetch the
locked Hatchling backend without network access. Keep those as explicit release
follow-ups in a normal developer environment. These limitations do not affect
the authoritative HTML artifacts, CLI, or GitHub Action.

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

## Portfolio demo path

`scripts/run_demo.sh` remains the deterministic draft fixture. The portfolio
quick-win is now available through `scripts/run_portfolio_demo.sh`: it runs
approved and needs-input scenarios and generates a linked
`DEMO_SUMMARY.html` artifact index. The wrapper returns success only when both
expected outcomes and their evidence files are present.

This portfolio validation path stays CLI-first and credential-free. MCP,
provider-specific chat adapters, hosted services, and automatic issue/PR
triggers are deferred enhancements and are not operational prerequisites.
Generated HTML surfaces embed the approved v19 mark and use the shared brand
tokens; the release checks also guard against the superseded presentation
palette. The stakeholder report, case study, and `DEMO_SUMMARY.html` are the
approved portfolio artifacts: their logo lockup and sticky section navigation
are a frozen presentation contract. Change that contract only through an
explicit design decision, followed by regenerated evidence and verification.

## Local skill wrapper

The provider-neutral local skill wrapper is implemented in
`scripts/run_local_skill.py`. It exposes ticket/repository/mode/resume inputs
and returns status plus artifact paths while preserving checkpoints, exit
codes, telemetry, and the frozen artifact contract. MCP, provider-specific
adapters, hosted services, and automatic issue/PR integrations remain
deferred.

## Portfolio handoff

The reviewer-first route is documented in
[`docs/MVP/PORTFOLIO_HANDOFF.md`](MVP/PORTFOLIO_HANDOFF.md). It points to the
visual deck, credential-free demo, real validation report, operational
boundaries, and release gate without requiring provider-specific integrations.
