from __future__ import annotations
import pytest
from src.prototype4.execution_evaluator import (
    Prototype3Result,
    ExecutionEvaluationRecord,
    evaluate_baseline,
    evaluate_zero_trust,
    evaluate_records,
    evaluate_results,
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


def test_evaluate_records_returns_two_rows_per_result():
    result = _make_result()
    rows = evaluate_records([result])
    assert len(rows) == 2
    assert rows[0].mode == "baseline_trust_model"
    assert rows[1].mode == "zero_trust_pipeline"
    assert rows[0].execution_outcome == "success"
    assert rows[1].execution_outcome == "success"
    assert rows[0].accepted is True
    assert rows[1].accepted is True
    assert rows[0].false_accept is False
    assert rows[1].false_accept is False


def test_semantic_failure_baseline_and_zero_trust():
    result = _make_result(semantic_valid=False)
    rows = evaluate_records([result])
    baseline, zt = rows[0], rows[1]
    assert baseline.execution_outcome == "semantic_failure"
    assert baseline.accepted is True
    assert baseline.false_accept is True
    assert zt.execution_outcome == "rejected"
    assert zt.accepted is False
    assert zt.rejection_reason == "semantic_invalid"
    assert zt.false_accept is False


def test_unsafe_baseline_rejected_zero_trust():
    result = _make_result(safety_valid=False, semantic_valid=True)
    rows = evaluate_records([result])
    baseline, zt = rows[0], rows[1]
    assert baseline.execution_outcome == "unsafe"
    assert baseline.accepted is True
    assert baseline.false_accept is True
    assert zt.execution_outcome == "rejected"
    assert zt.rejection_reason == "safety_invalid"
    assert zt.false_accept is False


def test_uncertainty_fail_baseline_success_zero_trust_rejected():
    result = _make_result(uncertainty_pass=False)
    rows = evaluate_records([result])
    baseline, zt = rows[0], rows[1]
    assert baseline.execution_outcome == "success"
    assert baseline.false_accept is False
    assert zt.execution_outcome == "rejected"
    assert zt.rejection_reason == "uncertainty_failed"
    assert zt.false_accept is False


def test_empty_plan_actions_no_op_both_modes():
    result = _make_result(plan_actions=[])
    rows = evaluate_records([result])
    baseline, zt = rows[0], rows[1]
    assert baseline.execution_outcome == "no_op"
    assert baseline.rejection_reason == "no_action"
    assert zt.execution_outcome == "no_op"
    assert zt.rejection_reason == "no_action"


def test_schema_invalid_no_op_baseline_rejected_zero_trust():
    result = _make_result(schema_valid=False, plan_actions=None)
    rows = evaluate_records([result])
    baseline, zt = rows[0], rows[1]
    assert baseline.execution_outcome == "no_op"
    assert baseline.rejection_reason == "schema_invalid"
    assert zt.execution_outcome == "rejected"
    assert zt.rejection_reason == "schema_invalid"


def test_unsafe_takes_precedence_over_semantic_failure_in_baseline():
    result = _make_result(safety_valid=False, semantic_valid=False)
    baseline = evaluate_baseline(result)
    assert baseline.execution_outcome == "unsafe"


def test_evaluate_results_is_alias():
    result = _make_result()
    assert evaluate_results([result]) == evaluate_records([result])
