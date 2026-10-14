"""Create a provider-usage summary from a Dev Journey telemetry JSONL file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from core.cost_report import summarize_telemetry, write_cost_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Telemetry JSONL path")
    parser.add_argument("--output", required=True, help="JSON report path")
    parser.add_argument("--max-run-tokens", type=int, default=0)
    parser.add_argument("--max-run-cost-usd", type=float, default=0.0)
    parser.add_argument("--max-bytes", type=int, default=0)
    parser.add_argument("--retention-days", type=int, default=0)
    args = parser.parse_args(argv)
    report = summarize_telemetry(
        args.input,
        max_run_tokens=max(0, args.max_run_tokens),
        max_run_cost_usd=max(0.0, args.max_run_cost_usd),
        max_bytes=max(0, args.max_bytes),
        retention_days=max(0, args.retention_days),
    )
    write_cost_report(report, args.output)
    print(json.dumps({"usage": report["usage"], "budget": report["budget"]}, sort_keys=True))
    return 2 if report["budget"]["status"] == "exceeded" else 0


if __name__ == "__main__":
    raise SystemExit(main())
