from __future__ import annotations


CLARIFICATION_CASES = [
    {
        "original_command": "Move it there.",
        "clarified_command": "Move the red cube to bin A.",
        "expected_original_decision": "REJECT",
        "expected_clarified_decision": "EXECUTE",
    },
    {
        "original_command": "Pick up the thing.",
        "clarified_command": "Pick up the blue cylinder.",
        "expected_original_decision": "CLARIFY",
        "expected_clarified_decision": "EXECUTE",
    },
    {
        "original_command": "Sort everything properly.",
        "clarified_command": "Place the red cube in bin A and the blue cylinder in bin B.",
        "expected_original_decision": "CLARIFY",
        "expected_clarified_decision": "EXECUTE",
    },
    {
        "original_command": "Move the red one near the other one.",
        "clarified_command": "Move the red cube to the left tray.",
        "expected_original_decision": "CLARIFY",
        "expected_clarified_decision": "EXECUTE",
    },
    {
        "original_command": "Handle the object.",
        "clarified_command": "Pick the green cube and place it in bin C.",
        "expected_original_decision": "CLARIFY",
        "expected_clarified_decision": "EXECUTE",
    },
]
