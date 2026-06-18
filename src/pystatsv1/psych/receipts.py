"""Receipt helpers for proof-first psychology workflows."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any
import json
import math


def write_json_receipt(path: str | Path, payload: Mapping[str, Any]) -> Path:
    """Write a stable, human-readable JSON receipt and return its path."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _as_float_or_none(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def compare_numeric_results(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    tolerance: float = 1e-6,
) -> dict[str, Any]:
    """Compare numeric metrics from two analysis engines.

    The return value is JSON-serializable and explicitly records missing and
    non-numeric values rather than silently treating them as matches.
    """

    keys = sorted(set(left) | set(right))
    comparisons: list[dict[str, Any]] = []
    all_within_tolerance = True
    for key in keys:
        left_present = key in left
        right_present = key in right
        left_value = _as_float_or_none(left.get(key)) if left_present else None
        right_value = _as_float_or_none(right.get(key)) if right_present else None
        if not left_present or not right_present:
            status = "missing"
            within = False
            absolute_difference = None
        elif left_value is None or right_value is None:
            status = "non_numeric"
            within = False
            absolute_difference = None
        else:
            absolute_difference = abs(left_value - right_value)
            within = absolute_difference <= tolerance
            status = "pass" if within else "fail"
        all_within_tolerance = all_within_tolerance and within
        comparisons.append(
            {
                "metric": key,
                "left": left.get(key) if left_present else None,
                "right": right.get(key) if right_present else None,
                "absolute_difference": absolute_difference,
                "within_tolerance": within,
                "status": status,
            }
        )
    return {
        "tolerance": tolerance,
        "all_within_tolerance": all_within_tolerance,
        "comparisons": comparisons,
    }
