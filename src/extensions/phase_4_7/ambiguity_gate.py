from __future__ import annotations

from src.extensions.phase_4_7.ambiguity_features import extract_ambiguity_features
from src.extensions.phase_4_7.ambiguity_policy import apply_policy


def evaluate_ambiguity(command: str) -> dict:
    features = extract_ambiguity_features(command)
    policy_result = apply_policy(features)
    return {
        "command": command,
        "ambiguity_score": policy_result.ambiguity_score,
        "decision": policy_result.decision,
        "reasons": policy_result.reasons,
    }
