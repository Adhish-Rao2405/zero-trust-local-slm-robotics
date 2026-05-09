from __future__ import annotations

from src.extensions.phase_4_7.ambiguity_features import extract_ambiguity_features


def test_move_it_there_detects_pronoun_and_ambiguous_location():
    features = extract_ambiguity_features("Move it there")

    assert features.pronoun_without_referent is True
    assert features.ambiguous_location is True
    assert "pronoun_without_referent" in features.reasons
    assert "ambiguous_location" in features.reasons


def test_clear_pick_and_place_has_low_ambiguity_features():
    features = extract_ambiguity_features("Pick the red cube and place it in bin A")

    assert features.reasons == []
    assert features.pronoun_without_referent is False
    assert features.vague_object_reference is False
    assert features.missing_target_location is False


def test_sort_everything_properly_detects_weak_underspecified_task():
    features = extract_ambiguity_features("Sort everything properly")

    assert features.weak_action_verb is True
    assert features.underspecified_task is True
    assert features.vague_object_reference is True
    assert "weak_action_verb" in features.reasons
    assert "underspecified_task" in features.reasons


def test_move_without_destination_detects_missing_target_location():
    features = extract_ambiguity_features("Move the blue cylinder")

    assert features.missing_target_location is True
