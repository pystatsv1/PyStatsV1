"""Backward-compatible shim for Track D matplotlib helpers.

Historically, Track D chapter scripts imported :mod:`scripts._mpl_compat`.
The implementation now lives in :mod:`pystatsv1.trackd.mpl_compat`.
"""

from __future__ import annotations

from pystatsv1.trackd.mpl_compat import *  # noqa: F401,F403
