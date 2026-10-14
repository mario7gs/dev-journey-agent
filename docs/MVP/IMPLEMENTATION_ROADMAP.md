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

## Queue rules

- Keep blocking mode as the default.
- Do not silently infer missing user requirements.
- Keep PDF generation local and optional; do not add a network or runtime download dependency.
- Keep release checks reproducible with the pinned `uv.lock` environment.
- Treat `docs/BRAND_GUIDELINES.html` as the only canonical brand-guide file.
- Keep `MEMORY.md` append-only; use versioned run state for machine resume.
