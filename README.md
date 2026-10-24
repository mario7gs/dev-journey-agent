# Dev-Journey-Agent

Portfolio AI agent for turning a vague ticket and an optional GitHub repository
into a traceable implementation plan: refinement → DoD/contracts → PRD/TRD →
TDD roadmap → stakeholder export.

## Status: Portfolio quick-win implemented

- ✅ Blocking mode is the default: unresolved Step 0 questions stop approval
- ✅ Draft mode continues for exploration but cannot be marked approved
- ✅ Read-only GitHub context is assembled before refinement
- ✅ Mock mode is deterministic and ticket-aware; `--demo` is an explicit fixture
- ✅ Real mode uses LiteLLM primary → fallback → local model chain
- ✅ Stable traceability IDs connect requirements, contracts, acceptance criteria, tests, security checks, and implementation steps
- ✅ Critic validates cross-stage references before approval
- ✅ Shared visual identity and brand tokens for HTML, PDF, and portfolio presentation surfaces
- ✅ Brand compliance checks for the approved v19 logo, canonical palette, and generated portfolio artifacts
- ✅ Frozen portfolio artifact contract: official lockup, sticky section navigation, and print-safe behavior
- ✅ Provider-neutral local skill wrapper with structured JSON input/output and isolated run bundles
- ✅ Portfolio exports: print-safe `FEATURE_SPEC.pdf`, `FEATURE_CASE_STUDY.html`, and presentation PDF
- ✅ Release polish: CI quality gates, reproducible demo script, and operations/cost documentation
- ✅ Phase 4 foundations: persisted-data redaction, bounded telemetry, run token/cost budgets, and controlled workflow artifacts
- ✅ Phase 4 controls: CI secret audit, explicit checkpoint retention pruning, and provider-usage budget reports
- Outputs: `FEATURE_SPEC.md` (developers) + `FEATURE_SPEC.html` / `FEATURE_SPEC.pdf` (stakeholders) + `FEATURE_CASE_STUDY.html` / `FEATURE_CASE_STUDY.pdf` (portfolio)

## What this project does

In plain language, Dev Journey Agent helps a team answer one question before
coding starts: “Do we understand this request well enough to work on it?”

It reads project context, asks for missing information, defines what success
means, and produces a reviewable plan. When the request remains too vague, it
stops and says what needs clarification. It does not change source code,
merge pull requests, or deploy software.

For a reviewer-first explanation, open the [portfolio handoff guide](docs/MVP/PORTFOLIO_HANDOFF.md).

The visual system is documented in [`docs/BRAND_GUIDELINES.md`](docs/BRAND_GUIDELINES.md)
and can be previewed as a standalone [HTML brand guide](docs/BRAND_GUIDELINES.html),
while the current implementation status is tracked in the [implementation dashboard](docs/MVP/IMPLEMENTATION_DASHBOARD.html),
with the approved v19 reusable mark at `src/templates/assets/dj-mark.png`
(`docs/assets/logo-smooth-junction-v19.png` is the versioned documentation
source; `docs/assets/dj-mark.png` is its documentation copy) and CSS tokens at
`src/templates/assets/brand.css`.

The implementation sequence is documented in
[`docs/MVP/IMPLEMENTATION_ROADMAP.md`](docs/MVP/IMPLEMENTATION_ROADMAP.md), beginning
with durable checkpoints and resumable execution.

Operational boundaries, recovery guidance, cost controls, and release checks
are documented in [`docs/OPERATIONS.md`](docs/OPERATIONS.md). The reproducible
portfolio fixture is described in [`examples/demo/README.md`](examples/demo/README.md).
The architecture overview is kept in [`docs/MVP/ARCHITECTURE_CONTEXT.md`](docs/MVP/ARCHITECTURE_CONTEXT.md).
The end-user walkthrough is available as the standalone [user journey guide](docs/MVP/USER_JOURNEY.html).
The GitHub-native transformation is tracked in the living [GitHub agent roadmap](docs/MVP/GITHUB_AGENT_ROADMAP.html).

Security and persistence checks can also be run directly:

```bash
uv run python scripts/security_audit.py .
uv run python scripts/cost_report.py \
  --input .dev-journey/telemetry/events.jsonl \
  --output .dev-journey/cost-summary.json \
  --max-run-cost-usd 1.00 \
  --max-run-tokens 50000
uv run python scripts/prune_artifacts.py \
  --root .dev-journey/checkpoints \
  --retention-days 14
```

Retention pruning is dry-run by default; add `--apply` only during an
explicit maintenance operation. GitHub planning artifacts use the workflow's
14-day retention policy and expire automatically.

## Quickstart

```bash
uv sync --extra dev
uv run pytest
uv run dev-journey --ticket "Add search" --repo owner/name --branch main
```

The package exposes the same pipeline through the `dev-journey` console
command. For a clean environment, install the locked project and invoke
`dev-journey --help`; the repository also includes a manual GitHub Action under
**Actions → Dev Journey plan**.

The action publishes a `dev-journey/plan` commit status: approved runs are
successful, draft runs remain pending, and needs-input runs are failures until
clarified. Issue or pull-request comments are opt-in workflow inputs; the
action never edits source code, merges, or deploys.

No API keys are required for deterministic mock mode (`USE_MOCK_LLM=true` default).
The default blocking mode exits with `NEEDS_INPUT` when refinement finds unresolved questions.

To continue and export a provisional result:

```bash
uv run python src/main.py --ticket "Add search" --mode draft
```

To demonstrate the fixed semantic-search fixture explicitly:

```bash
uv run python src/main.py --ticket "Demo" --demo --mode draft
```

### Portfolio quick-win: one command, two outcomes

Run the credential-free portfolio demonstration with two visible outcomes: an
approved plan and an intentionally needs-input plan.

```bash
bash scripts/run_portfolio_demo.sh
```

It generates `artifacts/demo/DEMO_SUMMARY.html`, separate approved and
needs-input bundles, checkpoints, telemetry, cost summaries, and security
evidence. The wrapper exits `0` only when both expected scenarios pass.

The original deterministic draft fixture remains available through
`bash scripts/run_demo.sh`.
MCP, provider-specific Codex/Claude/OpenCode adapters, hosted services, and
other provider integrations remain possible future enhancements, not
prerequisites for this portfolio experience. The provider-neutral local wrapper now delegates to
the existing CLI without changing the core surfaces.

The first real-repository validation is documented in
[`docs/MVP/REAL_TEST_CASE_REPORT.md`](docs/MVP/REAL_TEST_CASE_REPORT.md): an
approved read-only run and a complementary `needs_input` safety case, with no
credential values stored in the repository.

For a reviewer-first route through the project, use the
[`portfolio handoff guide`](docs/MVP/PORTFOLIO_HANDOFF.md). It links the deck,
credential-free demo, real validation evidence, engineering boundaries, and
release gate in the order they are easiest to evaluate.

The same validation is repeatable with an already-exported token:

```bash
export GITHUB_TOKEN
bash scripts/run_real_test_case.sh /tmp/dev-journey-real-test
```

The runner keeps the approved repository case and credential-free safety case
in separate bundles and never writes the token to disk.

### Provider-neutral local skill wrapper

The local wrapper exposes the existing CLI through a structured JSON contract
for agentic tools without introducing provider-specific integrations:

```bash
printf '%s' '{"schema_version":1,"ticket":"Add a health-check endpoint","mode":"blocking","out_dir":"artifacts/skill-runs/health-check"}' \
  | USE_MOCK_LLM=true uv run python scripts/run_local_skill.py
```

It returns status, exit code, run ID, and artifact paths as JSON. The wrapper
keeps checkpoints, memory, telemetry, and redacted console output inside the
artifact bundle. See [`docs/MVP/LOCAL_SKILL_WRAPPER.md`](docs/MVP/LOCAL_SKILL_WRAPPER.md)
for the request/response contract and security boundaries.

### Delivery-hardening status

The engineering release gate and portfolio publication package are complete:
the two-scenario demo evidence and frozen branded artifact contract are
verified, and the HTML deck plus LinkedIn/GitHub kit are available. PDF visual
QA and `uv build` remain environment-dependent follow-ups because the current
sandbox cannot run its browser binaries or fetch Hatchling. The CLI and GitHub
Action remain the core surfaces; provider integrations stay deferred.

Every completed stage writes an atomic, versioned checkpoint under
`.dev-journey/checkpoints/<run-id>/` (configurable with `CHECKPOINT_DIR`). If a
run is interrupted, resume from the last validated stage without repeating
completed LLM calls:

```bash
uv run python src/main.py --resume <run-id>
```

The checkpoint preserves the original ticket, repository, mode, mock/real
execution setting, traceability IDs, and validated outputs. `MEMORY.md`
remains an append-only human audit log.

Observability is disabled by default. To record stage latency, blocking
reasons, model fallback attempts, token usage, and cost metadata when the
provider supplies it, enable the Phoenix-compatible recorder:

```bash
PHOENIX_ENABLED=true \
TELEMETRY_PATH=.dev-journey/telemetry/events.jsonl \
uv run python src/main.py --ticket "Add search" --mode draft
```

The recorder always keeps a local JSONL evidence stream and fails open if the
collector or optional Phoenix SDK is unavailable. Install `arize-phoenix-otel`
in the environment to export the same stage spans to Phoenix using
`PHOENIX_ENDPOINT` and `PHOENIX_PROJECT_NAME`.

The complete export stage also writes a print-safe PDF and a five-slide case
study (`FEATURE_CASE_STUDY.html` plus PDF) using a local Chromium-compatible
browser. Set `DJ_CHROME_BINARY` when the browser is not on `PATH`; in restricted
environments the Markdown, HTML, and presentation HTML still finish and the
CLI reports the PDF renderer warning.

For real runs, copy `.env.example` to `.env`, set `USE_MOCK_LLM=false`, and configure
the model credentials and repository token required by your environment.
