from __future__ import annotations

from src.extensions.phase_4_9.formal_safety_rules import (
    FORMAL_SAFETY_RULES,
    RULES_BY_ID,
    get_rule_ids,
)


def test_all_formal_safety_rule_ids_exist():
    assert get_rule_ids() == [f"FS-{index:03d}" for index in range(1, 11)]
    assert set(RULES_BY_ID) == set(get_rule_ids())


def test_rules_have_required_metadata():
    for rule in FORMAL_SAFETY_RULES:
        assert rule.rule_id
        assert rule.name
        assert rule.description
        assert rule.severity in {"critical", "high"}
        assert rule.category

