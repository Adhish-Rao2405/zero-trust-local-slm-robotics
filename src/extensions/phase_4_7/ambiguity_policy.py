from __future__ import annotations

from dataclasses import dataclass

from src.extensions.phase_4_7.ambiguity_features import AmbiguityFeatures


EXECUTE = "EXECUTE"
CLARIFY = "CLARIFY"
REJECT = "REJECT"

FEATURE_WEIGHTS = {
    "pronoun_without_referent": 0.25,
    "vague_object_reference": 0.25,
    "missing_target_location": 0.25,
    "ambiguous_location": 0.20,
    "weak_action_verb": 0.15,
    "multiple_possible_objects": 0.20,
    "underspecified_task": 0.20,
    "missing_object": 0.20,
}


@dataclass(frozen=True)
class AmbiguityPolicyResult:
    ambiguity_score: float
    decision: str
    reasons: list[str]


def score_features(features: AmbiguityFeatures) -> float:
    score = sum(
        weight
        for name, weight in FEATURE_WEIGHTS.items()
        if getattr(features, name)
    )
    return min(1.0, round(score, 4))


def decide_from_score(score: float) -> str:
    bounded = min(1.0, max(0.0, score))
    if bounded <= 0.30:
        return EXECUTE
    if bounded <= 0.65:
        return CLARIFY
    return REJECT


def apply_policy(features: AmbiguityFeatures) -> AmbiguityPolicyResult:
    score = score_features(features)
    return AmbiguityPolicyResult(
        ambiguity_score=score,
        decision=decide_from_score(score),
        reasons=features.reasons,
    )
