"""Backwards-compatible shim for Track D ETL helpers.

The repo uses ``scripts/_business_etl.py`` in Business Track chapters.

The installed package exposes the canonical implementation at
``pystatsv1.trackd.etl``. This shim keeps existing imports working for students
running scripts directly from the repo.
"""

from __future__ import annotations

from pystatsv1.trackd.etl import *  # noqa: F401,F403
