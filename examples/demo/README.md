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

## Next queued portfolio experience

The next session will add a credential-free two-scenario wrapper:

- an approved mock run that demonstrates the complete evidence chain; and
- a needs-input/draft run that demonstrates the safety gate and provisional
  outcome.

Both bundles will be indexed by `DEMO_SUMMARY.html`, with links to generated
plans, checkpoints, telemetry, cost evidence, and the security audit. MCP,
chat-provider adapters, hosted services, and automatic issue/PR integrations
remain deferred possible next features.
