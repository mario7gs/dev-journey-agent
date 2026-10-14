from datetime import UTC, datetime, timedelta

from core.retention import expired_run_dirs, prune_expired_runs


def test_retention_is_dry_run_by_default_and_only_considers_directories(tmp_path):
    now = datetime(2026, 10, 14, tzinfo=UTC)
    expired = tmp_path / "old-run"
    expired.mkdir()
    (expired / "checkpoint.json").write_text("{}", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "old-run").mkdir()
    timestamp = (now - timedelta(days=30)).timestamp()
    import os

    os.utime(expired, (timestamp, timestamp))

    report = prune_expired_runs(tmp_path, 14, now=now)

    assert report.expired == (expired,)
    assert expired.exists()


def test_retention_apply_removes_expired_run_and_keeps_recent_run(tmp_path):
    now = datetime(2026, 10, 14, tzinfo=UTC)
    old_run = tmp_path / "old-run"
    recent_run = tmp_path / "recent-run"
    old_run.mkdir()
    recent_run.mkdir()
    import os

    old_timestamp = (now - timedelta(days=30)).timestamp()
    recent_timestamp = (now - timedelta(days=2)).timestamp()
    os.utime(old_run, (old_timestamp, old_timestamp))
    os.utime(recent_run, (recent_timestamp, recent_timestamp))

    report = prune_expired_runs(tmp_path, 14, now=now, dry_run=False)

    assert report.deleted == (old_run,)
    assert not old_run.exists()
    assert recent_run.exists()


def test_retention_rejects_non_positive_days(tmp_path):
    try:
        expired_run_dirs(tmp_path, 0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("expected invalid retention period to fail")
