from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.extensions.phase_4_10.extension_audit import (
    REPO_ROOT,
    build_extension_audit,
)


OUTPUT_DIR = REPO_ROOT / "results" / "prototype4_extensions" / "phase_4_10"
AUDIT_CSV = OUTPUT_DIR / "extension_audit_table.csv"
AUDIT_JSON = OUTPUT_DIR / "extension_audit_summary.json"

FIELDNAMES = ["phase", "component", "status", "metric", "value", "evidence_path"]


def run_extension_audit(output_dir: str | Path = OUTPUT_DIR) -> dict:
    audit = build_extension_audit()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_audit_csv(output / AUDIT_CSV.name, audit)
    (output / AUDIT_JSON.name).write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return audit


def main() -> None:
    audit = run_extension_audit()
    phases = audit["phases"]
    print(f"Prototype 4 optional extension audit: {audit['audit_status']}")
    print("")
    print("Phase 4.7:")
    print(f"- evidence: {phases['phase_4_7']['status']}")
    print(f"- commands evaluated: {phases['phase_4_7']['metrics']['commands_evaluated']}")
    print(f"- decision counts recorded: {_status(phases['phase_4_7']['checks']['decision_counts_recorded'])}")
    print("")
    print("Phase 4.8:")
    print(f"- evidence: {phases['phase_4_8']['status']}")
    print(
        "- clarification cases evaluated: "
        f"{phases['phase_4_8']['metrics']['clarification_cases_evaluated']}"
    )
    print(f"- recovery rate: {phases['phase_4_8']['metrics']['recovery_rate']:.2f}")
    print("")
    print("Phase 4.9:")
    print(f"- evidence: {phases['phase_4_9']['status']}")
    print(
        "- formal safety cases evaluated: "
        f"{phases['phase_4_9']['metrics']['formal_safety_cases_evaluated']}"
    )
    print(f"- unsafe rejection rate: {phases['phase_4_9']['metrics']['unsafe_rejection_rate']:.2f}")
    print("")
    print("Freeze status:")
    print(audit["audit_status"])


def _write_audit_csv(path: Path, audit: dict) -> None:
    rows = _audit_rows(audit)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _audit_rows(audit: dict) -> list[dict]:
    rows = []
    for phase, phase_audit in audit["phases"].items():
        evidence_path = phase_audit["evidence_paths"]["summary"]
        for metric, value in phase_audit["metrics"].items():
            rows.append(_row(phase, "evidence", phase_audit["status"], metric, value, evidence_path))
        for check, passed in phase_audit["checks"].items():
            rows.append(_row(phase, "check", _status(passed), check, passed, evidence_path))

    for metric, passed in audit["isolation_checks"].items():
        rows.append(_row("global", "isolation", _status(passed), metric, passed, "results/prototype4_extensions/"))
    for metric, passed in audit["documentation_checks"].items():
        rows.append(_row("global", "documentation", _status(passed), metric, passed, "docs/prototype4_extensions/"))
    for metric, passed in audit["source_folder_checks"].items():
        rows.append(_row("global", "source", _status(passed), metric, passed, "src/extensions/"))
    for metric, passed in audit["test_folder_checks"].items():
        rows.append(_row("global", "tests", _status(passed), metric, passed, "tests/extensions/"))

    rows.append(
        _row(
            "phase_4_10",
            "freeze",
            audit["audit_status"],
            "audit_status",
            audit["audit_status"],
            "results/prototype4_extensions/phase_4_10/extension_audit_summary.json",
        )
    )
    rows.append(
        _row(
            "phase_4_10",
            "freeze",
            audit["audit_status"],
            "freeze_statement",
            audit["freeze_statement"],
            "docs/prototype4_extensions/phase_4_10_extension_audit_and_freeze.md",
        )
    )
    return rows


def _row(
    phase: str,
    component: str,
    status: str,
    metric: str,
    value: Any,
    evidence_path: str,
) -> dict:
    return {
        "phase": phase,
        "component": component,
        "status": status,
        "metric": metric,
        "value": value,
        "evidence_path": evidence_path,
    }


def _status(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


if __name__ == "__main__":
    main()

