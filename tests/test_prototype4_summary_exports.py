from __future__ import annotations
import csv
import pytest
from pathlib import Path
from src.prototype4.execution_evaluator import ExecutionEvaluationRecord
from src.prototype4.summary_exports import (
    write_execution_comparison_csv,
    write_by_ambiguity_csv,
    write_by_model_csv,
    write_false_accepts_csv,
    export_all,
    export_prototype4_summaries,
)


def _make_record(**overrides) -> ExecutionEvaluationRecord:
    defaults = dict(
        command_id="C01",
        command_text="pick up the medicine cup",
        ambiguity_level="clear",
        model_name="fake_slm",
        mode="baseline_trust_model",
        execution_outcome="success",
        accepted=True,
        false_accept=False,
        rejection_reason="",
        plan_actions=[{"action": "pick", "object": "medicine_cup"}],
        schema_valid=True,
        semantic_valid=True,
        uncertainty_pass=True,
        safety_valid=True,
        latency_ms=100,
    )
    defaults.update(overrides)
    return ExecutionEvaluationRecord(**defaults)


def test_export_all_creates_all_four_files(tmp_path):
    record = _make_record()
    export_all([record], str(tmp_path))
    assert (tmp_path / "prototype4_execution_comparison.csv").exists()
    assert (tmp_path / "prototype4_by_ambiguity.csv").exists()
    assert (tmp_path / "prototype4_by_model.csv").exists()
    assert (tmp_path / "prototype4_false_accepts.csv").exists()


def test_execution_comparison_has_required_columns(tmp_path):
    write_execution_comparison_csv([_make_record()], str(tmp_path))
    with open(tmp_path / "prototype4_execution_comparison.csv", newline="", encoding="utf-8") as f:
        columns = csv.DictReader(f).fieldnames
    expected = [
        "command_id", "command_text", "ambiguity_level", "model_name",
        "mode", "execution_outcome", "accepted", "false_accept", "rejection_reason",
        "schema_valid", "semantic_valid", "uncertainty_pass", "safety_valid", "latency_ms",
    ]
    assert columns == expected


def test_by_ambiguity_groups_by_ambiguity_level_and_mode(tmp_path):
    r1 = _make_record(ambiguity_level="clear", mode="baseline_trust_model")
    r2 = _make_record(
        ambiguity_level="clear", mode="zero_trust_pipeline",
        execution_outcome="rejected", accepted=False,
    )
    write_by_ambiguity_csv([r1, r2], str(tmp_path))
    with open(tmp_path / "prototype4_by_ambiguity.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    expected_cols = [
        "ambiguity_level", "mode", "total", "accepted_count", "rejection_count",
        "success_count", "semantic_failure_count", "unsafe_count", "no_op_count",
        "false_accept_count", "success_rate", "false_accept_rate",
    ]
    assert columns == expected_cols
    assert len(rows) == 2  # same ambiguity_level, different modes → 2 groups


def test_by_model_groups_by_model_name_and_mode(tmp_path):
    r1 = _make_record(model_name="fake_slm", mode="baseline_trust_model")
    r2 = _make_record(
        model_name="fake_slm", mode="zero_trust_pipeline",
        execution_outcome="rejected", accepted=False,
    )
    write_by_model_csv([r1, r2], str(tmp_path))
    with open(tmp_path / "prototype4_by_model.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    expected_cols = [
        "model_name", "mode", "total", "accepted_count", "rejection_count",
        "success_count", "semantic_failure_count", "unsafe_count", "no_op_count",
        "false_accept_count", "success_rate", "false_accept_rate",
    ]
    assert columns == expected_cols
    assert len(rows) == 2  # same model_name, different modes → 2 groups


def test_false_accepts_empty_when_none(tmp_path):
    record = _make_record(false_accept=False)
    count = write_false_accepts_csv([record], str(tmp_path))
    assert count == 0
    path = tmp_path / "prototype4_false_accepts.csv"
    assert path.exists()
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 0


def test_false_accepts_one_row_when_one_exists(tmp_path):
    fa_record = _make_record(
        command_id="C01",
        false_accept=True,
        execution_outcome="unsafe",
        accepted=True,
    )
    not_fa_record = _make_record(command_id="C02", false_accept=False)
    count = write_false_accepts_csv([fa_record, not_fa_record], str(tmp_path))
    assert count == 1
    with open(tmp_path / "prototype4_false_accepts.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["command_id"] == "C01"


def test_write_execution_comparison_returns_row_count(tmp_path):
    records = [_make_record(command_id=f"C0{i}") for i in range(3)]
    count = write_execution_comparison_csv(records, str(tmp_path))
    assert count == 3


def test_by_ambiguity_success_rates_correct(tmp_path):
    r1 = _make_record(
        command_id="C01", ambiguity_level="clear", mode="baseline_trust_model",
        execution_outcome="success", accepted=True,
    )
    r2 = _make_record(
        command_id="C02", ambiguity_level="clear", mode="baseline_trust_model",
        execution_outcome="semantic_failure", accepted=True, false_accept=True,
    )
    write_by_ambiguity_csv([r1, r2], str(tmp_path))
    with open(tmp_path / "prototype4_by_ambiguity.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    row = rows[0]
    assert row["ambiguity_level"] == "clear"
    assert int(row["total"]) == 2
    assert int(row["success_count"]) == 1
    assert float(row["success_rate"]) == 0.5
