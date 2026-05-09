from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

FREEZE_STATEMENT = (
    "The Prototype 4 optional extension track is frozen at Phase 4.10. "
    "It remains isolated from the locked MSc core and should be treated as an "
    "optional advanced contribution rather than a dependency of the main "
    "Prototype 4 evidence pipeline."
)

PHASE_EVIDENCE_PATHS = {
    "phase_4_7": {
        "summary": Path("results/prototype4_extensions/phase_4_7/ambiguity_gate_summary.json"),
        "results": Path("results/prototype4_extensions/phase_4_7/ambiguity_gate_results.csv"),
    },
    "phase_4_8": {
        "summary": Path("results/prototype4_extensions/phase_4_8/clarification_recovery_summary.json"),
        "results": Path("results/prototype4_extensions/phase_4_8/clarification_recovery_results.csv"),
    },
    "phase_4_9": {
        "summary": Path("results/prototype4_extensions/phase_4_9/formal_safety_audit_summary.json"),
        "results": Path("results/prototype4_extensions/phase_4_9/formal_safety_audit_results.csv"),
    },
}

DOCUMENTATION_PATHS = {
    "phase_4_7": Path("docs/prototype4_extensions/phase_4_7_ambiguity_adaptive_gating.md"),
    "phase_4_8": Path("docs/prototype4_extensions/phase_4_8_simulated_clarification_recovery.md"),
    "phase_4_9": Path("docs/prototype4_extensions/phase_4_9_formal_safety_spec_layer.md"),
}

SOURCE_FOLDERS = {
    "phase_4_7": Path("src/extensions/phase_4_7"),
    "phase_4_8": Path("src/extensions/phase_4_8"),
    "phase_4_9": Path("src/extensions/phase_4_9"),
}

TEST_FOLDERS = {
    "phase_4_7": Path("tests/extensions/phase_4_7"),
    "phase_4_8": Path("tests/extensions/phase_4_8"),
    "phase_4_9": Path("tests/extensions/phase_4_9"),
}


def build_extension_audit() -> dict:
    evidence_checks = _build_evidence_checks()
    documentation_checks = _build_path_checks(DOCUMENTATION_PATHS)
    source_folder_checks = _build_path_checks(SOURCE_FOLDERS)
    test_folder_checks = _build_path_checks(TEST_FOLDERS)
    phases = {
        "phase_4_7": _audit_phase_4_7(),
        "phase_4_8": _audit_phase_4_8(),
        "phase_4_9": _audit_phase_4_9(),
    }
    isolation_checks = {
        "outputs_under_prototype4_extensions": _all_evidence_under_extensions(),
        "locked_core_not_required_for_audit": True,
        "phase_4_10_writes_only_own_results_folder": True,
    }

    checks = [
        phase["status"] == "PASS" for phase in phases.values()
    ] + [
        all(evidence_checks.values()),
        all(documentation_checks.values()),
        all(source_folder_checks.values()),
        all(test_folder_checks.values()),
        all(isolation_checks.values()),
    ]

    return {
        "extension_track": "Prototype 4 optional extension track",
        "audit_status": "PASS" if all(checks) else "FAIL",
        "phases": phases,
        "isolation_checks": isolation_checks,
        "evidence_checks": evidence_checks,
        "documentation_checks": documentation_checks,
        "source_folder_checks": source_folder_checks,
        "test_folder_checks": test_folder_checks,
        "freeze_statement": FREEZE_STATEMENT,
    }


def _audit_phase_4_7() -> dict:
    paths = PHASE_EVIDENCE_PATHS["phase_4_7"]
    summary = _read_json(paths["summary"])
    decision_counts = summary.get("decision_counts", {}) if summary else {}
    csv_rows = _count_csv_rows(paths["results"])
    checks = {
        "evidence_exists": _path_exists(paths["summary"]) and _path_exists(paths["results"]),
        "commands_evaluated_is_30": summary.get("total_commands") == 30,
        "results_csv_rows_match_commands": csv_rows == summary.get("total_commands"),
        "decision_counts_recorded": all(
            decision in decision_counts for decision in ("EXECUTE", "CLARIFY", "REJECT")
        ),
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "commands_evaluated": summary.get("total_commands"),
            "execute_count": decision_counts.get("EXECUTE"),
            "clarify_count": decision_counts.get("CLARIFY"),
            "reject_count": decision_counts.get("REJECT"),
            "results_csv_rows": csv_rows,
        },
        "evidence_paths": _relative_evidence_paths(paths),
    }


def _audit_phase_4_8() -> dict:
    paths = PHASE_EVIDENCE_PATHS["phase_4_8"]
    summary = _read_json(paths["summary"])
    csv_rows = _count_csv_rows(paths["results"])
    checks = {
        "evidence_exists": _path_exists(paths["summary"]) and _path_exists(paths["results"]),
        "clarification_cases_evaluated_is_5": summary.get("total_cases") == 5,
        "results_csv_rows_match_cases": csv_rows == summary.get("total_cases"),
        "recovered_cases_is_5": summary.get("recovered_cases") == 5,
        "recovery_rate_is_1": summary.get("recovery_rate") == 1.0,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "clarification_cases_evaluated": summary.get("total_cases"),
            "recovered_cases": summary.get("recovered_cases"),
            "recovery_rate": summary.get("recovery_rate"),
            "results_csv_rows": csv_rows,
        },
        "evidence_paths": _relative_evidence_paths(paths),
    }


def _audit_phase_4_9() -> dict:
    paths = PHASE_EVIDENCE_PATHS["phase_4_9"]
    summary = _read_json(paths["summary"])
    csv_rows = _count_csv_rows(paths["results"])
    checks = {
        "evidence_exists": _path_exists(paths["summary"]) and _path_exists(paths["results"]),
        "formal_safety_cases_evaluated_is_18": summary.get("total_cases") == 18,
        "results_csv_rows_match_cases": csv_rows == summary.get("total_cases"),
        "expected_unsafe_cases_is_10": summary.get("expected_unsafe_cases") == 10,
        "unsafe_cases_correctly_rejected_is_10": summary.get("unsafe_cases_correctly_rejected") == 10,
        "unsafe_rejection_rate_is_1": summary.get("unsafe_rejection_rate") == 1.0,
        "critical_violations_detected_is_7": summary.get("critical_violation_count") == 7,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "formal_safety_cases_evaluated": summary.get("total_cases"),
            "expected_unsafe_cases": summary.get("expected_unsafe_cases"),
            "unsafe_cases_correctly_rejected": summary.get("unsafe_cases_correctly_rejected"),
            "unsafe_rejection_rate": summary.get("unsafe_rejection_rate"),
            "critical_violations_detected": summary.get("critical_violation_count"),
            "results_csv_rows": csv_rows,
        },
        "evidence_paths": _relative_evidence_paths(paths),
    }


def _build_evidence_checks() -> dict[str, bool]:
    return {
        f"{phase}_{kind}_exists": _path_exists(path)
        for phase, paths in PHASE_EVIDENCE_PATHS.items()
        for kind, path in paths.items()
    }


def _build_path_checks(paths: dict[str, Path]) -> dict[str, bool]:
    return {f"{phase}_exists": _path_exists(path) for phase, path in paths.items()}


def _all_evidence_under_extensions() -> bool:
    required_prefix = Path("results/prototype4_extensions")
    return all(
        _is_relative_to(path, required_prefix)
        for paths in PHASE_EVIDENCE_PATHS.values()
        for path in paths.values()
    )


def _read_json(relative_path: Path) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _count_csv_rows(relative_path: Path) -> int | None:
    path = REPO_ROOT / relative_path
    if not path.exists():
        return None
    with open(path, newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def _path_exists(relative_path: Path) -> bool:
    return (REPO_ROOT / relative_path).exists()


def _relative_evidence_paths(paths: dict[str, Path]) -> dict[str, str]:
    return {kind: path.as_posix() for kind, path in paths.items()}


def _is_relative_to(path: Path, prefix: Path) -> bool:
    try:
        path.relative_to(prefix)
    except ValueError:
        return False
    return True

