"""Safe, explicit retention helpers for durable run checkpoints."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class RetentionReport:
    """Result of a retention inspection or prune operation."""

    root: Path
    retention_days: int
    cutoff: datetime
    expired: tuple[Path, ...]
    deleted: tuple[Path, ...] = ()


def _validate_days(retention_days: int) -> int:
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")
    return retention_days


def expired_run_dirs(
    root: str | Path,
    retention_days: int,
    *,
    now: datetime | None = None,
) -> RetentionReport:
    """Find immediate child run directories older than the retention cutoff.

    The helper intentionally never walks beyond the configured root's first
    level. This prevents a retention run from accidentally treating arbitrary
    nested repository directories as agent runs.
    """
    days = _validate_days(retention_days)
    root_path = Path(root)
    current = (now or datetime.now(UTC)).astimezone(UTC)
    cutoff = current - timedelta(days=days)
    if not root_path.is_dir():
        return RetentionReport(root_path, days, cutoff, ())

    expired: list[Path] = []
    for child in sorted(root_path.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        try:
            modified = datetime.fromtimestamp(child.stat().st_mtime, tz=UTC)
        except OSError:
            continue
        if modified < cutoff:
            expired.append(child)
    return RetentionReport(root_path, days, cutoff, tuple(expired))


def prune_expired_runs(
    root: str | Path,
    retention_days: int,
    *,
    now: datetime | None = None,
    dry_run: bool = True,
) -> RetentionReport:
    """Inspect or remove expired immediate child run directories.

    ``dry_run`` defaults to ``True`` so callers must explicitly opt into
    deletion. Only directories returned by :func:`expired_run_dirs` are ever
    passed to ``rmtree``.
    """
    report = expired_run_dirs(root, retention_days, now=now)
    if dry_run:
        return report

    deleted: list[Path] = []
    for directory in report.expired:
        if directory.is_dir():
            shutil.rmtree(directory)
            deleted.append(directory)
    return RetentionReport(
        report.root,
        report.retention_days,
        report.cutoff,
        report.expired,
        tuple(deleted),
    )
