from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from src.extensions.phase_4_8.clarification_cases import CLARIFICATION_CASES
from src.extensions.phase_4_8.clarification_recovery import evaluate_clarification_recovery


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "results" / "prototype4_extensions" / "phase_4_8"
RESULTS_CSV = OUTPUT_DIR / "clarification_recovery_results.csv"
SUMMARY_JSON = OUTPUT_DIR / "clarification_recovery_summary.json"

FIELDNAMES = [
    "original_command",
    "original_decision",
    "original_ambiguity_score",
    "clarified_command",
    "clarified_decision",
    "clarified_ambiguity_score",
    "score_delta",
    "recovered",
]


def run_clarification_recovery(
    cases: list[dict] | None = None,
    output_dir: str | Path = OUTPUT_DIR,
) -> dict:
    selected_cases = cases if cases is not None else CLARIFICATION_CASES
    results = [
        evaluate_clarification_recovery(case["original_command"], case["clarified_command"])
        for case in selected_cases
    ]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_results_csv(output / RESULTS_CSV.name, results)
    summary = _summarize(results)
    (output / SUMMARY_JSON.name).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    summary = run_clarification_recovery()
    print(f"Clarification recovery cases evaluated: {summary['total_cases']}")
    print(f"Recovered cases: {summary['recovered_cases']}")
    print(f"Recovery rate: {summary['recovery_rate']:.2f}")


def _summarize(results: list[dict]) -> dict:
    total = len(results)
    recovered = sum(1 for result in results if result["recovered"])
    return {
        "total_cases": total,
        "recovered_cases": recovered,
        "recovery_rate": recovered / total if total else 0.0,
        "mean_original_ambiguity_score": _mean(result["original_ambiguity_score"] for result in results),
        "mean_clarified_ambiguity_score": _mean(result["clarified_ambiguity_score"] for result in results),
        "mean_score_delta": _mean(result["score_delta"] for result in results),
        "original_decision_counts": dict(sorted(Counter(result["original_decision"] for result in results).items())),
        "clarified_decision_counts": dict(sorted(Counter(result["clarified_decision"] for result in results).items())),
    }


def _write_results_csv(path: Path, results: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)


def _mean(values) -> float:
    numbers = list(values)
    return round(sum(numbers) / len(numbers), 4) if numbers else 0.0


if __name__ == "__main__":
    main()
