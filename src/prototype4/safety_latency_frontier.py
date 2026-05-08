from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import median

from src.prototype4.execution_evaluator import Prototype3Result


CONFIG_ORDER = [
    "schema_only",
    "schema_semantic",
    "schema_semantic_uncertainty",
    "full_zero_trust",
]

_CSV_COLUMNS = [
    "configuration",
    "total",
    "accepted_count",
    "rejection_count",
    "success_count",
    "semantic_failure_count",
    "unsafe_count",
    "no_op_count",
    "false_accept_count",
    "accepted_rate",
    "rejection_rate",
    "success_rate",
    "false_accept_rate",
    "mean_latency_ms",
    "median_latency_ms",
]


@dataclass
class FrontierRecord:
    configuration: str
    total: int
    accepted_count: int
    rejection_count: int
    success_count: int
    semantic_failure_count: int
    unsafe_count: int
    no_op_count: int
    false_accept_count: int
    accepted_rate: float
    rejection_rate: float
    success_rate: float
    false_accept_rate: float
    mean_latency_ms: float
    median_latency_ms: float


def evaluate_frontier(results: list[Prototype3Result]) -> list[FrontierRecord]:
    return [_evaluate_configuration(name, results) for name in CONFIG_ORDER]


def export_safety_latency_frontier(
    records: list[FrontierRecord],
    output_dir: str | Path = "results/summaries",
) -> dict[str, int]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    csv_count = write_frontier_csv(records, path / "safety_latency_frontier.csv")
    write_frontier_markdown(records, path / "safety_latency_frontier.md")
    return {"safety_latency_frontier_csv": csv_count, "safety_latency_frontier_md": 1}


def write_frontier_csv(records: list[FrontierRecord], output_path: str | Path) -> int:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(_record_to_row(record))
    return len(records)


def write_frontier_markdown(records: list[FrontierRecord], output_path: str | Path) -> None:
    lines = [
        "# Safety-Latency Frontier",
        "",
        "| Configuration | Accepted | Rejected | Success | Unsafe | Semantic failure | False accepts | Mean latency ms | Median latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in records:
        lines.append(
            "| "
            f"{record.configuration} | "
            f"{record.accepted_count} | "
            f"{record.rejection_count} | "
            f"{record.success_count} | "
            f"{record.unsafe_count} | "
            f"{record.semantic_failure_count} | "
            f"{record.false_accept_count} | "
            f"{record.mean_latency_ms:.2f} | "
            f"{record.median_latency_ms:.2f} |"
        )

    lines.extend([
        "",
        "False accepts are accepted plans whose deterministic execution outcome is unsafe or semantic_failure.",
        "Latency is calculated over accepted rows for each configuration.",
    ])
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _evaluate_configuration(
    configuration: str,
    results: list[Prototype3Result],
) -> FrontierRecord:
    total = len(results)
    accepted_count = 0
    rejection_count = 0
    success_count = 0
    semantic_failure_count = 0
    unsafe_count = 0
    no_op_count = 0
    false_accept_count = 0
    latencies: list[int] = []

    for result in results:
        accepted, outcome = _evaluate_result(configuration, result)
        if accepted:
            accepted_count += 1
            if result.latency_ms is not None:
                latencies.append(result.latency_ms)
        else:
            rejection_count += 1

        if outcome == "success":
            success_count += 1
        elif outcome == "semantic_failure":
            semantic_failure_count += 1
        elif outcome == "unsafe":
            unsafe_count += 1
        elif outcome == "no_op":
            no_op_count += 1

        if accepted and outcome in {"semantic_failure", "unsafe"}:
            false_accept_count += 1

    return FrontierRecord(
        configuration=configuration,
        total=total,
        accepted_count=accepted_count,
        rejection_count=rejection_count,
        success_count=success_count,
        semantic_failure_count=semantic_failure_count,
        unsafe_count=unsafe_count,
        no_op_count=no_op_count,
        false_accept_count=false_accept_count,
        accepted_rate=_rate(accepted_count, total),
        rejection_rate=_rate(rejection_count, total),
        success_rate=_rate(success_count, total),
        false_accept_rate=_rate(false_accept_count, total),
        mean_latency_ms=_mean(latencies),
        median_latency_ms=float(median(latencies)) if latencies else 0.0,
    )


def _evaluate_result(configuration: str, result: Prototype3Result) -> tuple[bool, str]:
    if not result.plan_actions:
        return False, "no_op"
    if not _passes_configuration(configuration, result):
        return False, "rejected"
    if not result.safety_valid:
        return True, "unsafe"
    if not result.semantic_valid:
        return True, "semantic_failure"
    return True, "success"


def _passes_configuration(configuration: str, result: Prototype3Result) -> bool:
    if configuration == "schema_only":
        return result.schema_valid
    if configuration == "schema_semantic":
        return result.schema_valid and result.semantic_valid
    if configuration == "schema_semantic_uncertainty":
        return result.schema_valid and result.semantic_valid and result.uncertainty_pass
    if configuration == "full_zero_trust":
        return (
            result.schema_valid
            and result.semantic_valid
            and result.uncertainty_pass
            and result.safety_valid
        )
    raise ValueError(f"Unknown frontier configuration: {configuration}")


def _record_to_row(record: FrontierRecord) -> dict[str, object]:
    return {
        "configuration": record.configuration,
        "total": record.total,
        "accepted_count": record.accepted_count,
        "rejection_count": record.rejection_count,
        "success_count": record.success_count,
        "semantic_failure_count": record.semantic_failure_count,
        "unsafe_count": record.unsafe_count,
        "no_op_count": record.no_op_count,
        "false_accept_count": record.false_accept_count,
        "accepted_rate": record.accepted_rate,
        "rejection_rate": record.rejection_rate,
        "success_rate": record.success_rate,
        "false_accept_rate": record.false_accept_rate,
        "mean_latency_ms": record.mean_latency_ms,
        "median_latency_ms": record.median_latency_ms,
    }


def _rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def _mean(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0.0
