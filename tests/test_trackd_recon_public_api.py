from __future__ import annotations

import importlib


def test_trackd_recon_helpers_are_exported_from_trackd() -> None:
    trackd = importlib.import_module("pystatsv1.trackd")
    recon = importlib.import_module("pystatsv1.trackd.recon")

    exported = [
        "BankReconOutputs",
        "write_json",
        "build_cash_txns_from_gl",
        "build_cash_txn_from_gl",
        "bank_reconcile",
        "reconcile_bank_statement",
        "ar_rollforward_vs_tb",
        "build_ar_rollforward",
    ]

    for name in exported:
        assert getattr(trackd, name) is getattr(recon, name)
        assert name in getattr(trackd, "__all__")
