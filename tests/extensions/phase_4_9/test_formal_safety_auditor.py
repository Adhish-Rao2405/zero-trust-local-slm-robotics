from __future__ import annotations

from src.extensions.phase_4_9.formal_safety_auditor import (
    audit_action_plan,
    audit_gate_decision,
)
from src.extensions.phase_4_9.formal_safety_cases import FORMAL_SAFETY_CASES


def test_safe_builtin_action_plans_pass():
    safe_action_cases = [
        case for case in FORMAL_SAFETY_CASES
        if case["audit_type"] == "action_plan" and case["expected_safe"]
    ]

    assert safe_action_cases
    for case in safe_action_cases:
        result = audit_action_plan(case["action_plan"])
        assert result["passed"], case["case_id"]
        assert result["violations"] == []


def test_unsafe_builtin_cases_fail():
    unsafe_cases = [case for case in FORMAL_SAFETY_CASES if not case["expected_safe"]]

    assert unsafe_cases
    for case in unsafe_cases:
        if case["audit_type"] == "action_plan":
            result = audit_action_plan(case["action_plan"])
        else:
            result = audit_gate_decision(case["command"], case["gate_decision"])
        assert not result["passed"], case["case_id"]
        assert result["violations"]


def test_missing_action_fails():
    result = audit_action_plan({})

    assert not result["passed"]
    assert _rule_ids(result) == {"FS-001"}


def test_unsupported_action_fails():
    result = audit_action_plan({"action": "teleport", "target": "bin_A"})

    assert not result["passed"]
    assert _rule_ids(result) == {"FS-002"}


def test_out_of_bounds_coordinates_fail():
    result = audit_action_plan({"action": "move_ee", "target_xyz": [1.2, 0.0, 0.2]})

    assert not result["passed"]
    assert "FS-004" in _rule_ids(result)


def test_unknown_zone_fails():
    result = audit_action_plan({"action": "move_ee", "target": "ceiling"})

    assert not result["passed"]
    assert "FS-005" in _rule_ids(result)


def test_unknown_extra_field_fails():
    result = audit_action_plan({"action": "reset", "extra": "unsafe"})

    assert not result["passed"]
    assert "FS-009" in _rule_ids(result)


def test_gripper_width_outside_bounds_fails():
    result = audit_action_plan({"action": "open_gripper", "width": 0.5})

    assert not result["passed"]
    assert "FS-006" in _rule_ids(result)


def test_force_outside_bounds_fails():
    result = audit_action_plan({"action": "close_gripper", "force": 99.0})

    assert not result["passed"]
    assert "FS-007" in _rule_ids(result)


def test_unknown_object_fails():
    result = audit_action_plan({"action": "pick", "object": "mystery_block"})

    assert not result["passed"]
    assert "FS-008" in _rule_ids(result)


def test_clarify_gate_decision_cannot_be_execution_authorised():
    result = audit_gate_decision(
        "Move it there",
        {"decision": "CLARIFY", "execution_authorised": True},
    )

    assert not result["passed"]
    assert _rule_ids(result) == {"FS-010"}


def test_reject_gate_decision_cannot_be_execution_authorised():
    result = audit_gate_decision(
        "Do something unsafe",
        {"decision": "REJECT", "execution_authorised": True},
    )

    assert not result["passed"]
    assert _rule_ids(result) == {"FS-010"}


def test_execute_gate_decision_with_unsafe_action_plan_fails():
    result = audit_gate_decision(
        "Move outside the workspace",
        {
            "decision": "EXECUTE",
            "execution_authorised": True,
            "action_plan": {"action": "move_ee", "target_xyz": [999, 0, 0]},
        },
    )

    assert not result["passed"]
    assert "FS-004" in _rule_ids(result)


def _rule_ids(result: dict) -> set[str]:
    return {violation["rule_id"] for violation in result["violations"]}

