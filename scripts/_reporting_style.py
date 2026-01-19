"""Backward-compatible shim for Track D reporting-style helpers.

Historically, Track D chapter scripts imported :mod:`scripts._reporting_style`.
The implementation now lives in :mod:`pystatsv1.trackd.reporting_style`.

Keeping this shim prevents template drift and avoids breaking older chapter
scripts that import from ``scripts/``.
"""

from __future__ import annotations

from pystatsv1.trackd.reporting_style import *  # noqa: F401,F403
