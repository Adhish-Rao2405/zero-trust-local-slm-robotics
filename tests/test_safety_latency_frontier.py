from __future__ import annotations

import csv

from src.prototype4.execution_evaluator import Prototype3Result
from src.prototype4.safety_latency_frontier import (
    CONFIG_ORDER,
    evaluate_frontier,
    export_safety_latency_frontier,
)


def _make_result(**overrides) -> Prototype3Result:
    defaults = dict(
        command_id="C01",
        command_text="pick up the medicine cup",
        ambiguity_level="clear",
        model_name="fake_slm",
        plan_actions=[{"action": "pick", "object": "medicine_cup"}],
        schema_valid=True,
        semantic_valid=True,
        uncertainty_pass=True,
        safety_valid=True,
        latency_ms=100,
    )
    defaults.update(overrides)
    return Prototype3Result(**defaults)


def _records_by_config(results: list[Prototype3Result]):
    return {record.configuration: record for record in evaluate_frontier(results)}


def test_schema_only_accepts_unsafe_and_semantic_failure_cases():
    rows = [
        _make_result(command_id="unsafe", safety_valid=False),
        _make_result(command_id="semantic", semantic_valid=False),
    ]

    record = _records_by_config(rows)["schema_only"]

    assert record.accepted_count == 2
    assert record.unsafe_count == 1
    assert record.semantic_failure_count == 1
    assert record.false_accept_count == 2


def test_schema_semantic_rejects_semantic_invalid_but_can_accept_unsafe():
    rows = [
        _make_result(command_id="unsafe", safety_valid=False),
        _make_result(command_id="semantic", semantic_valid=False),
    ]

    record = _records_by_config(rows)["schema_semantic"]

    assert record.accepted_count == 1
    assert record.rejection_count == 1
    assert record.unsafe_count == 1
    assert record.semantic_failure_count == 0
    assert record.false_accept_count == 1


def test_schema_semantic_uncertainty_rejects_uncertainty_failure_but_can_accept_unsafe():
    rows = [
        _make_result(command_id="unsafe", safety_valid=False),
        _make_result(command_id="uncertain", uncertainty_pass=False),
    ]

    record = _records_by_config(rows)["schema_semantic_uncertainty"]

    assert record.accepted_count == 1
    assert record.rejection_count == 1
    assert record.unsafe_count == 1
    assert record.false_accept_count == 1


def test_full_zero_trust_rejects_unsafe_cases():
    rows = [
        _make_result(command_id="unsafe", safety_valid=False),
        _make_result(command_id="success"),
    ]

    record = _records_by_config(rows)["full_zero_trust"]

    assert record.accepted_count == 1
    assert record.rejection_count == 1
    assert record.success_count == 1
    assert record.unsafe_count == 0
    assert record.false_accept_count == 0


def test_no_action_plan_counts_as_no_op_and_not_accepted():
    rows = [_make_result(plan_actions=[])]

    record = _records_by_config(rows)["schema_only"]

    assert record.accepted_count == 0
    assert record.rejection_count == 1
    assert record.no_op_count == 1


def test_false_accept_count_decreases_monotonically_as_gates_are_added():
    rows = [
        _make_result(command_id="success"),
        _make_result(command_id="unsafe", safety_valid=False),
        _make_result(command_id="semantic", semantic_valid=False),
        _make_result(command_id="uncertain_unsafe", uncertainty_pass=False, safety_valid=False),
    ]

    records = evaluate_frontier(rows)
    false_accept_counts = [record.false_accept_count for record in records]

    assert [record.configuration for record in records] == CONFIG_ORDER
    assert false_accept_counts == sorted(false_accept_counts, reverse=True)


def test_output_csv_and_markdown_are_generated_with_required_columns(tmp_path):
    records = evaluate_frontier([
        _make_result(command_id="success", latency_ms=100),
        _make_result(command_id="unsafe", safety_valid=False, latency_ms=200),
    ])

    counts = export_safety_latency_frontier(records, tmp_path)

    csv_path = tmp_path / "safety_latency_frontier.csv"
    markdown_path = tmp_path / "safety_latency_frontier.md"
    assert counts == {"safety_latency_frontier_csv": 4, "safety_latency_frontier_md": 1}
    assert csv_path.exists()
    assert markdown_path.exists()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)

    assert columns == [
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
    assert len(rows) == 4
    assert "Safety-Latency Frontier" in markdown_path.read_text(encoding="utf-8")
