"""Inspect or explicitly prune expired checkpoint run directories."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from core.retention import prune_expired_runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Configured checkpoint directory")
    parser.add_argument("--retention-days", type=int, required=True)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Delete expired immediate child run directories; default is a dry run",
    )
    args = parser.parse_args(argv)
    report = prune_expired_runs(
        args.root,
        args.retention_days,
        dry_run=not args.apply,
    )
    action = "would delete" if not args.apply else "deleted"
    for path in report.expired:
        print(f"{action}: {path}")
    if not report.expired:
        print("No expired run directories found.")
    if args.apply:
        print(f"Pruned {len(report.deleted)} expired run director{'y' if len(report.deleted) == 1 else 'ies'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
