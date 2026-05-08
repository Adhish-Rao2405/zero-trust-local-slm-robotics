from __future__ import annotations

import csv
import json

import pytest

from src.prototype4.execution_evaluator import Prototype3Result, evaluate_records
from src.prototype4.loaders import load_prototype3_results_csv, load_prototype3_results_json


PROTOTYPE3_JSONL = "datasets/prototype3_results/rq5_comparison.jsonl"


def test_load_real_prototype3_jsonl_maps_reference_fields():
    results = load_prototype3_results_json(PROTOTYPE3_JSONL)

    assert len(results) == 120
    assert all(isinstance(result, Prototype3Result) for result in results)

    first = results[0]
    assert first.command_id == "C01"
    assert first.command_text == "Pick up the medicine cup"
    assert first.ambiguity_level == "clear"
    assert first.model_name == "foundry:qwen2.5-coder-0.5b:cpu"
    assert first.schema_valid is True
    assert first.semantic_valid is False
    assert first.uncertainty_pass is True
    assert first.safety_valid is False
    assert first.latency_ms == 4571
    assert first.plan_actions == [{"action": "pick", "object": "medicine cup"}]


def test_real_prototype3_jsonl_contains_expected_evidence_mix():
    results = load_prototype3_results_json(PROTOTYPE3_JSONL)

    model_names = {result.model_name for result in results}
    ambiguity_levels = {result.ambiguity_level for result in results}

    assert len(model_names) == 4
    assert {"clear", "moderate", "high"} <= ambiguity_levels
    assert any(r.schema_valid and r.semantic_valid and r.uncertainty_pass and r.safety_valid for r in results)
    assert any(r.schema_valid and not r.semantic_valid for r in results)
    assert any(r.schema_valid and not r.safety_valid for r in results)
    assert any(r.schema_valid and r.semantic_valid and not r.uncertainty_pass for r in results)
    assert any(not r.schema_valid and not r.plan_actions for r in results)


def test_missing_plan_actions_is_normalised_to_empty_list(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(
        json.dumps([
            {
                "command_id": "C01",
                "command_text": "wait",
                "ambiguity_level": "clear",
                "model_name": "local_slm_alpha",
                "schema_valid": True,
                "semantic_valid": True,
                "uncertainty_pass": True,
                "safety_valid": True,
                "latency_ms": 10,
            }
        ]),
        encoding="utf-8",
    )

    result = load_prototype3_results_json(path)[0]

    assert result.plan_actions == []
    assert result.latency_ms == 10


def test_missing_required_field_raises_clear_value_error(tmp_path):
    path = tmp_path / "bad_results.json"
    path.write_text(
        json.dumps([
            {
                "command_id": "C01",
                "ambiguity_level": "clear",
                "model_name": "local_slm_alpha",
                "schema_valid": True,
                "semantic_valid": True,
                "uncertainty_pass": True,
                "safety_valid": True,
            }
        ]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="row 0.*missing required field.*command_text"):
        load_prototype3_results_json(path)


def test_prototype3_aliases_are_supported_in_wrapped_json(tmp_path):
    path = tmp_path / "wrapped_results.json"
    path.write_text(
        json.dumps({
            "results": [
                {
                    "command_id": "C01",
                    "command_text": "pick up the cup",
                    "difficulty": "clear",
                    "model": "foundry:test",
                    "raw_response": "{\"actions\":[{\"action\":\"pick\",\"object\":\"cup\"}]}",
                    "schema_valid": True,
                    "semantic_score": 1.0,
                    "uncertainty_flag": False,
                    "safety_valid": True,
                }
            ]
        }),
        encoding="utf-8",
    )

    result = load_prototype3_results_json(path)[0]

    assert result.ambiguity_level == "clear"
    assert result.model_name == "foundry:test"
    assert result.semantic_valid is True
    assert result.uncertainty_pass is True
    assert result.plan_actions == [{"action": "pick", "object": "cup"}]
    assert result.latency_ms is None


def test_load_prototype3_results_csv_maps_row_level_aliases(tmp_path):
    path = tmp_path / "results.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "command_id",
                "command_text",
                "difficulty",
                "model",
                "raw_response",
                "schema_valid",
                "semantic_score",
                "uncertainty_flag",
                "safety_valid",
                "latency_ms",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "command_id": "C01",
            "command_text": "Open the gripper",
            "difficulty": "clear",
            "model": "foundry:test",
            "raw_response": "{\"actions\":[{\"action\":\"opengripper\"}]}",
            "schema_valid": "true",
            "semantic_score": "1.0",
            "uncertainty_flag": "false",
            "safety_valid": "true",
            "latency_ms": "42",
        })

    result = load_prototype3_results_csv(path)[0]

    assert result.model_name == "foundry:test"
    assert result.ambiguity_level == "clear"
    assert result.plan_actions == [{"action": "opengripper"}]
    assert result.semantic_valid is True
    assert result.uncertainty_pass is True
    assert result.latency_ms == 42


def test_loaded_real_prototype3_jsonl_evaluates_to_two_records_per_input():
    results = load_prototype3_results_json(PROTOTYPE3_JSONL)
    records = evaluate_records(results)

    assert len(records) == 240
    assert {record.mode for record in records} == {"baseline_trust_model", "zero_trust_pipeline"}
