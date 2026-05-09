from __future__ import annotations

from src.extensions.phase_4_9.formal_safety_rules import RULES_BY_ID, get_rule_ids
from src.extensions.phase_4_9.formal_safety_spec import (
    ALLOWED_FIELDS_BY_ACTION,
    ALLOWED_ZONES,
    FORCE_BOUNDS,
    GRIPPER_WIDTH_BOUNDS,
    KNOWN_OBJECTS,
    REQUIRED_FIELDS_BY_ACTION,
    SUPPORTED_ACTIONS,
    TARGET_REQUIRED_ACTIONS,
    WORKSPACE_BOUNDS,
)


def audit_action_plan(action_plan: dict) -> dict:
    violations: list[dict] = []
    rule_ids_checked = get_rule_ids()[:-1]

    action = action_plan.get("action") if isinstance(action_plan, dict) else None
    if not action:
        violations.append(_violation("FS-001", "action field is required"))
        return _audit_result(False, violations, rule_ids_checked)

    if action not in SUPPORTED_ACTIONS:
        violations.append(_violation("FS-002", f"unsupported action: {action}"))
        return _audit_result(False, violations, rule_ids_checked)

    violations.extend(_check_required_fields(action_plan, action))
    violations.extend(_check_unknown_fields(action_plan, action))
    violations.extend(_check_target_xyz(action_plan))
    violations.extend(_check_zone_target(action_plan))
    violations.extend(_check_gripper_width(action_plan))
    violations.extend(_check_force(action_plan))
    violations.extend(_check_object_reference(action_plan))

    return _audit_result(not violations, violations, rule_ids_checked)


def audit_gate_decision(command: str, gate_decision: dict) -> dict:
    violations: list[dict] = []
    rule_ids_checked = ["FS-010"]

    decision = gate_decision.get("decision")
    execution_authorised = bool(gate_decision.get("execution_authorised", False))

    if decision in {"CLARIFY", "REJECT"} and execution_authorised:
        violations.append(
            _violation(
                "FS-010",
                f"{decision} command must not be execution-authorised",
            )
        )

    action_audit = None
    action_plan = gate_decision.get("action_plan")
    if decision == "EXECUTE" and execution_authorised and action_plan is not None:
        action_audit = audit_action_plan(action_plan)
        rule_ids_checked.extend(action_audit["rule_ids_checked"])
        violations.extend(action_audit["violations"])

    result = _audit_result(not violations, violations, rule_ids_checked)
    result["command"] = command
    result["gate_decision"] = gate_decision
    if action_audit is not None:
        result["action_audit"] = action_audit
    return result


def _check_required_fields(action_plan: dict, action: str) -> list[dict]:
    violations = []
    required_fields = REQUIRED_FIELDS_BY_ACTION[action]
    missing = sorted(field for field in required_fields if field not in action_plan)
    if missing:
        violations.append(
            _violation("FS-003", f"missing required field(s): {', '.join(missing)}")
        )

    if action in TARGET_REQUIRED_ACTIONS and not (
        "target" in action_plan or "target_xyz" in action_plan
    ):
        violations.append(_violation("FS-003", f"{action} requires target or target_xyz"))

    if "target_xyz" in action_plan and not _is_xyz_tuple(action_plan["target_xyz"]):
        violations.append(_violation("FS-003", "target_xyz must contain three numeric values"))

    return violations


def _check_unknown_fields(action_plan: dict, action: str) -> list[dict]:
    allowed_fields = ALLOWED_FIELDS_BY_ACTION[action]
    extra_fields = sorted(field for field in action_plan if field not in allowed_fields)
    if not extra_fields:
        return []
    return [_violation("FS-009", f"unknown field(s): {', '.join(extra_fields)}")]


def _check_target_xyz(action_plan: dict) -> list[dict]:
    target_xyz = action_plan.get("target_xyz")
    if not _is_xyz_tuple(target_xyz):
        return []

    axis_values = dict(zip(("x", "y", "z"), target_xyz))
    for axis, value in axis_values.items():
        lower, upper = WORKSPACE_BOUNDS[axis]
        if value < lower or value > upper:
            return [
                _violation(
                    "FS-004",
                    "target_xyz is outside permitted workspace bounds",
                )
            ]
    return []


def _check_zone_target(action_plan: dict) -> list[dict]:
    target = action_plan.get("target")
    if target is None:
        return []
    if target in ALLOWED_ZONES:
        return []
    return [_violation("FS-005", f"target zone is not allowed: {target}")]


def _check_gripper_width(action_plan: dict) -> list[dict]:
    if "width" not in action_plan:
        return []
    width = action_plan["width"]
    lower, upper = GRIPPER_WIDTH_BOUNDS
    if not isinstance(width, (int, float)) or isinstance(width, bool) or width < lower or width > upper:
        return [_violation("FS-006", "gripper width is outside permitted bounds")]
    return []


def _check_force(action_plan: dict) -> list[dict]:
    if "force" not in action_plan:
        return []
    force = action_plan["force"]
    lower, upper = FORCE_BOUNDS
    if not isinstance(force, (int, float)) or isinstance(force, bool) or force < lower or force > upper:
        return [_violation("FS-007", "force is outside permitted bounds")]
    return []


def _check_object_reference(action_plan: dict) -> list[dict]:
    object_ref = action_plan.get("object")
    if object_ref is None:
        return []
    if object_ref in KNOWN_OBJECTS:
        return []
    return [_violation("FS-008", f"referenced object is unknown: {object_ref}")]


def _is_xyz_tuple(value: object) -> bool:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return False
    return all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)


def _violation(rule_id: str, message: str) -> dict:
    rule = RULES_BY_ID[rule_id]
    return {
        "rule_id": rule.rule_id,
        "severity": rule.severity,
        "message": message,
    }


def _audit_result(passed: bool, violations: list[dict], rule_ids_checked: list[str]) -> dict:
    return {
        "passed": passed,
        "violations": violations,
        "rule_ids_checked": list(dict.fromkeys(rule_ids_checked)),
    }

