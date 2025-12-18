"""Tests for Track D Chapter 1 (LedgerLab + accounting integrity checks)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch01_accounting_measurement import analyze_ch01
from scripts.sim_business_ledgerlab import simulate_ledgerlab_month, write_ledgerlab


def test_simulator_transactions_balance() -> None:
    """Every transaction should balance: sum(debits) == sum(credits) by txn_id."""
    outs = simulate_ledgerlab_month(month="2025-01", n_sales=6, random_state=123)
    gl = outs.gl_journal

    by_txn = gl.groupby("txn_id", as_index=False)[["debit", "credit"]].sum()
    diffs = (by_txn["debit"] - by_txn["credit"]).abs()
    assert float(diffs.max()) < 1e-6


def test_ch01_analysis_writes_artifacts(tmp_path: Path) -> None:
    """Analyzer should write summary JSON + plots and pass key integrity checks."""
    datadir = tmp_path / "ledgerlab"
    outdir = tmp_path / "out"

    outs = simulate_ledgerlab_month(month="2025-01", n_sales=8, random_state=42)
    write_ledgerlab(outs, datadir)

    summary = analyze_ch01(datadir, outdir, seed=42)

    assert summary.checks["transactions_balanced"] is True
    assert summary.checks["accounting_equation_balances"] is True

    assert (outdir / "business_ch01_summary.json").exists()
    assert (outdir / "business_ch01_cash_balance.png").exists()
    assert (outdir / "business_ch01_balance_sheet_bar.png").exists()


def test_simulation_deterministic_by_seed(tmp_path: Path) -> None:
    """Same seed should produce identical sales total."""
    outs1 = simulate_ledgerlab_month(month="2025-01", n_sales=10, random_state=7)
    outs2 = simulate_ledgerlab_month(month="2025-01", n_sales=10, random_state=7)

    s1 = float(outs1.gl_journal.loc[outs1.gl_journal["account_id"] == "4000", "credit"].sum())
    s2 = float(outs2.gl_journal.loc[outs2.gl_journal["account_id"] == "4000", "credit"].sum())
    assert s1 == s2

    # Smoke: outputs are valid CSV tables
    write_ledgerlab(outs1, tmp_path / "a")
    df = pd.read_csv(tmp_path / "a" / "chart_of_accounts.csv")
    assert {"account_id", "account_name", "account_type", "normal_side"}.issubset(df.columns)
