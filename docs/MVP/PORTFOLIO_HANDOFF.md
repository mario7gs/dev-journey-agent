# Dev Journey Agent — Portfolio Handoff

This is the shortest credible review path for the project. It is designed for
a hiring manager, senior engineer, team lead, architect, or technology leader
who wants to understand the value without studying the whole repository first.

The [LinkedIn publication kit](../PORTFOLIO_PUBLICATION_KIT.md) includes a
nontechnical post and an eight-page PDF carousel for the same story.

## One-sentence positioning

Dev Journey Agent is a CLI-first planning copilot that turns an underspecified
development ticket into a traceable, reviewable implementation plan—and stops
when a high-severity requirement gap remains unresolved.

## Recommended review path

### 1. Start with the visual story

Open the self-contained [portfolio deck](../../artifacts/portfolio/DEV_JOURNEY_PORTFOLIO_DECK.html).
It explains the problem, workflow, safety gate, evidence, and trade-offs in
six short sections. For a concise recruiter-facing version, use the
[LinkedIn carousel PDF](../../artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf).

### 2. See the product run without credentials

Run:

```bash
bash scripts/run_portfolio_demo.sh
```

Then open [`artifacts/demo/DEMO_SUMMARY.html`](../../artifacts/demo/DEMO_SUMMARY.html).
The summary presents the approved plan and the intentionally blocked plan with
separate artifacts, checkpoints, telemetry, cost reports, and security
evidence.

### 3. Inspect the external validation proof

Read the [real test-case report](REAL_TEST_CASE_REPORT.md). It records a
successful read-only run against `mario7gs/dev-journey-agent@main` and a
complementary ambiguous-ticket run that returned `needs_input` with exit code
`2` instead of inventing an approved plan.

The repeatable runner is available at
[`scripts/run_real_test_case.sh`](../../scripts/run_real_test_case.sh).

### 4. Review the engineering boundaries

Use the [operations notes](../OPERATIONS.md) for configuration, privacy,
recovery, cost controls, retention, and release checks. The
[implementation roadmap](IMPLEMENTATION_ROADMAP.md) records the decisions and
deliberate deferrals.

## Claim-to-evidence map

| Portfolio claim | Evidence | What a reviewer can verify |
| --- | --- | --- |
| The workflow is useful immediately | Portfolio demo and summary | One command produces two contrasting outcomes and inspectable artifacts |
| The agent does not hide ambiguity | Needs-input report and exit code `2` | Missing search scope/data source blocks approval |
| The workflow is traceable | Checkpoints, `MEMORY.md`, telemetry, status JSON | Stages, IDs, recovery state, and review signals are persisted |
| The integration boundary is practical | Local skill wrapper | Generic agentic tools can invoke the existing CLI without provider coupling |
| The project is security-conscious | Secret audit, redaction, budget and retention controls | Credentials are not persisted and limits are explicit |
| The scope is intentionally restrained | Roadmap and operations notes | CLI and GitHub Action stay core; integrations are deferred |

## Release gate

Run the repository checks with:

```bash
UV_CACHE_DIR=/tmp/dev-journey-agent-uv-cache bash scripts/verify.sh
```

Expected result: the full test suite passes, the secret audit passes, lint and
type checks pass, and the HTML surfaces parse successfully. Package building
remains environment-dependent when the locked Hatchling backend is unavailable
offline.

## Portfolio handoff status

- [x] Core CLI pipeline and GitHub Action are implemented.
- [x] Security, persistence, checkpoints, telemetry, and cost controls are documented.
- [x] Credential-free two-scenario demo is implemented.
- [x] Approved artifact layout, logo, palette, and navigation are frozen.
- [x] Provider-neutral local skill wrapper is implemented.
- [x] Real repository and needs-input cases are documented and repeatable.
- [x] HTML portfolio deck and LinkedIn/GitHub publication kit are available.
- [x] LinkedIn carousel PDF was rendered and visually checked page by page.
- [ ] Run `uv build` in a normal environment with the locked Hatchling backend available.

## Explicitly deferred

MCP, provider-specific Codex/Claude/OpenCode/Gemini adapters, hosted services,
automatic issue/PR integrations, source-code mutation, and deployment remain
future enhancements. They are not required to demonstrate the current
portfolio value.
