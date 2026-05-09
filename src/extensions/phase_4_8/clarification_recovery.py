from __future__ import annotations

from src.extensions.phase_4_7.ambiguity_gate import evaluate_ambiguity
from src.extensions.phase_4_7.ambiguity_policy import CLARIFY, EXECUTE, REJECT


RECOVERABLE_ORIGINAL_DECISIONS = {CLARIFY, REJECT}


def evaluate_clarification_recovery(
    original_command: str,
    clarified_command: str,
) -> dict:
    original = evaluate_ambiguity(original_command)
    clarified = evaluate_ambiguity(clarified_command)
    original_score = float(original["ambiguity_score"])
    clarified_score = float(clarified["ambiguity_score"])
    score_delta = round(original_score - clarified_score, 4)
    recovered = (
        original["decision"] in RECOVERABLE_ORIGINAL_DECISIONS
        and clarified["decision"] == EXECUTE
        and clarified_score < original_score
    )

    return {
        "original_command": original_command,
        "original_decision": original["decision"],
        "original_ambiguity_score": original_score,
        "clarified_command": clarified_command,
        "clarified_decision": clarified["decision"],
        "clarified_ambiguity_score": clarified_score,
        "score_delta": score_delta,
        "recovered": recovered,
    }
