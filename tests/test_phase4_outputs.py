from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase4_metrics_manifest_parses_and_matches_headline_metrics():
    manifest = json.loads((ROOT / "results/evidence_pack/metrics_manifest.json").read_text(encoding="utf-8"))

    assert manifest["prototype3_input_rows"] == 120
    assert manifest["prototype4_execution_records"] == 240
    assert manifest["baseline_false_accepts"] == 76
    assert manifest["zero_trust_false_accepts"] == 0
    assert manifest["safety_latency_frontier_false_accepts"] == [76, 4, 0, 0]


def test_required_phase4_6_figures_exist_and_are_pngs():
    figure_names = [
        "safety_latency_frontier.png",
        "rejection_by_ambiguity.png",
        "model_comparison_heatmap.png",
        "outcome_comparison_by_mode.png",
        "false_accept_reduction.png",
        "pipeline_summary_metrics.png",
    ]

    for name in figure_names:
        path = ROOT / "figures" / name
        assert path.exists()
        assert path.stat().st_size > 1000
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_required_phase4_6_tables_exist():
    table_names = [
        "key_metrics_summary",
        "outcome_counts_by_mode",
        "safety_latency_frontier",
        "file_manifest_summary",
    ]

    for name in table_names:
        csv_path = ROOT / "tables" / f"{name}.csv"
        tex_path = ROOT / "tables" / f"{name}.tex"
        assert csv_path.exists()
        assert tex_path.exists()
        assert csv_path.stat().st_size > 0
        assert tex_path.stat().st_size > 0


def test_outcome_counts_table_matches_confirmed_values():
    with open(ROOT / "tables/outcome_counts_by_mode.csv", newline="", encoding="utf-8") as f:
        rows = {row["mode"]: row for row in csv.DictReader(f)}

    assert rows["baseline"] == {
        "mode": "baseline",
        "unsafe": "76",
        "success": "14",
        "no_op": "30",
        "rejected": "0",
        "total_rows": "120",
        "false_accepts": "76",
    }
    assert rows["zero-trust"] == {
        "mode": "zero-trust",
        "unsafe": "0",
        "success": "14",
        "no_op": "0",
        "rejected": "106",
        "total_rows": "120",
        "false_accepts": "0",
    }


def test_writing_pack_files_exist():
    names = [
        "phase4_results_summary.md",
        "dissertation_results_paragraphs.md",
        "figure_notes.md",
        "table_notes.md",
        "safe_gate_positioning_note.md",
    ]

    for name in names:
        path = ROOT / "results/writing_pack" / name
        assert path.exists()
        assert path.stat().st_size > 200
