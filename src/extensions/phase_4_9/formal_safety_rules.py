from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormalSafetyRule:
    rule_id: str
    name: str
    description: str
    severity: str
    category: str


FORMAL_SAFETY_RULES: tuple[FormalSafetyRule, ...] = (
    FormalSafetyRule(
        rule_id="FS-001",
        name="Action present",
        description="Action plan must include an action field.",
        severity="critical",
        category="schema",
    ),
    FormalSafetyRule(
        rule_id="FS-002",
        name="Supported action",
        description="Action must be a member of the formal supported action set.",
        severity="critical",
        category="schema",
    ),
    FormalSafetyRule(
        rule_id="FS-003",
        name="Required action parameters",
        description="Action parameters must satisfy the required schema for the selected action.",
        severity="high",
        category="schema",
    ),
    FormalSafetyRule(
        rule_id="FS-004",
        name="Workspace bounds",
        description="target_xyz values must remain inside the permitted robot workspace bounds.",
        severity="critical",
        category="physical_bounds",
    ),
    FormalSafetyRule(
        rule_id="FS-005",
        name="Allowed zone target",
        description="Zone targets must be members of the allowed zone set.",
        severity="critical",
        category="semantic_targeting",
    ),
    FormalSafetyRule(
        rule_id="FS-006",
        name="Gripper width bounds",
        description="Gripper width must be within permitted bounds when supplied.",
        severity="high",
        category="actuator_bounds",
    ),
    FormalSafetyRule(
        rule_id="FS-007",
        name="Force bounds",
        description="Force must be within permitted bounds when supplied.",
        severity="critical",
        category="actuator_bounds",
    ),
    FormalSafetyRule(
        rule_id="FS-008",
        name="Known object reference",
        description="Referenced objects must be members of the known object set.",
        severity="high",
        category="semantic_targeting",
    ),
    FormalSafetyRule(
        rule_id="FS-009",
        name="No unknown fields",
        description="Action plans must not contain unknown or extra fields for the selected action.",
        severity="high",
        category="schema",
    ),
    FormalSafetyRule(
        rule_id="FS-010",
        name="Ambiguity gate execution authority",
        description="Commands classified as CLARIFY or REJECT must not be authorised for execution.",
        severity="critical",
        category="execution_authorisation",
    ),
)


RULES_BY_ID: dict[str, FormalSafetyRule] = {
    rule.rule_id: rule for rule in FORMAL_SAFETY_RULES
}


def get_rule(rule_id: str) -> FormalSafetyRule:
    return RULES_BY_ID[rule_id]


def get_rule_ids() -> list[str]:
    return [rule.rule_id for rule in FORMAL_SAFETY_RULES]

