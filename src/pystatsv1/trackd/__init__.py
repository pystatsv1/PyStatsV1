"""Track D (Business): accounting-oriented statistics, forecasting, and data analysis.

This subpackage will gradually grow from thin chapter-runner scripts into a reusable
mini-library: data loading, schema checks, feature engineering helpers, forecasting
baselines, and report builders.
"""

from __future__ import annotations

from ._errors import TrackDDataError, TrackDSchemaError  # noqa: F401
from ._types import DataFrame, DataFrames, PathLike  # noqa: F401

__all__ = [
    "DataFrame",
    "DataFrames",
    "PathLike",
    "TrackDDataError",
    "TrackDSchemaError",
]
