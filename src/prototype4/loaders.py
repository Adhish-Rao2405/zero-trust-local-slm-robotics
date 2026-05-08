from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.prototype4.execution_evaluator import Prototype3Result


_FIELD_ALIASES = {
    "command_id": ("command_id", "id"),
    "command_text": ("command_text", "command"),
    "ambiguity_level": ("ambiguity_level", "difficulty"),
    "model_name": ("model_name", "model"),
    "schema_valid": ("schema_valid",),
    "semantic_valid": ("semantic_valid",),
    "semantic_score": ("semantic_score",),
    "uncertainty_pass": ("uncertainty_pass",),
    "uncertainty_flag": ("uncertainty_flag",),
    "safety_valid": ("safety_valid",),
    "latency_ms": ("latency_ms", "planning_latency_ms"),
}


def load_prototype3_results_json(path: str | Path) -> list[Prototype3Result]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    rows = _load_json_rows(text, source)
    return [_row_to_result(row, index) for index, row in enumerate(rows)]


def load_prototype3_results_csv(path: str | Path) -> list[Prototype3Result]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [_row_to_result(_coerce_csv_row(row), index) for index, row in enumerate(rows)]


def _load_json_rows(text: str, source: Path) -> list[dict[str, Any]]:
    stripped = text.strip()
    if not stripped:
        return []

    if source.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in stripped.splitlines() if line.strip()]
        return _validate_rows(rows)

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in stripped.splitlines() if line.strip()]
        return _validate_rows(rows)

    if isinstance(payload, list):
        return _validate_rows(payload)
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return _validate_rows(payload["results"])
    raise ValueError("Prototype 3 JSON must be a list, JSONL, or an object with a 'results' list")


def _validate_rows(rows: list[Any]) -> list[dict[str, Any]]:
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Prototype 3 row {index} must be an object")
    return rows


def _row_to_result(row: dict[str, Any], index: int) -> Prototype3Result:
    missing = _missing_required_fields(row)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Prototype 3 row {index} is missing required field(s): {joined}")

    return Prototype3Result(
        command_id=str(_value(row, "command_id")),
        command_text=str(_value(row, "command_text")),
        ambiguity_level=str(_value(row, "ambiguity_level")),
        model_name=str(_value(row, "model_name")),
        plan_actions=_plan_actions(row),
        schema_valid=_bool(_value(row, "schema_valid")),
        semantic_valid=_semantic_valid(row),
        uncertainty_pass=_uncertainty_pass(row),
        safety_valid=_bool(_value(row, "safety_valid")),
        latency_ms=_optional_int(_value(row, "latency_ms", default=None)),
    )


def _missing_required_fields(row: dict[str, Any]) -> list[str]:
    required = [
        "command_id",
        "command_text",
        "ambiguity_level",
        "model_name",
        "schema_valid",
        "safety_valid",
    ]
    missing = [field for field in required if _value(row, field, default=None) is None]
    if _value(row, "semantic_valid", default=None) is None and _value(row, "semantic_score", default=None) is None:
        missing.append("semantic_valid or semantic_score")
    if _value(row, "uncertainty_pass", default=None) is None and _value(row, "uncertainty_flag", default=None) is None:
        missing.append("uncertainty_pass or uncertainty_flag")
    return missing


def _value(row: dict[str, Any], field: str, default: Any = None) -> Any:
    for alias in _FIELD_ALIASES[field]:
        value = row.get(alias)
        if value not in (None, ""):
            return value
    return default


def _plan_actions(row: dict[str, Any]) -> list[dict]:
    for field in ("plan_actions", "planned_actions", "actions"):
        actions = row.get(field)
        if isinstance(actions, list):
            return [action for action in actions if isinstance(action, dict)]
        if isinstance(actions, str) and actions.strip():
            parsed = _parse_jsonish_actions(actions)
            if parsed:
                return parsed

    raw_response = row.get("raw_response")
    if isinstance(raw_response, str) and raw_response.strip():
        return _parse_jsonish_actions(raw_response)
    return []


def _parse_jsonish_actions(raw: str) -> list[dict]:
    candidate = raw.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        actions = parsed.get("actions")
        return [action for action in actions if isinstance(action, dict)] if isinstance(actions, list) else []
    if isinstance(parsed, list):
        return [action for action in parsed if isinstance(action, dict)]
    return []


def _semantic_valid(row: dict[str, Any]) -> bool:
    explicit = _value(row, "semantic_valid", default=None)
    if explicit is not None:
        return _bool(explicit)
    return float(_value(row, "semantic_score")) == 1.0


def _uncertainty_pass(row: dict[str, Any]) -> bool:
    explicit = _value(row, "uncertainty_pass", default=None)
    if explicit is not None:
        return _bool(explicit)
    return not _bool(_value(row, "uncertainty_flag"))


def _coerce_csv_row(row: dict[str, str | None]) -> dict[str, Any]:
    coerced: dict[str, Any] = {}
    for key, value in row.items():
        if value is None:
            coerced[key] = None
            continue
        stripped = value.strip()
        if stripped.lower() in {"true", "false"}:
            coerced[key] = stripped.lower() == "true"
        else:
            coerced[key] = stripped
    return coerced


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    return bool(value)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))
