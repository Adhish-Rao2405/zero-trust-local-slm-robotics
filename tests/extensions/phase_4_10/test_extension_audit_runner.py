from __future__ import annotations

import csv
import json
from pathlib import Path

from src.extensions.phase_4_10.extension_audit import REPO_ROOT
from src.extensions.phase_4_10.extension_audit_runner import (
    OUTPUT_DIR,
    run_extension_audit,
)


PRIOR_EVIDENCE_FILES = [
    Path("results/prototype4_extensions/phase_4_7/ambiguity_gate_summary.json"),
    Path("results/prototype4_extensions/phase_4_7/ambiguity_gate_results.csv"),
    Path("results/prototype4_extensions/phase_4_8/clarification_recovery_summary.json"),
    Path("results/prototype4_extensions/phase_4_8/clarification_recovery_results.csv"),
    Path("results/prototype4_extensions/phase_4_9/formal_safety_audit_summary.json"),
    Path("results/prototype4_extensions/phase_4_9/formal_safety_audit_results.csv"),
]


def test_runner_writes_only_phase_4_10_outputs(tmp_path):
    output_dir = tmp_path / "results" / "prototype4_extensions" / "phase_4_10"

    audit = run_extension_audit(output_dir=output_dir)

    assert audit["audit_status"] == "PASS"
    assert (output_dir / "extension_audit_table.csv").exists()
    assert (output_dir / "extension_audit_summary.json").exists()
    assert {path.name for path in output_dir.iterdir()} == {
        "extension_audit_table.csv",
        "extension_audit_summary.json",
    }
    assert "prototype4_extensions" in OUTPUT_DIR.parts
    assert OUTPUT_DIR.parts[-1] == "phase_4_10"


def test_runner_writes_valid_json_summary(tmp_path):
    run_extension_audit(output_dir=tmp_path)

    parsed = json.loads((tmp_path / "extension_audit_summary.json").read_text(encoding="utf-8"))
    assert parsed["audit_status"] == "PASS"
    assert "freeze_statement" in parsed
    assert set(parsed["phases"]) == {"phase_4_7", "phase_4_8", "phase_4_9"}


def test_runner_writes_csv_table(tmp_path):
    run_extension_audit(output_dir=tmp_path)

    with open(tmp_path / "extension_audit_table.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows
    assert set(rows[0]) == {"phase", "component", "status", "metric", "value", "evidence_path"}
    assert any(
        row["phase"] == "phase_4_7"
        and row["metric"] == "commands_evaluated"
        and row["value"] == "30"
        for row in rows
    )
    assert any(
        row["phase"] == "phase_4_10"
        and row["component"] == "freeze"
        and row["metric"] == "audit_status"
        and row["value"] == "PASS"
        for row in rows
    )


def test_runner_does_not_overwrite_prior_extension_evidence(tmp_path):
    before = {
        path: (REPO_ROOT / path).read_bytes()
        for path in PRIOR_EVIDENCE_FILES
    }

    run_extension_audit(output_dir=tmp_path)

    after = {
        path: (REPO_ROOT / path).read_bytes()
        for path in PRIOR_EVIDENCE_FILES
    }
    assert after == before

