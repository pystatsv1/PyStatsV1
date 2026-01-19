"""Backwards-compatible shim for Track D schema helpers.

The shipped Track D workbook template imports ``scripts._business_schema``.
To keep all existing chapter runners working without edits, this file remains
as the import surface, but the implementation now lives in
``pystatsv1.trackd.schema``.
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
