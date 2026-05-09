from __future__ import annotations

from src.extensions.phase_4_7.ambiguity_policy import CLARIFY, EXECUTE, REJECT
from src.extensions.phase_4_8.clarification_recovery import evaluate_clarification_recovery


def test_output_contains_required_fields():
    result = evaluate_clarification_recovery("Move it there.", "Move the red cube to bin A.")

    assert set(result) == {
        "original_command",
        "original_decision",
        "original_ambiguity_score",
        "clarified_command",
        "clarified_decision",
        "clarified_ambiguity_score",
        "score_delta",
        "recovered",
    }


def test_ambiguous_original_has_higher_score_than_clarified_command():
    result = evaluate_clarification_recovery("Move it there.", "Move the red cube to bin A.")

    assert result["original_ambiguity_score"] > result["clarified_ambiguity_score"]
    assert result["score_delta"] > 0


def test_clarified_command_can_recover_to_execute():
    result = evaluate_clarification_recovery("Pick up the thing.", "Pick up the blue cylinder.")

    assert result["original_decision"] == CLARIFY
    assert result["clarified_decision"] == EXECUTE
    assert result["recovered"] is True


def test_recovered_true_for_reject_to_execute_when_score_decreases():
    result = evaluate_clarification_recovery("Move it there.", "Move the red cube to bin A.")

    assert result["original_decision"] == REJECT
    assert result["clarified_decision"] == EXECUTE
    assert result["score_delta"] > 0
    assert result["recovered"] is True


def test_recovered_false_when_original_was_already_executable():
    result = evaluate_clarification_recovery(
        "Move the blue cylinder to the left tray.",
        "Move the blue cylinder to the left tray.",
    )

    assert result["original_decision"] == EXECUTE
    assert result["clarified_decision"] == EXECUTE
    assert result["recovered"] is False


def test_recovered_false_when_clarified_command_is_still_ambiguous():
    result = evaluate_clarification_recovery("Move it there.", "Move the thing there.")

    assert result["original_decision"] in {CLARIFY, REJECT}
    assert result["clarified_decision"] != EXECUTE
    assert result["recovered"] is False
