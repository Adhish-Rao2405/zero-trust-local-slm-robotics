from __future__ import annotations

import re
from dataclasses import dataclass


VAGUE_OBJECT_TERMS = {
    "thing",
    "object",
    "item",
    "stuff",
    "something",
    "everything",
}
PRONOUN_TERMS = {"it", "this", "that", "these", "those"}
AMBIGUOUS_LOCATION_PHRASES = {
    "there",
    "over there",
    "here",
    "somewhere",
    "near it",
    "next to it",
    "near the other one",
}
WEAK_ACTION_VERBS = {"sort", "fix", "arrange", "handle", "do", "manage"}
OBJECT_ACTION_VERBS = {"pick", "grab", "take", "move", "place", "put", "transfer"}
DESTINATION_ACTION_VERBS = {"move", "place", "put", "transfer"}
DESTINATION_MARKERS = {
    "to",
    "into",
    "onto",
    "in",
    "on",
    "near",
    "next",
    "left",
    "right",
    "bin",
    "tray",
    "zone",
    "area",
}
NON_OBJECT_WORDS = {
    "pick",
    "up",
    "grab",
    "take",
    "move",
    "place",
    "put",
    "transfer",
    "the",
    "a",
    "an",
    "and",
    "to",
    "into",
    "onto",
    "in",
    "on",
    "near",
    "next",
    "left",
    "right",
    "open",
    "close",
    "reset",
}


@dataclass(frozen=True)
class AmbiguityFeatures:
    command: str
    pronoun_without_referent: bool
    vague_object_reference: bool
    missing_target_location: bool
    ambiguous_location: bool
    weak_action_verb: bool
    multiple_possible_objects: bool
    underspecified_task: bool
    missing_object: bool

    @property
    def reasons(self) -> list[str]:
        return [
            name
            for name in (
                "pronoun_without_referent",
                "vague_object_reference",
                "missing_target_location",
                "ambiguous_location",
                "weak_action_verb",
                "multiple_possible_objects",
                "underspecified_task",
                "missing_object",
            )
            if getattr(self, name)
        ]

    def as_dict(self) -> dict[str, bool | str | list[str]]:
        return {
            "command": self.command,
            "pronoun_without_referent": self.pronoun_without_referent,
            "vague_object_reference": self.vague_object_reference,
            "missing_target_location": self.missing_target_location,
            "ambiguous_location": self.ambiguous_location,
            "weak_action_verb": self.weak_action_verb,
            "multiple_possible_objects": self.multiple_possible_objects,
            "underspecified_task": self.underspecified_task,
            "missing_object": self.missing_object,
            "reasons": self.reasons,
        }


def extract_ambiguity_features(command: str) -> AmbiguityFeatures:
    normalized = _normalize(command)
    tokens = normalized.split()
    token_set = set(tokens)

    pronoun_without_referent = _detect_pronoun_without_referent(tokens)
    vague_object_reference = bool(token_set & VAGUE_OBJECT_TERMS)
    ambiguous_location = any(_phrase_present(normalized, phrase) for phrase in AMBIGUOUS_LOCATION_PHRASES)
    weak_action_verb = bool(token_set & WEAK_ACTION_VERBS)
    multiple_possible_objects = any(
        _phrase_present(normalized, phrase)
        for phrase in ("correct one", "red one", "blue one", "other one", "the one")
    )
    underspecified_task = (
        weak_action_verb
        or "properly" in token_set
        or _phrase_present(normalized, "sort this out")
        or _phrase_present(normalized, "get this ready")
    )
    missing_target_location = _has_any(tokens, DESTINATION_ACTION_VERBS) and not _has_any(tokens, DESTINATION_MARKERS)
    missing_object = _detect_missing_object(tokens)

    return AmbiguityFeatures(
        command=command,
        pronoun_without_referent=pronoun_without_referent,
        vague_object_reference=vague_object_reference,
        missing_target_location=missing_target_location,
        ambiguous_location=ambiguous_location,
        weak_action_verb=weak_action_verb,
        multiple_possible_objects=multiple_possible_objects,
        underspecified_task=underspecified_task,
        missing_object=missing_object,
    )


def _detect_missing_object(tokens: list[str]) -> bool:
    if not _has_any(tokens, OBJECT_ACTION_VERBS):
        return False
    object_candidates = [
        token
        for token in tokens
        if token not in NON_OBJECT_WORDS
        and token not in DESTINATION_MARKERS
        and token not in VAGUE_OBJECT_TERMS
        and token not in PRONOUN_TERMS
        and not token.isdigit()
    ]
    return len(object_candidates) == 0


def _detect_pronoun_without_referent(tokens: list[str]) -> bool:
    for idx, token in enumerate(tokens):
        if token not in PRONOUN_TERMS:
            continue
        prior_candidates = [
            prior
            for prior in tokens[:idx]
            if prior not in NON_OBJECT_WORDS
            and prior not in DESTINATION_MARKERS
            and prior not in VAGUE_OBJECT_TERMS
            and prior not in PRONOUN_TERMS
        ]
        if not prior_candidates:
            return True
    return False


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _has_any(tokens: list[str], candidates: set[str]) -> bool:
    return any(token in candidates for token in tokens)


def _phrase_present(text: str, phrase: str) -> bool:
    return f" {phrase} " in f" {text} "
