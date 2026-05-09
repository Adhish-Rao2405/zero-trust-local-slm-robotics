from __future__ import annotations

import csv
import json

from src.extensions.phase_4_8.clarification_cases import CLARIFICATION_CASES
from src.extensions.phase_4_8.clarification_runner import run_clarification_recovery


def test_builtin_clarification_cases_have_expected_fields():
    assert len(CLARIFICATION_CASES) >= 5
    for case in CLARIFICATION_CASES:
        assert set(case) == {
            "original_command",
            "clarified_command",
            "expected_original_decision",
            "expected_clarified_decision",
        }


def test_runner_writes_only_phase_4_8_outputs(tmp_path):
    summary = run_clarification_recovery(output_dir=tmp_path)

    results_path = tmp_path / "clarification_recovery_results.csv"
    summary_path = tmp_path / "clarification_recovery_summary.json"
    assert results_path.exists()
    assert summary_path.exists()
    assert summary["total_cases"] == len(CLARIFICATION_CASES)

    with open(results_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(CLARIFICATION_CASES)
    assert all(row["recovered"] == "True" for row in rows)

    parsed_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert parsed_summary["recovered_cases"] == len(CLARIFICATION_CASES)
    assert parsed_summary["recovery_rate"] == 1.0


def test_summary_contains_required_metrics(tmp_path):
    summary = run_clarification_recovery(output_dir=tmp_path)

    assert set(summary) == {
        "total_cases",
        "recovered_cases",
        "recovery_rate",
        "mean_original_ambiguity_score",
        "mean_clarified_ambiguity_score",
        "mean_score_delta",
        "original_decision_counts",
        "clarified_decision_counts",
    }
    assert summary["mean_original_ambiguity_score"] > summary["mean_clarified_ambiguity_score"]
    assert summary["mean_score_delta"] > 0
