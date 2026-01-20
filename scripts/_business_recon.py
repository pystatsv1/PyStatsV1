"""Backwards-compatible shim for Track D reconciliation helpers.

The repo uses ``scripts/_business_recon.py`` in Business Track chapters.

The installed package exposes the canonical implementation at
``pystatsv1.trackd.recon``. This shim keeps existing imports working for students
running scripts directly from the repo.
"""

from __future__ import annotations

from pystatsv1.trackd.recon import *  # noqa: F401,F403
