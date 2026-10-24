# Dev Journey Agent — Implementation Roadmap

> Implementation record for the completed delivery sequence. It documents the
> intended order and the evidence for each track.

## Current baseline

The project currently has an end-to-end pipeline covering:

- Step 0 refinement with read-only repository context.
- Blocking mode as the default and explicit draft mode.
- Deterministic mock execution plus the configured real-model fallback chain.
- Output contracts, Definition of Done, PRD/TRD, security assessment, TDD
  roadmap, critic validation, traceability IDs, and Markdown/HTML export.
- Print-safe PDF export and a concise HTML/PDF case-study presentation view.
- Optional stage telemetry with local run-cost evidence and Phoenix span export.
- Shared portfolio-oriented visual language using the approved PNG logo.

The canonical visual guide is [`BRAND_GUIDELINES.html`](../BRAND_GUIDELINES.html).
The current delivery snapshot is [`IMPLEMENTATION_DASHBOARD.html`](IMPLEMENTATION_DASHBOARD.html).

## Queued implementation order

### 1. Durable checkpoints and resumable execution — implemented

**Purpose:** prevent repeated LLM calls and lost work when a run is interrupted.

**Implementation sequence:**

1. Define a versioned checkpoint envelope containing `run_id`, pipeline stage,
   mode, timestamp, schema version, traceability data, and validated stage
   output.
2. Store one atomic checkpoint after every completed stage, without replacing
   the append-only human audit history in `MEMORY.md`.
3. Add a resume command such as `--resume <run_id>`.
4. Validate checkpoint compatibility before resuming; reject corrupted,
   incomplete, or incompatible checkpoints clearly.
5. Resume only from the last completed stage and preserve blocking/draft
   semantics.
6. Ensure deterministic IDs and prior validated outputs are reused rather than
   regenerated.

**Delivered:** versioned JSON checkpoint envelopes are atomically persisted
under `.dev-journey/checkpoints/<run-id>/`; `--resume <run-id>` validates and
continues from the last completed stage. Checkpoints retain validated state,
stage output, mode, runtime configuration, and stable traceability IDs while
`MEMORY.md` remains append-only. Tests cover corrupt/tampered checkpoints,
interruption/resume, and preservation of the blocking gate.

**Acceptance criteria:**

- An interrupted run can resume from its last completed stage.
- Completed LLM stages are not called again during resume.
- Blocking mode cannot be bypassed by resuming.
- Draft mode remains explicitly provisional.
- Checkpoint writes are atomic and recoverable.
- Resume and interruption behavior is covered by automated tests.

### 2. Observability and run-cost evidence — implemented

Start only after checkpoint/resume behavior is stable.

- Integrate the existing Phoenix configuration with stage-level tracing.
- Record latency, model/fallback selection, token/cost metadata when available,
  and blocking reasons.
- Correlate traces with `run_id` and traceability IDs.
- Keep observability optional and disabled by default.

**Delivered:** the optional recorder emits one JSONL event per pipeline stage,
including `run_id`, mode, traceability IDs, latency, blocking reasons, model
fallback order, token usage, and provider cost metadata. Resume and gate events
are also recorded. When `arize-phoenix-otel` is installed, the same stage
boundaries are exported as Phoenix OpenTelemetry spans; missing SDKs and
collector failures remain non-fatal.

### 3. Portfolio-grade PDF and presentation export — implemented

Start only after the operational pipeline is resumable and observable.

- Render the existing stakeholder HTML to print-safe PDF.
- Preserve the canonical `BRAND_GUIDELINES.html` design system and approved PNG
  logo.
- Add a concise portfolio case-study presentation view.
- Verify visual output, page breaks, accessibility text, and asset embedding.

**Delivered:** `write_docs(..., include_pdf=True, include_presentation=True)` now
renders the stakeholder report and case-study deck through a local headless
Chromium browser when available. The presentation uses semantic headings,
accessible image text, embedded PNG branding, 16:9 print pages, and explicit
status/evidence content. Browser failures remain non-fatal to the Markdown and
HTML export and are surfaced as CLI warnings so a restricted environment can
still complete the run.

**Acceptance evidence:** renderer command and missing-browser behavior are
unit-tested; presentation sections, counts, semantic labels, and embedded
assets are covered by tests; the stakeholder template carries A4 print rules
and page-break-safe cards.

### 4. Release and portfolio polish — implemented

- Add CI checks for tests, linting, packaging, and generated documentation.
- Add a reproducible demo command and sample run artifact.
- Document configuration, privacy boundaries, failure recovery, and cost
  controls.
- Review the README as a portfolio entry point after the functional work is
  complete.

**Delivered:** the repository now has a CI quality workflow covering tests,
linting, type checks, HTML validation, and package builds. `scripts/verify.sh`
mirrors those checks locally, while `scripts/run_demo.sh` produces a
deterministic draft artifact bundle from the fixed mock fixture. Configuration,
privacy boundaries, failure recovery, and cost controls are documented in
`docs/OPERATIONS.md` and linked from the README.

### 5. Portfolio quick-win demo and artifact index — implemented

**Purpose:** make the project's value obvious in one credential-free command.

**Implementation sequence:**

1. Add `scripts/run_portfolio_demo.sh`, a wrapper that runs an approved mock
   scenario and an intentionally blocked/draft scenario.
2. Write the two reviewable bundles under
   `artifacts/demo/approved/` and `artifacts/demo/needs-input/`.
3. Generate a small `DEMO_SUMMARY.html` index showing statuses, outputs,
   checkpoints, telemetry, budgets, and the security-audit result.
4. Treat the expected provisional exit code `2` as an internal result for the
   needs-input scenario while requiring the wrapper itself to exit `0` only
   when both scenarios and artifact assertions pass.
5. Update the README and demo documentation with a 60-second quickstart and
   expected outputs.
6. Refresh portfolio evidence counts and verification dates.

**Acceptance criteria:**

- Runs without API keys or GitHub credentials.
- The approved scenario reports `approved`/`success` and exit `0`.
- The needs-input scenario reports `needs_input` or `draft` and preserves
  provisional exit `2` internally.
- The summary links to Markdown, HTML, PDF, case-study, checkpoint,
  telemetry, cost, and security evidence where produced.
- Automated verification covers the wrapper and generated index.

**Delivered:** `scripts/run_portfolio_demo.sh` now runs an approved health-check
scenario and an intentionally needs-input demo scenario without credentials.
It preserves the internal exit-code distinction, writes separate evidence
bundles, generates `DEMO_SUMMARY.html`, runs the security audit, and produces
redacted cost summaries for both cases. Focused subprocess verification covers
the wrapper and the generated index. The stakeholder report, case-study
presentation, and portfolio summary now use the approved v19 mark and canonical
brand tokens; regression checks reject the superseded palette.

### 6. Approved portfolio artifact contract — locked

The following artifact presentation is now part of the approved portfolio
baseline and should not change incidentally:

- The v19 logo and full lockup are used consistently across the stakeholder
  report, case-study presentation, and `DEMO_SUMMARY.html`.
- The lockup reads `DEV JOURNEY` with `AGENT · FEATURE PLANNING COPILOT` below
  it, using the canonical brand tokens and typography.
- Each artifact has a sticky navigation bar with section buttons that target
  semantic anchors in the document; the navigation is hidden for print output.
- Generated artifacts remain self-contained, reviewable, and linked to their
  evidence bundles.

This is the visual acceptance baseline for the portfolio MVP. Any future
visual change requires an explicit design decision and an update to the brand
guidelines, artifact tests, and generated evidence.

**Evidence:** generated approved and needs-input bundles, `DEMO_SUMMARY.html`,
the shared templates/CSS, focused navigation assertions, and the full
83-test release verification.

### 7. Provider-neutral local skill wrapper — implemented

**Purpose:** make the approved CLI workflow easy to invoke from a local
agentic tool without coupling the core pipeline to one provider.

**Implementation scope:**

1. Define a small provider-neutral skill contract for ticket input, repository
   reference, branch, mode, output directory, and resume ID.
2. Add a local wrapper that delegates to the existing CLI and returns concise
   status plus artifact paths.
3. Preserve blocking/draft semantics, exit codes, checkpoints, telemetry, and
   the approved artifact contract.
4. Add a mock-only verification path and documentation showing invocation from
   a generic local skill runner.
5. Keep the CLI and GitHub Action as the core supported surfaces.

**Explicitly out of scope:** MCP, Codex/Claude/OpenCode/Gemini-specific
adapters, hosted services, and automatic issue/PR integrations. Those remain
future enhancements.

**Delivered:** `scripts/run_local_skill.py` accepts a versioned JSON request
from stdin or a request file, delegates to the existing CLI without a shell,
and emits structured status, exit code, run ID, artifact paths, and bundle
location. Each run isolates memory, checkpoints, telemetry, and redacted
console output under its artifact directory. Focused tests cover approved
execution, invalid input, needs-input exit preservation, secret-safe logs, and
resume-mode handling.

### 8. Possible future integrations — deferred

The CLI and GitHub Action remain the core supported surfaces while the
portfolio demo is polished. Possible later enhancements include:

- an MCP server exposing plan, resume, status, and artifact tools;
- a hosted HTTPS MCP service with authentication;
- automatic issue/PR triggers and richer dashboards; and
- provider-specific chat adapters, including Gemini-oriented entry points.

These are optional adapters, not prerequisites for the portfolio MVP. They are
explicitly deferred until the credential-free demo is easy to run and review.

### 9. Delivery-hardening split — Part 2 implemented

The final delivery-hardening work is intentionally split so the portfolio
project stays useful, credible, and small enough to review.

**Part 1 — engineering release gate (completed this session):**

- rerun the credential-free approved and needs-input portfolio scenarios;
- refresh the separate artifact bundles and `DEMO_SUMMARY.html` evidence index;
- verify the frozen logo, palette, lockup, sticky navigation, and print-safe
  artifact contract;
- run the full release checks and record the remaining environment-dependent
  PDF/build limitations.

**Part 2 — visual/publication handoff (implemented this session):**

- attempt final PDF visual QA and record the renderer limitation honestly;
- attempt the package build and record the offline Hatchling limitation;
- refresh evidence and add the publication assets; and
- create a concise, polished slide/case-study package plus LinkedIn- and
  GitHub-ready presentation assets or guidance.

The final portfolio package is available as the self-contained HTML deck at
`artifacts/portfolio/DEV_JOURNEY_PORTFOLIO_DECK.html`, the recruiter-facing
carousel at `artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf`, and
the plain-language positioning in `README.md`. The CLI and GitHub Action stay
the core supported surfaces; MCP, hosted services, provider-specific adapters,
and automatic issue/PR integrations remain deferred. PDF export remains an
optional local capability: this sandbox's Chrome and Firefox binaries both
crash before rendering, so the generated HTML remains the authoritative visual
review surface until a working renderer is available.

### 10. Real repository validation — completed

The first external validation loop is recorded in
[`REAL_TEST_CASE_REPORT.md`](REAL_TEST_CASE_REPORT.md). The operator's
read-only run against `mario7gs/dev-journey-agent@main` approved the health-check
ticket with exit code `0` and generated the stakeholder and portfolio exports.
The complementary deterministic ambiguous-ticket run returned `needs_input`
with exit code `2`, naming the missing search scope/data source. No source,
issue, pull request, merge, or deployment mutation occurred, and no credential
value is stored in the report.

### 11. Reproducible real-test runner — implemented

`scripts/run_real_test_case.sh` now makes the external validation repeatable.
It requires a pre-exported `GITHUB_TOKEN`, runs the approved health-check case
against the selected repository and branch, then unsets the credential for the
credential-free needs-input case. It validates both machine-readable status
payloads and key artifact files while keeping the CLI/GitHub Action as the
supported product surfaces. A focused test verifies the missing-token guard.

### 12. Portfolio handoff packet — ready

The reviewer-first route is captured in
[`PORTFOLIO_HANDOFF.md`](PORTFOLIO_HANDOFF.md). It connects the visual deck,
credential-free demo, real validation report, operations notes, claim-to-
evidence map, release gate, and explicit deferred scope. This closes the
portfolio delivery path while keeping PDF visual QA and `uv build` as the only
environment-dependent follow-ups.

### 13. Public repository and HR-friendly presentation polish — implemented

The GitHub entry point now explains the product in plain language and links to
the reviewer-first handoff. Added lightweight `CONTRIBUTING.md` and
`SECURITY.md` guidance. The portfolio deck, recruiter-facing carousel, and
README now lead with the human problem, explain the workflow without assuming
programming knowledge, and preserve technical evidence for engineering
readers.

## Next-session starting checklist

- [x] Read this roadmap and confirm the checkpoint/resume scope.
- [x] Run `uv run pytest` and `uv run ruff check .`.
- [x] Inspect the current state and memory modules.
- [x] Implement the checkpoint envelope and atomic persistence first.
- [x] Add interruption/resume tests before adding the CLI flag.
- [x] Update this roadmap with the completed result.
- [x] Implement portfolio PDF and case-study presentation exports.
- [x] Add CI and local release verification checks.
- [x] Add a reproducible demo artifact workflow and operations documentation.
- [x] Implement the credential-free two-scenario portfolio demo and artifact index.
- [x] Add the one-command quickstart and generated evidence assertions.
- [x] Refresh the portfolio-facing evidence after the demo is verified.
- [x] Lock the approved artifact layout, navigation, logo, and palette contract.
- [x] Implement the provider-neutral local skill wrapper.
- [x] Complete Part 1 of delivery hardening and refresh portfolio evidence.
- [x] Complete Part 2 publication assets and LinkedIn/GitHub support materials.
- [x] Validate one approved real-repository run and one needs-input safety case;
  record the sanitized evidence in `REAL_TEST_CASE_REPORT.md`.
- [x] Add the repeatable `scripts/run_real_test_case.sh` validation runner with
  a pre-exported-token guard.
- [ ] Re-run PDF visual QA and `uv build` in an environment with working
  Chromium and network access to the locked Hatchling backend.

## Queue rules

- Keep blocking mode as the default.
- Do not silently infer missing user requirements.
- Keep PDF generation local and optional; do not add a network or runtime download dependency.
- Keep release checks reproducible with the pinned `uv.lock` environment.
- Treat `docs/BRAND_GUIDELINES.html` as the only canonical brand-guide file.
- Treat the approved artifact contract above as frozen until an explicit design
  decision changes it.
- Keep `MEMORY.md` append-only; use versioned run state for machine resume.
- Keep the next demo deterministic, credential-free, and reviewable in under a
  minute.
- Treat MCP, chat-provider adapters, hosted services, and automatic triggers as
  deferred enhancements rather than prerequisites for the local skill-wrapper
  milestone.
