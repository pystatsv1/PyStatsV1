"""Backwards-compatible shim for Track D reconciliation helpers.

The repo uses ``scripts/_business_recon.py`` in Business Track chapters.

The installed package exposes the canonical implementation at
``pystatsv1.trackd.recon``. This shim keeps existing imports working for students
running scripts directly from the repo.
"""

from __future__ import annotations

from pystatsv1.trackd.recon import (
    BankReconOutputs,
    ar_rollforward_vs_tb,
    bank_reconcile,
    build_ar_rollforward,
    build_cash_txn_from_gl,
    build_cash_txns_from_gl,
    reconcile_bank_statement,
    write_json,
)

__all__ = [
    "write_json",
    "build_cash_txns_from_gl",
    "build_cash_txn_from_gl",
    "BankReconOutputs",
    "bank_reconcile",
    "reconcile_bank_statement",
    "ar_rollforward_vs_tb",
    "build_ar_rollforward",
]
