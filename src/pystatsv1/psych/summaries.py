"""Descriptive-summary helpers for psychology-style examples."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any
import math

import pandas as pd


def _as_dataframe(data: pd.DataFrame | Iterable[dict[str, Any]]) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(list(data))


def _normalize_value_cols(value_cols: str | Sequence[str]) -> list[str]:
    if isinstance(value_cols, str):
        return [value_cols]
    return list(value_cols)


def _rounded(value: Any, decimals: int) -> float | int | str | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value
    if math.isnan(numeric):
        return None
    return round(numeric, decimals)


def describe_by_group(
    data: pd.DataFrame | Iterable[dict[str, Any]],
    group_col: str,
    value_cols: str | Sequence[str],
    *,
    decimals: int = 6,
) -> list[dict[str, Any]]:
    """Return simple group-level descriptive statistics.

    Parameters
    ----------
    data:
        A pandas DataFrame or iterable of row dictionaries.
    group_col:
        Categorical grouping column, such as an experimental condition.
    value_cols:
        One numeric column name or a sequence of numeric column names.
    decimals:
        Rounding precision for JSON-stable receipts.

    Returns
    -------
    list of dict
        One record per group/value-column pair with n, mean, sd, min, and max.
    """

    df = _as_dataframe(data)
    value_names = _normalize_value_cols(value_cols)
    missing = [col for col in [group_col, *value_names] if col not in df.columns]
    if missing:
        raise KeyError(f"Missing required column(s): {', '.join(missing)}")

    records: list[dict[str, Any]] = []
    grouped = df.groupby(group_col, dropna=False, sort=True)
    for group_value, group_df in grouped:
        for value_col in value_names:
            values = pd.to_numeric(group_df[value_col], errors="coerce").dropna()
            n = int(values.shape[0])
            sd_value = values.std(ddof=1) if n > 1 else None
            records.append(
                {
                    group_col: group_value.item() if hasattr(group_value, "item") else group_value,
                    "variable": value_col,
                    "n": n,
                    "mean": _rounded(values.mean() if n else None, decimals),
                    "sd": _rounded(sd_value, decimals),
                    "min": _rounded(values.min() if n else None, decimals),
                    "max": _rounded(values.max() if n else None, decimals),
                }
            )
    return records
