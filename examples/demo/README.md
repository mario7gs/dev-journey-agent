# Reproducible demo artifact

Run the deterministic fixture from the repository root:

```bash
bash scripts/run_demo.sh
```

The command writes a reviewable draft artifact set under `artifacts/demo/`:

- `FEATURE_SPEC.md` — developer-facing plan
- `FEATURE_SPEC.html` — stakeholder report
- `FEATURE_CASE_STUDY.html` — five-slide portfolio view
- `MEMORY.md` and `checkpoints/` — audit and resume evidence

The fixture intentionally contains unresolved scope questions. The underlying
pipeline returns `2`, confirming that draft mode remains provisional; the
wrapper treats that expected result as a successful artifact generation.

## Portfolio quick-win: two outcomes

Run the complete credential-free portfolio demonstration with:

```bash
bash scripts/run_portfolio_demo.sh
```

It produces:

- an approved mock run that demonstrates the complete evidence chain; and
- a needs-input/draft run that demonstrates the safety gate and provisional
  outcome.

Both bundles are indexed by `DEMO_SUMMARY.html`, with links to generated plans,
checkpoints, telemetry, cost evidence, and the security audit. The wrapper
returns success only when both expected outcomes and their evidence files are
present. The generated report, case-study, and summary use the official v19
mark, shared color tokens, and sticky section navigation. This presentation
contract is frozen for the portfolio MVP; visual changes require an explicit
design decision and regenerated evidence. MCP, chat-provider adapters, hosted
services, and automatic issue/PR integrations remain deferred possible next
features. The provider-neutral local skill wrapper is now implemented as a
thin JSON adapter around the existing CLI; see
`docs/MVP/LOCAL_SKILL_WRAPPER.md` for its contract.
