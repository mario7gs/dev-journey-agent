# Provider-neutral local skill wrapper

`scripts/run_local_skill.py` is the project's deliberately small adapter for
local agentic tools. It exposes the existing CLI through a stable JSON
contract; it is not a second planning pipeline and it does not provide a
provider-specific integration.

## Invocation

Read one JSON request from stdin:

```bash
RUN_DIR="$(mktemp -d)"
printf '%s' '{
  "schema_version": 1,
  "ticket": "Add a health-check endpoint",
  "mode": "blocking",
  "out_dir": "'"$RUN_DIR"'/health-check"
}' | USE_MOCK_LLM=true uv run python scripts/run_local_skill.py
```

The wrapper writes a self-contained bundle containing the delegated CLI's
Markdown/HTML artifacts, `run-status.json`, checkpoints, memory, telemetry,
and a redacted `console.log`. It emits one JSON response on stdout and keeps
human-oriented CLI output in `console.log`.

It can also read a request file:

```bash
uv run python scripts/run_local_skill.py --request-file request.json
```

## Request contract

```json
{
  "schema_version": 1,
  "ticket": "Add a health-check endpoint",
  "repo": "owner/name",
  "branch": "main",
  "mode": "blocking",
  "out_dir": "artifacts/skill-runs/health-check",
  "resume": "existing-run-id"
}
```

`ticket` is required for a new run. `repo`, `branch`, and `mode` are optional;
the defaults are no repository context, `main`, and `blocking`. `out_dir` is
optional for a new run and defaults to a unique directory under
`artifacts/skill-runs/`; it is required when resuming. A resume request may
include only `resume`, `out_dir`, `mode`, and `schema_version`; ticket and
repository identity come from the checkpoint.

## Response contract

```json
{
  "schema_version": 1,
  "run_id": "...",
  "status": "approved",
  "github_status": "success",
  "approved": true,
  "exit_code": 0,
  "block_reasons": [],
  "output_paths": {
    "md": ".../FEATURE_SPEC.md",
    "html": ".../FEATURE_SPEC.html"
  },
  "artifact_dir": ".../artifacts/skill-runs/health-check",
  "console_log": ".../console.log"
}
```

The process exit code preserves the CLI contract: `0` for approved, `2` for
needs-input or draft, and `1` for an invalid request or wrapper failure.

## Security and scope boundaries

- The wrapper uses direct argument arrays; it never invokes a shell.
- Request fields are schema-checked and unknown fields are rejected.
- Memory, checkpoints, and telemetry are isolated inside the selected output
  bundle instead of using the caller's default paths.
- Console output is redacted before it is persisted or exposed through the
  artifact bundle.
- The wrapper makes no provider or GitHub write calls and does not edit source
  code, issues, pull requests, or deployments.
- Provider-specific adapters, MCP, hosted execution, and automatic triggers are
  intentionally outside this contract.
