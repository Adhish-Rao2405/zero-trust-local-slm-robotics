from __future__ import annotations

import csv
import json

from src.extensions.phase_4_7.ambiguity_gate import evaluate_ambiguity
from src.extensions.phase_4_7.ambiguity_policy import CLARIFY, EXECUTE, REJECT
from src.extensions.phase_4_7.ambiguity_runner import run_ambiguity_gate


def test_gate_output_contains_required_fields():
    result = evaluate_ambiguity("Move it there")

    assert set(result) == {"command", "ambiguity_score", "decision", "reasons"}
    assert result["command"] == "Move it there"
    assert isinstance(result["ambiguity_score"], float)
    assert isinstance(result["reasons"], list)


def test_clear_command_is_executable():
    result = evaluate_ambiguity("Move the blue cylinder to the left tray")

    assert result["decision"] == EXECUTE
    assert result["ambiguity_score"] <= 0.30


def test_moderately_ambiguous_command_is_clarified():
    result = evaluate_ambiguity("Pick up the object")

    assert result["decision"] == CLARIFY
    assert "vague_object_reference" in result["reasons"]


def test_highly_ambiguous_command_is_rejected_or_clarified():
    result = evaluate_ambiguity("Move it there")

    assert result["decision"] in {CLARIFY, REJECT}
    assert result["ambiguity_score"] > 0.30


def test_runner_writes_only_extension_outputs(tmp_path):
    benchmark = tmp_path / "benchmark.json"
    benchmark.write_text(
        json.dumps([
            {"id": "C01", "command": "Pick the red cube and place it in bin A"},
            {"id": "C02", "command": "Move it there"},
        ]),
        encoding="utf-8",
    )
    output_dir = tmp_path / "phase_4_7"

    summary = run_ambiguity_gate(benchmark, output_dir)

    assert summary["total_commands"] == 2
    assert (output_dir / "ambiguity_gate_results.csv").exists()
    assert (output_dir / "ambiguity_gate_summary.json").exists()

    with open(output_dir / "ambiguity_gate_results.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [row["command_id"] for row in rows] == ["C01", "C02"]
