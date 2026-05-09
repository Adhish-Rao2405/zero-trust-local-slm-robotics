from __future__ import annotations

from src.extensions.phase_4_7.ambiguity_features import extract_ambiguity_features
from src.extensions.phase_4_7.ambiguity_policy import (
    CLARIFY,
    EXECUTE,
    REJECT,
    decide_from_score,
    score_features,
)


def test_low_score_returns_execute():
    assert decide_from_score(0.30) == EXECUTE


def test_medium_score_returns_clarify():
    assert decide_from_score(0.31) == CLARIFY
    assert decide_from_score(0.65) == CLARIFY


def test_high_score_returns_reject():
    assert decide_from_score(0.66) == REJECT


def test_score_never_exceeds_one():
    features = extract_ambiguity_features("Move it somewhere with the thing and sort everything properly near the other one")

    assert score_features(features) == 1.0


def test_scoring_is_deterministic():
    command = "Move the red one near the other one"

    assert score_features(extract_ambiguity_features(command)) == score_features(extract_ambiguity_features(command))
