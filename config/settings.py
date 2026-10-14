"""Global settings: env loading, LiteLLM model chain, Phoenix toggle.

MVP defaults to mocked LLMs so no keys are required.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    use_mock_llm: bool = True
    openai_api_key: str = ""
    github_token: str = ""
    phoenix_endpoint: str = "http://localhost:6006"
    phoenix_enabled: bool = False
    phoenix_project_name: str = "dev-journey-agent"
    telemetry_path: str = ".dev-journey/telemetry/events.jsonl"
    telemetry_retention_days: int = 14
    telemetry_max_bytes: int = 5_000_000
    max_run_cost_usd: float = 0.0
    max_run_tokens: int = 0
    primary_model: str = "gpt-4o"
    fallback_model: str = "gpt-4o-mini"
    local_model: str = "ollama/llama3"
    llm_timeout_seconds: int = 60
    repo_context_budget_tokens: int = 20_000
    repo_context_max_files: int = 80
    memory_path: str = "MEMORY.md"
    checkpoint_dir: str = ".dev-journey/checkpoints"


def load_settings(env: dict[str, str] | None = None) -> Settings:
    """Load settings from env mapping (defaults to os.environ). Pure/immutable."""
    src = dict(_dotenv_values())
    src.update(os.environ if env is None else env)

    def get(key: str, default: str) -> str:
        val = src.get(key, default)
        return val if isinstance(val, str) else default

    mock_raw = get("USE_MOCK_LLM", "true").strip().lower()
    return Settings(
        use_mock_llm=mock_raw in ("1", "true", "yes", "on"),
        openai_api_key=get("OPENAI_API_KEY", ""),
        github_token=get("GITHUB_TOKEN", ""),
        phoenix_endpoint=get("PHOENIX_ENDPOINT", "http://localhost:6006"),
        phoenix_enabled=get("PHOENIX_ENABLED", "false").strip().lower()
        in ("1", "true", "yes", "on"),
        phoenix_project_name=get("PHOENIX_PROJECT_NAME", "dev-journey-agent"),
        telemetry_path=get("TELEMETRY_PATH", ".dev-journey/telemetry/events.jsonl"),
        telemetry_retention_days=max(1, int(get("TELEMETRY_RETENTION_DAYS", "14"))),
        telemetry_max_bytes=max(1, int(get("TELEMETRY_MAX_BYTES", "5000000"))),
        max_run_cost_usd=max(0.0, float(get("MAX_RUN_COST_USD", "0"))),
        max_run_tokens=max(0, int(get("MAX_RUN_TOKENS", "0"))),
        primary_model=get("PRIMARY_MODEL", "gpt-4o"),
        fallback_model=get("FALLBACK_MODEL", "gpt-4o-mini"),
        local_model=get("LOCAL_MODEL", "ollama/llama3"),
        llm_timeout_seconds=max(1, int(get("LLM_TIMEOUT_SECONDS", "60"))),
        repo_context_budget_tokens=max(1, int(get("REPO_CONTEXT_BUDGET_TOKENS", "20000"))),
        repo_context_max_files=max(1, int(get("REPO_CONTEXT_MAX_FILES", "80"))),
        memory_path=get("MEMORY_PATH", "MEMORY.md"),
        checkpoint_dir=get("CHECKPOINT_DIR", ".dev-journey/checkpoints"),
    )


def _dotenv_values(path: str | Path = ".env") -> dict[str, str]:
    """Load a minimal dotenv file without overriding the process environment."""
    file_path = Path(path)
    if not file_path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values
