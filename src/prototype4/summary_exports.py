from __future__ import annotations
import csv
from pathlib import Path
from collections import defaultdict
from src.prototype4.execution_evaluator import ExecutionEvaluationRecord

_COMPARISON_COLUMNS = [
    "command_id", "command_text", "ambiguity_level", "model_name",
    "mode", "execution_outcome", "accepted", "false_accept", "rejection_reason",
    "schema_valid", "semantic_valid", "uncertainty_pass", "safety_valid", "latency_ms",
]

_BY_AMBIGUITY_COLUMNS = [
    "ambiguity_level", "mode", "total",
    "accepted_count", "rejection_count",
    "success_count", "semantic_failure_count", "unsafe_count", "no_op_count",
    "false_accept_count", "success_rate", "false_accept_rate",
]

_BY_MODEL_COLUMNS = [
    "model_name", "mode", "total",
    "accepted_count", "rejection_count",
    "success_count", "semantic_failure_count", "unsafe_count", "no_op_count",
    "false_accept_count", "success_rate", "false_accept_rate",
]

_FALSE_ACCEPTS_COLUMNS = [
    "command_id", "command_text", "ambiguity_level", "model_name",
    "mode", "execution_outcome", "rejection_reason",
    "schema_valid", "semantic_valid", "uncertainty_pass", "safety_valid", "latency_ms",
]


def _aggregate_group(group: list[ExecutionEvaluationRecord]) -> dict:
    total = len(group)
    accepted_count = sum(1 for r in group if r.accepted)
    rejection_count = total - accepted_count
    success_count = sum(1 for r in group if r.execution_outcome == "success")
    semantic_failure_count = sum(1 for r in group if r.execution_outcome == "semantic_failure")
    unsafe_count = sum(1 for r in group if r.execution_outcome == "unsafe")
    no_op_count = sum(1 for r in group if r.execution_outcome == "no_op")
    false_accept_count = sum(1 for r in group if r.false_accept)
    return {
        "total": total,
        "accepted_count": accepted_count,
        "rejection_count": rejection_count,
        "success_count": success_count,
        "semantic_failure_count": semantic_failure_count,
        "unsafe_count": unsafe_count,
        "no_op_count": no_op_count,
        "false_accept_count": false_accept_count,
        "success_rate": success_count / total if total else 0.0,
        "false_accept_rate": false_accept_count / total if total else 0.0,
    }


def write_execution_comparison_csv(
    records: list[ExecutionEvaluationRecord], output_path: str
) -> int:
    path = Path(output_path) / "prototype4_execution_comparison.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_COMPARISON_COLUMNS)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "command_id": r.command_id,
                "command_text": r.command_text,
                "ambiguity_level": r.ambiguity_level,
                "model_name": r.model_name,
                "mode": r.mode,
                "execution_outcome": r.execution_outcome,
                "accepted": r.accepted,
                "false_accept": r.false_accept,
                "rejection_reason": r.rejection_reason,
                "schema_valid": r.schema_valid,
                "semantic_valid": r.semantic_valid,
                "uncertainty_pass": r.uncertainty_pass,
                "safety_valid": r.safety_valid,
                "latency_ms": r.latency_ms,
            })
    return len(records)


def write_by_ambiguity_csv(
    records: list[ExecutionEvaluationRecord], output_path: str
) -> int:
    path = Path(output_path) / "prototype4_by_ambiguity.csv"
    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        groups[(r.ambiguity_level, r.mode)].append(r)

    rows = []
    for (ambiguity_level, mode), group in groups.items():
        agg = _aggregate_group(group)
        rows.append({"ambiguity_level": ambiguity_level, "mode": mode, **agg})

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_BY_AMBIGUITY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_by_model_csv(
    records: list[ExecutionEvaluationRecord], output_path: str
) -> int:
    path = Path(output_path) / "prototype4_by_model.csv"
    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        groups[(r.model_name, r.mode)].append(r)

    rows = []
    for (model_name, mode), group in groups.items():
        agg = _aggregate_group(group)
        rows.append({"model_name": model_name, "mode": mode, **agg})

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_BY_MODEL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_false_accepts_csv(
    records: list[ExecutionEvaluationRecord], output_path: str
) -> int:
    path = Path(output_path) / "prototype4_false_accepts.csv"
    false_accepts = [r for r in records if r.false_accept]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FALSE_ACCEPTS_COLUMNS)
        writer.writeheader()
        for r in false_accepts:
            writer.writerow({
                "command_id": r.command_id,
                "command_text": r.command_text,
                "ambiguity_level": r.ambiguity_level,
                "model_name": r.model_name,
                "mode": r.mode,
                "execution_outcome": r.execution_outcome,
                "rejection_reason": r.rejection_reason,
                "schema_valid": r.schema_valid,
                "semantic_valid": r.semantic_valid,
                "uncertainty_pass": r.uncertainty_pass,
                "safety_valid": r.safety_valid,
                "latency_ms": r.latency_ms,
            })
    return len(false_accepts)


def export_prototype4_summaries(
    records: list[ExecutionEvaluationRecord], output_dir: str = "results/summaries"
) -> dict[str, int]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return {
        "execution_comparison": write_execution_comparison_csv(records, output_dir),
        "by_ambiguity": write_by_ambiguity_csv(records, output_dir),
        "by_model": write_by_model_csv(records, output_dir),
        "false_accepts": write_false_accepts_csv(records, output_dir),
    }


# Backward-compatibility alias
export_all = export_prototype4_summaries
