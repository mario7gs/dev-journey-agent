"""Summarize redacted JSONL telemetry into a reviewable cost report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _number(value: Any) -> int | float:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return value
    return 0


def _budget_status(
    total_tokens: int,
    total_cost_usd: float,
    max_run_tokens: int,
    max_run_cost_usd: float,
) -> str:
    exceeded_tokens = bool(max_run_tokens) and total_tokens > max_run_tokens
    exceeded_cost = bool(max_run_cost_usd) and total_cost_usd > max_run_cost_usd
    if exceeded_tokens or exceeded_cost:
        return "exceeded"
    if max_run_tokens or max_run_cost_usd:
        return "within_budget"
    return "not_configured"


def summarize_telemetry(
    path: str | Path,
    *,
    max_run_tokens: int = 0,
    max_run_cost_usd: float = 0.0,
    max_bytes: int = 0,
    retention_days: int = 0,
) -> dict[str, Any]:
    """Aggregate stage usage without exposing raw telemetry values.

    Stage events contain per-stage usage, so only ``event == "stage"`` records
    are included in the total. Malformed lines are counted and omitted rather
    than making a diagnostic report mask the original planning result.
    """
    telemetry_path = Path(path)
    total_input = 0
    total_output = 0
    total_tokens = 0
    total_cost = 0.0
    stage_count = 0
    malformed_lines = 0
    run_ids: set[str] = set()
    events: list[dict[str, Any]] = []

    if telemetry_path.is_file():
        for line in telemetry_path.read_text(encoding="utf-8").splitlines():
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                malformed_lines += 1
                continue
            if not isinstance(payload, dict):
                malformed_lines += 1
                continue
            events.append(payload)
            if payload.get("run_id"):
                run_ids.add(str(payload["run_id"]))
            if payload.get("event") != "stage":
                continue
            stage_count += 1
            attributes = payload.get("attributes")
            usage = attributes.get("usage") if isinstance(attributes, dict) else {}
            if not isinstance(usage, dict):
                continue
            total_input += int(_number(usage.get("input_tokens")))
            total_output += int(_number(usage.get("output_tokens")))
            total_tokens += int(_number(usage.get("total_tokens")))
            total_cost += float(_number(usage.get("cost_usd")))

    budgets = [
        event.get("attributes", {}).get("budget", {})
        for event in events
        if isinstance(event.get("attributes"), dict)
        and isinstance(event["attributes"].get("budget"), dict)
    ]
    if budgets:
        latest = budgets[-1]
        max_run_tokens = int(_number(latest.get("max_run_tokens"))) or max_run_tokens
        max_run_cost_usd = float(_number(latest.get("max_run_cost_usd"))) or max_run_cost_usd

    file_bytes = telemetry_path.stat().st_size if telemetry_path.is_file() else 0
    report: dict[str, Any] = {
        "schema_version": 1,
        "telemetry_path": str(telemetry_path),
        "run_ids": sorted(run_ids),
        "events": len(events),
        "stage_events": stage_count,
        "malformed_lines": malformed_lines,
        "usage": {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_tokens,
            "cost_usd": round(total_cost, 8),
        },
        "budget": {
            "max_run_tokens": max_run_tokens,
            "max_run_cost_usd": max_run_cost_usd,
            "status": _budget_status(
                total_tokens,
                total_cost,
                max_run_tokens,
                max_run_cost_usd,
            ),
        },
        "retention": {
            "file_bytes": file_bytes,
            "max_bytes": max_bytes,
            "size_status": "exceeded" if max_bytes and file_bytes > max_bytes else "within_limit",
            "retention_days": retention_days,
        },
    }
    return report


def write_cost_report(report: dict[str, Any], output: str | Path) -> Path:
    """Write a deterministic, human-readable JSON report atomically enough for CI."""
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
