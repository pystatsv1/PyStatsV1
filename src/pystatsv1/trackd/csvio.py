"""Track D CSV I/O helpers.

This module centralizes the most common, student-facing CSV loading patterns
used across Track D.

Goals
- Friendly, consistent error messages.
- Small surface area (easy to reuse in chapter runners and BYOD adapters).
- Avoid leaking low-level pandas exceptions to beginners.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from ._errors import TrackDDataError, TrackDSchemaError
from ._types import DataFrame, PathLike


def read_csv_required(
    path: PathLike,
    *,
    required_cols: Sequence[str] | None = None,
    parse_dates: Sequence[str] | None = None,
    dtypes: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> DataFrame:
    """Read a CSV file and enforce required columns.

    Parameters
    ----------
    path:
        Path to the CSV file.
    required_cols:
        Column names that must be present in the CSV header row.
    parse_dates:
        Column names to parse as dates (passed to pandas).
    dtypes:
        Optional dtype mapping (passed to pandas).

    Raises
    ------
    TrackDDataError:
        If the file is missing or can't be read.
    TrackDSchemaError:
        If required columns are missing.

    Returns
    -------
    pandas.DataFrame
    """
    p = Path(path)
    if not p.exists():
        raise TrackDDataError(
            f"Missing CSV file: {p}.\n"
            "Hint: check your export location and filename, then try again."
        )

    read_kwargs: dict[str, Any] = dict(kwargs)
    if parse_dates is not None:
        read_kwargs["parse_dates"] = list(parse_dates)
    if dtypes is not None:
        read_kwargs["dtype"] = dtypes

    try:
        df = pd.read_csv(p, **read_kwargs)
    except Exception as e:  # pragma: no cover
        raise TrackDDataError(
            f"Could not read CSV: {p}.\n"
            f"Reason: {type(e).__name__}: {e}"
        ) from e

    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            found = ", ".join(map(str, df.columns)) if len(df.columns) else "(no columns)"
            req = ", ".join(missing)
            raise TrackDSchemaError(
                f"Missing required columns in {p.name}: {req}.\n"
                f"Found columns: {found}.\n"
                "Hint: ensure the first row is the header, and re-export as CSV if needed."
            )

    return df
