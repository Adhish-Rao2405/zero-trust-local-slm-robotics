from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from src.extensions.phase_4_9.formal_safety_auditor import (
    audit_action_plan,
    audit_gate_decision,
)
from src.extensions.phase_4_9.formal_safety_cases import FORMAL_SAFETY_CASES


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "results" / "prototype4_extensions" / "phase_4_9"
RESULTS_CSV = OUTPUT_DIR / "formal_safety_audit_results.csv"
SUMMARY_JSON = OUTPUT_DIR / "formal_safety_audit_summary.json"

FIELDNAMES = [
    "case_id",
    "audit_type",
    "expected_safe",
    "passed",
    "violation_rule_ids",
    "critical_violation_count",
    "rule_ids_checked",
    "subject",
]


def run_formal_safety_audit(
    cases: list[dict] | None = None,
    output_dir: str | Path = OUTPUT_DIR,
) -> dict:
    selected_cases = cases if cases is not None else FORMAL_SAFETY_CASES
    results = [_evaluate_case(case) for case in selected_cases]

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_results_csv(output / RESULTS_CSV.name, results)
    summary = _summarize(results)
    (output / SUMMARY_JSON.name).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    summary = run_formal_safety_audit()
    print(f"Formal safety cases evaluated: {summary['total_cases']}")
    print(f"Expected unsafe cases: {summary['expected_unsafe_cases']}")
    print(f"Unsafe cases correctly rejected: {summary['unsafe_cases_correctly_rejected']}")
    print(f"Unsafe rejection rate: {summary['unsafe_rejection_rate']:.2f}")
    print(f"Critical violations detected: {summary['critical_violation_count']}")


def _evaluate_case(case: dict) -> dict:
    if case["audit_type"] == "action_plan":
        audit = audit_action_plan(case["action_plan"])
        subject = case["action_plan"]
    elif case["audit_type"] == "gate_decision":
        audit = audit_gate_decision(case["command"], case["gate_decision"])
        subject = {
            "command": case["command"],
            "gate_decision": case["gate_decision"],
        }
    else:
        raise ValueError(f"unsupported audit_type: {case['audit_type']}")

    critical_count = sum(1 for violation in audit["violations"] if violation["severity"] == "critical")
    return {
        "case_id": case["case_id"],
        "audit_type": case["audit_type"],
        "expected_safe": case["expected_safe"],
        "passed": audit["passed"],
        "violations": audit["violations"],
        "violation_rule_ids": [violation["rule_id"] for violation in audit["violations"]],
        "critical_violation_count": critical_count,
        "rule_ids_checked": audit["rule_ids_checked"],
        "subject": subject,
    }


def _summarize(results: list[dict]) -> dict:
    total = len(results)
    passed_cases = sum(1 for result in results if result["passed"])
    expected_safe_cases = sum(1 for result in results if result["expected_safe"])
    expected_unsafe_cases = total - expected_safe_cases
    unsafe_cases_correctly_rejected = sum(
        1 for result in results if not result["expected_safe"] and not result["passed"]
    )
    violation_counts = Counter(
        rule_id
        for result in results
        for rule_id in result["violation_rule_ids"]
    )
    critical_violation_count = sum(result["critical_violation_count"] for result in results)
    return {
        "total_cases": total,
        "passed_cases": passed_cases,
        "failed_cases": total - passed_cases,
        "expected_safe_cases": expected_safe_cases,
        "expected_unsafe_cases": expected_unsafe_cases,
        "unsafe_cases_correctly_rejected": unsafe_cases_correctly_rejected,
        "unsafe_rejection_rate": (
            unsafe_cases_correctly_rejected / expected_unsafe_cases
            if expected_unsafe_cases
            else 0.0
        ),
        "rule_violation_counts": dict(sorted(violation_counts.items())),
        "critical_violation_count": critical_violation_count,
    }


def _write_results_csv(path: Path, results: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "case_id": result["case_id"],
                    "audit_type": result["audit_type"],
                    "expected_safe": result["expected_safe"],
                    "passed": result["passed"],
                    "violation_rule_ids": json.dumps(result["violation_rule_ids"]),
                    "critical_violation_count": result["critical_violation_count"],
                    "rule_ids_checked": json.dumps(result["rule_ids_checked"]),
                    "subject": json.dumps(result["subject"], sort_keys=True),
                }
            )


if __name__ == "__main__":
    main()

