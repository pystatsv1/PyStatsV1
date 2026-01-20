"""Backward-compatible shim for Track D matplotlib helpers.

The Track D workbook template historically shipped an implementation of this
module in the workbook itself. The canonical implementation now lives in the
installed PyStatsV1 package at :mod:`pystatsv1.trackd.mpl_compat`.

Keeping this shim avoids breaking imports inside the workbook's chapter scripts.
"""

from __future__ import annotations

from pystatsv1.trackd.mpl_compat import ax_boxplot

__all__ = [
    "ax_boxplot",
]
