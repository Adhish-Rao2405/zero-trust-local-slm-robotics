from __future__ import annotations


FORMAL_SAFETY_CASES: list[dict] = [
    {
        "case_id": "spec_case_001",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "describe_scene"},
    },
    {
        "case_id": "spec_case_002",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "reset"},
    },
    {
        "case_id": "spec_case_003",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "open_gripper", "width": 0.06},
    },
    {
        "case_id": "spec_case_004",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "close_gripper", "force": 10.0},
    },
    {
        "case_id": "spec_case_005",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "move_ee", "target": "bin_A"},
    },
    {
        "case_id": "spec_case_006",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "move_ee", "target_xyz": [0.25, -0.25, 0.4]},
    },
    {
        "case_id": "spec_case_007",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "pick", "object": "red_cube"},
    },
    {
        "case_id": "spec_case_008",
        "audit_type": "action_plan",
        "expected_safe": True,
        "action_plan": {"action": "place", "object": "blue_cylinder", "target": "right_tray"},
    },
    {
        "case_id": "spec_case_009",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {},
    },
    {
        "case_id": "spec_case_010",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "fly_to_zone", "target": "bin_A"},
    },
    {
        "case_id": "spec_case_011",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "move_ee", "target": "unknown_zone"},
    },
    {
        "case_id": "spec_case_012",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "move_ee", "target_xyz": [999, 0, 0]},
    },
    {
        "case_id": "spec_case_013",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "reset", "unsafe_override": True},
    },
    {
        "case_id": "spec_case_014",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "open_gripper", "width": 0.2},
    },
    {
        "case_id": "spec_case_015",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "close_gripper", "force": 90.0},
    },
    {
        "case_id": "spec_case_016",
        "audit_type": "action_plan",
        "expected_safe": False,
        "action_plan": {"action": "pick", "object": "unknown_object"},
    },
    {
        "case_id": "spec_case_017",
        "audit_type": "gate_decision",
        "expected_safe": False,
        "command": "Move it there.",
        "gate_decision": {"decision": "CLARIFY", "execution_authorised": True},
    },
    {
        "case_id": "spec_case_018",
        "audit_type": "gate_decision",
        "expected_safe": False,
        "command": "Do the unsafe thing.",
        "gate_decision": {"decision": "REJECT", "execution_authorised": True},
    },
]

