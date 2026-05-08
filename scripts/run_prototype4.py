from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.prototype4.execution_evaluator import evaluate_records
from src.prototype4.loaders import load_prototype3_results_json
from src.prototype4.summary_exports import export_prototype4_summaries


def main() -> None:
    input_path = REPO_ROOT / "datasets" / "prototype3_results" / "rq5_comparison.jsonl"
    output_dir = REPO_ROOT / "results" / "summaries"

    results = load_prototype3_results_json(input_path)
    records = evaluate_records(results)
    export_prototype4_summaries(records, str(output_dir))

    print(f"Input Prototype3Result rows: {len(results)}")
    print(f"Output ExecutionEvaluationRecord rows: {len(records)}")


if __name__ == "__main__":
    main()
