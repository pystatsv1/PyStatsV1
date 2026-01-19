"""Backwards-compatible shim for Track D schema helpers.

The Track D workbook template (and legacy scripts) historically imported
``scripts._business_schema``.

As of PR-1.2b, the canonical implementation lives in
``pystatsv1.trackd.schema`` so it can be reused by chapter runners and future
"bring-your-own data" pipelines.
"""

from __future__ import annotations

from pystatsv1.trackd.schema import (
    DATASET_NSO_V1,
    NSO_V1,
    TableSchema,
    assert_schema,
    validate_schema,
    validate_table_map,
)

__all__ = [
    "DATASET_NSO_V1",
    "NSO_V1",
    "TableSchema",
    "validate_schema",
    "validate_table_map",
    "assert_schema",
]
