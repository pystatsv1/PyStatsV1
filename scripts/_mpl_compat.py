"""Backward-compatible shim for Track D matplotlib helpers.

Historically, some Track D and workbook scripts imported
:mod:`scripts._mpl_compat`.

The canonical implementation now lives in :mod:`pystatsv1.trackd.mpl_compat`.
This shim keeps existing imports working for students running scripts directly
from the repo.
"""

from __future__ import annotations

from pystatsv1.trackd.mpl_compat import ax_boxplot

__all__ = [
    "ax_boxplot",
]
