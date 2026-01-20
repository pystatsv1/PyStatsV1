"""Track D (Business): accounting-oriented statistics, forecasting, and data analysis.

This subpackage will gradually grow from thin chapter-runner scripts into a reusable
mini-library: data loading, schema checks, feature engineering helpers, forecasting
baselines, and report builders.
"""

from __future__ import annotations

from ._errors import TrackDDataError, TrackDSchemaError  # noqa: F401
from ._types import DataFrame, DataFrames, PathLike  # noqa: F401
from .csvio import read_csv_required  # noqa: F401
from .schema import (  # noqa: F401
    DATASET_NSO_V1,
    NSO_V1,
    TableSchema,
    assert_schema,
    validate_schema,
)

from .etl import (
    GLPrepOutputs,
    analyze_gl_preparation,
    build_data_dictionary,
    build_gl_tidy_dataset,
    prepare_gl_monthly_summary,
    prepare_gl_tidy,
)

from .recon import (
    BankReconOutputs,
    ar_rollforward_vs_tb,
    bank_reconcile,
    build_ar_rollforward,
    build_cash_txn_from_gl,
    build_cash_txns_from_gl,
    reconcile_bank_statement,
    write_json,
)

__all__ = [
    "DataFrame",
    "DataFrames",
    "PathLike",
    "DATASET_NSO_V1",
    "NSO_V1",
    "TableSchema",
    "assert_schema",
    "TrackDDataError",
    "TrackDSchemaError",
    "read_csv_required",
    "validate_schema",
    "GLPrepOutputs",
    "prepare_gl_tidy",
    "build_gl_tidy_dataset",
    "prepare_gl_monthly_summary",
    "build_data_dictionary",
    "analyze_gl_preparation",
    "BankReconOutputs",
    "write_json",
    "build_cash_txns_from_gl",
    "build_cash_txn_from_gl",
    "bank_reconcile",
    "reconcile_bank_statement",
    "ar_rollforward_vs_tb",
    "build_ar_rollforward",
]
