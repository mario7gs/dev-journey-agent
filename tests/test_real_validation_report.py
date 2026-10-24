from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_real_validation_report_records_approved_and_needs_input_paths() -> None:
    report = (ROOT / "docs/MVP/REAL_TEST_CASE_REPORT.md").read_text(encoding="utf-8")

    assert "mario7gs/dev-journey-agent@main" in report
    assert "1282e851d5ad49649fe66182c15f9ad6" in report
    assert "approved" in report
    assert "needs_input" in report
    assert "Exit code: `0`" in report
    assert "exit code: `2`" in report
    assert "0689e2d2972f466ba7aa48139212c748" in report
    assert "GITHUB_TOKEN=" not in report
    assert "github_pat_" not in report
    assert "ghp_" not in report
