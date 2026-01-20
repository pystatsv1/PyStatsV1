"""Backwards-compatible shim for Track D ETL helpers.

The repo uses ``scripts/_business_etl.py`` in Business Track chapters.

The installed package exposes the canonical implementation at
``pystatsv1.trackd.etl``. This shim keeps existing imports working for students
running scripts directly from the repo.
"""

from __future__ import annotations

from pystatsv1.trackd.etl import (
    GLPrepOutputs,
    analyze_gl_preparation,
    build_data_dictionary,
    build_gl_tidy_dataset,
    prepare_gl_monthly_summary,
    prepare_gl_tidy,
)

__all__ = [
    "GLPrepOutputs",
    "prepare_gl_tidy",
    "build_gl_tidy_dataset",
    "prepare_gl_monthly_summary",
    "build_data_dictionary",
    "analyze_gl_preparation",
]
