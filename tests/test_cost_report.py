import json

from core.cost_report import summarize_telemetry, write_cost_report


def test_cost_report_aggregates_stage_usage_and_budget(tmp_path):
    telemetry = tmp_path / "events.jsonl"
    telemetry.write_text(
        json.dumps(
            {
                "event": "stage",
                "run_id": "run-1",
                "attributes": {
                    "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15, "cost_usd": 0.02},
                    "budget": {"max_run_tokens": 100, "max_run_cost_usd": 0.10},
                },
            }
        )
        + "\n"
        + json.dumps(
            {
                "event": "stage",
                "run_id": "run-1",
                "attributes": {
                    "usage": {"input_tokens": 20, "output_tokens": 5, "total_tokens": 25, "cost_usd": 0.03},
                    "budget": {"max_run_tokens": 100, "max_run_cost_usd": 0.10},
                },
            }
        )
        + "\n"
        + '{"event":"resume"}\n'
        + "not-json\n",
        encoding="utf-8",
    )

    report = summarize_telemetry(telemetry, max_bytes=1000, retention_days=14)

    assert report["usage"] == {
        "input_tokens": 30,
        "output_tokens": 10,
        "total_tokens": 40,
        "cost_usd": 0.05,
    }
    assert report["budget"]["status"] == "within_budget"
    assert report["events"] == 3
    assert report["malformed_lines"] == 1
    assert report["retention"]["retention_days"] == 14


def test_cost_report_marks_exceeded_budget_and_writes_json(tmp_path):
    telemetry = tmp_path / "events.jsonl"
    telemetry.write_text(
        json.dumps(
            {
                "event": "stage",
                "run_id": "run-2",
                "attributes": {"usage": {"total_tokens": 12, "cost_usd": 0.40}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    report = summarize_telemetry(telemetry, max_run_tokens=10, max_run_cost_usd=0.25)
    output = write_cost_report(report, tmp_path / "cost-summary.json")

    assert report["budget"]["status"] == "exceeded"
    assert json.loads(output.read_text(encoding="utf-8"))["usage"]["cost_usd"] == 0.4
