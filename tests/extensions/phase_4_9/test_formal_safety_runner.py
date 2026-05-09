from __future__ import annotations

import csv
import json

from src.extensions.phase_4_9.formal_safety_cases import FORMAL_SAFETY_CASES
from src.extensions.phase_4_9.formal_safety_runner import (
    OUTPUT_DIR,
    run_formal_safety_audit,
)


def test_builtin_formal_safety_cases_have_expected_shape():
    assert len(FORMAL_SAFETY_CASES) == 18
    assert sum(1 for case in FORMAL_SAFETY_CASES if case["expected_safe"]) == 8
    assert sum(1 for case in FORMAL_SAFETY_CASES if not case["expected_safe"]) == 10

    for case in FORMAL_SAFETY_CASES:
        assert {"case_id", "audit_type", "expected_safe"}.issubset(case)
        if case["audit_type"] == "action_plan":
            assert "action_plan" in case
        elif case["audit_type"] == "gate_decision":
            assert {"command", "gate_decision"}.issubset(case)
        else:
            raise AssertionError(case["audit_type"])


def test_runner_writes_only_phase_4_9_outputs(tmp_path):
    output_dir = tmp_path / "results" / "prototype4_extensions" / "phase_4_9"

    summary = run_formal_safety_audit(output_dir=output_dir)

    results_path = output_dir / "formal_safety_audit_results.csv"
    summary_path = output_dir / "formal_safety_audit_summary.json"
    assert results_path.exists()
    assert summary_path.exists()
    assert "prototype4_extensions" in OUTPUT_DIR.parts
    assert OUTPUT_DIR.parts[-1] == "phase_4_9"

    with open(results_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(FORMAL_SAFETY_CASES)
    assert {path.name for path in output_dir.iterdir()} == {
        "formal_safety_audit_results.csv",
        "formal_safety_audit_summary.json",
    }

    parsed_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert parsed_summary == summary


def test_summary_contains_required_metrics(tmp_path):
    summary = run_formal_safety_audit(output_dir=tmp_path)

    assert set(summary) == {
        "total_cases",
        "passed_cases",
        "failed_cases",
        "expected_safe_cases",
        "expected_unsafe_cases",
        "unsafe_cases_correctly_rejected",
        "unsafe_rejection_rate",
        "rule_violation_counts",
        "critical_violation_count",
    }
    assert summary["total_cases"] == len(FORMAL_SAFETY_CASES)
    assert summary["expected_safe_cases"] == 8
    assert summary["expected_unsafe_cases"] == 10
    assert summary["unsafe_cases_correctly_rejected"] == 10
    assert summary["unsafe_rejection_rate"] == 1.0
    assert summary["critical_violation_count"] > 0

