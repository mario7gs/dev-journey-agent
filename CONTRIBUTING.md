# Contributing to Dev Journey Agent

Thank you for taking an interest in the project.

## Start here

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src config
```

Run the complete local release gate before opening a pull request:

```bash
UV_CACHE_DIR=/tmp/dev-journey-agent-uv-cache bash scripts/verify.sh
```

## Project boundaries

Keep changes focused on the CLI-first planning workflow and its manual GitHub
Action. Preserve blocking mode as the default, explicit draft semantics,
read-only repository context, redacted persistence, and the frozen portfolio
artifact contract.

MCP, provider-specific chat adapters, hosted services, automatic issue/PR
mutations, and deployments are intentionally deferred. Proposals in those
areas should explain why the current boundaries are no longer sufficient.

## Security expectations

Never commit tokens, private keys, local credential files, or raw provider
output. Use mock mode for tests and demos. Keep real credentials in the local
process environment and review the secret audit before sharing artifacts.
