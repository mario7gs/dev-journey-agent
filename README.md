# Dev-Journey-Agent

Portfolio AI agent for turning a vague ticket and an optional GitHub repository
into a traceable implementation plan: refinement → DoD/contracts → PRD/TRD →
TDD roadmap → stakeholder export.

## Status: Phases 0–5 implemented · portfolio quick-win queued

- ✅ Blocking mode is the default: unresolved Step 0 questions stop approval
- ✅ Draft mode continues for exploration but cannot be marked approved
- ✅ Read-only GitHub context is assembled before refinement
- ✅ Mock mode is deterministic and ticket-aware; `--demo` is an explicit fixture
- ✅ Real mode uses LiteLLM primary → fallback → local model chain
- ✅ Stable traceability IDs connect requirements, contracts, acceptance criteria, tests, security checks, and implementation steps
- ✅ Critic validates cross-stage references before approval
- ✅ Shared visual identity and brand tokens for HTML, PDF, and portfolio presentation surfaces
- ✅ Portfolio exports: print-safe `FEATURE_SPEC.pdf`, `FEATURE_CASE_STUDY.html`, and presentation PDF
- ✅ Release polish: CI quality gates, reproducible demo script, and operations/cost documentation
- ✅ Phase 4 foundations: persisted-data redaction, bounded telemetry, run token/cost budgets, and controlled workflow artifacts
- ✅ Phase 4 controls: CI secret audit, explicit checkpoint retention pruning, and provider-usage budget reports
- Outputs: `FEATURE_SPEC.md` (developers) + `FEATURE_SPEC.html` / `FEATURE_SPEC.pdf` (stakeholders) + `FEATURE_CASE_STUDY.html` / `FEATURE_CASE_STUDY.pdf` (portfolio)

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

### Portfolio quick-win queued for the next session

The next implementation milestone is a credential-free, one-command portfolio
demo with two visible outcomes: an approved plan and an intentionally
needs-input/draft plan. It will generate a compact `DEMO_SUMMARY.html` linking
the outputs, checkpoints, telemetry, budget report, and security evidence.

The current deterministic fixture remains available through
`bash scripts/run_demo.sh`. The planned wrapper is
`bash scripts/run_portfolio_demo.sh` and will be added in the next session.
MCP, Codex/Claude/OpenCode skill wrappers, hosted services, and other provider
integrations are recorded as possible future enhancements, not prerequisites
for this portfolio milestone.

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
