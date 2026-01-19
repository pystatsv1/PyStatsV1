"""Backward-compatible shim for Track D reporting style.

The Track D workbook template historically shipped an implementation of this
module in the workbook itself. The canonical implementation now lives in the
installed PyStatsV1 package at :mod:`pystatsv1.trackd.reporting_style`.

Keeping this shim avoids breaking imports inside the workbook's chapter scripts.
"""

from __future__ import annotations

from pystatsv1.trackd.reporting_style import *  # noqa: F401,F403
