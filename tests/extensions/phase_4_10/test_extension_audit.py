from __future__ import annotations

from src.extensions.phase_4_10.extension_audit import (
    FREEZE_STATEMENT,
    build_extension_audit,
)


def test_build_extension_audit_returns_dictionary():
    audit = build_extension_audit()

    assert isinstance(audit, dict)
    assert audit["extension_track"] == "Prototype 4 optional extension track"


def test_audit_status_is_pass_when_required_files_exist():
    audit = build_extension_audit()

    assert audit["audit_status"] == "PASS"
    assert all(phase["status"] == "PASS" for phase in audit["phases"].values())
    assert all(audit["evidence_checks"].values())
    assert all(audit["documentation_checks"].values())
    assert all(audit["source_folder_checks"].values())
    assert all(audit["test_folder_checks"].values())
    assert all(audit["isolation_checks"].values())


def test_required_extension_phases_are_present():
    audit = build_extension_audit()

    assert set(audit["phases"]) == {"phase_4_7", "phase_4_8", "phase_4_9"}


def test_phase_4_7_metrics_are_audited():
    phase = build_extension_audit()["phases"]["phase_4_7"]

    assert phase["metrics"]["commands_evaluated"] == 30
    assert phase["metrics"]["execute_count"] == 24
    assert phase["metrics"]["clarify_count"] == 4
    assert phase["metrics"]["reject_count"] == 2
    assert phase["checks"]["decision_counts_recorded"]


def test_phase_4_8_metrics_are_audited():
    phase = build_extension_audit()["phases"]["phase_4_8"]

    assert phase["metrics"]["clarification_cases_evaluated"] == 5
    assert phase["metrics"]["recovered_cases"] == 5
    assert phase["metrics"]["recovery_rate"] == 1.0


def test_phase_4_9_metrics_are_audited():
    phase = build_extension_audit()["phases"]["phase_4_9"]

    assert phase["metrics"]["formal_safety_cases_evaluated"] == 18
    assert phase["metrics"]["expected_unsafe_cases"] == 10
    assert phase["metrics"]["unsafe_cases_correctly_rejected"] == 10
    assert phase["metrics"]["unsafe_rejection_rate"] == 1.0
    assert phase["metrics"]["critical_violations_detected"] == 7


def test_freeze_statement_is_present():
    audit = build_extension_audit()

    assert audit["freeze_statement"] == FREEZE_STATEMENT
    assert "frozen at Phase 4.10" in audit["freeze_statement"]
    assert "optional advanced contribution" in audit["freeze_statement"]

