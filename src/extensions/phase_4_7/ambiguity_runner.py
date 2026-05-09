from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from src.extensions.phase_4_7.ambiguity_gate import evaluate_ambiguity


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BENCHMARK = REPO_ROOT / "datasets" / "prototype3_results" / "benchmark_v1.json"
OUTPUT_DIR = REPO_ROOT / "results" / "prototype4_extensions" / "phase_4_7"
RESULTS_CSV = OUTPUT_DIR / "ambiguity_gate_results.csv"
SUMMARY_JSON = OUTPUT_DIR / "ambiguity_gate_summary.json"

FALLBACK_COMMANDS = [
    {"command_id": "E01", "command": "Pick the red cube and place it in bin A"},
    {"command_id": "E02", "command": "Move it there"},
    {"command_id": "E03", "command": "Sort everything properly"},
]


def run_ambiguity_gate(
    benchmark_path: str | Path = DEFAULT_BENCHMARK,
    output_dir: str | Path = OUTPUT_DIR,
) -> dict[str, int | dict[str, int]]:
    commands = _load_commands(Path(benchmark_path))
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    rows = []
    for item in commands:
        result = evaluate_ambiguity(item["command"])
        rows.append({
            "command_id": item["command_id"],
            "command": result["command"],
            "ambiguity_score": result["ambiguity_score"],
            "decision": result["decision"],
            "reasons": ";".join(result["reasons"]),
        })

    decision_counts = Counter(row["decision"] for row in rows)
    mean_score = sum(float(row["ambiguity_score"]) for row in rows) / len(rows) if rows else 0.0
    summary = {
        "total_commands": len(rows),
        "decision_counts": dict(sorted(decision_counts.items())),
        "mean_ambiguity_score": round(mean_score, 4),
        "source": str(Path(benchmark_path)),
    }

    _write_results_csv(output / RESULTS_CSV.name, rows)
    (output / SUMMARY_JSON.name).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    summary = run_ambiguity_gate()
    print(f"Ambiguity gate commands evaluated: {summary['total_commands']}")
    print(f"Decision counts: {summary['decision_counts']}")


def _load_commands(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return FALLBACK_COMMANDS
    payload = json.loads(path.read_text(encoding="utf-8"))
    commands = []
    for index, item in enumerate(payload):
        command = item.get("command") or item.get("command_text")
        if not command:
            continue
        commands.append({
            "command_id": str(item.get("id") or item.get("command_id") or f"C{index + 1:02d}"),
            "command": command,
        })
    return commands


def _write_results_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["command_id", "command", "ambiguity_score", "decision", "reasons"],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
