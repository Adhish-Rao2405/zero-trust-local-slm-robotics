from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.prototype4.loaders import load_prototype3_results_json
from src.prototype4.safety_latency_frontier import (
    evaluate_frontier,
    export_safety_latency_frontier,
)


def main() -> None:
    input_path = REPO_ROOT / "datasets" / "prototype3_results" / "rq5_comparison.jsonl"
    output_dir = REPO_ROOT / "results" / "summaries"

    results = load_prototype3_results_json(input_path)
    frontier_records = evaluate_frontier(results)
    export_safety_latency_frontier(frontier_records, output_dir)

    print(f"Input Prototype3Result rows: {len(results)}")
    print(f"Safety-latency frontier rows: {len(frontier_records)}")


if __name__ == "__main__":
    main()
