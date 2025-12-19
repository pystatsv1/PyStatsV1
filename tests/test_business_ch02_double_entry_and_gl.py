"""Tests for Track D Chapter 2 (GL as database + trial balance consistency)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch02_double_entry_and_gl import analyze_ch02
from scripts.sim_business_ledgerlab import simulate_ledgerlab_month, write_ledgerlab


def test_ch02_creates_tidy_gl_and_tb(tmp_path: Path) -> None:
    outs = simulate_ledgerlab_month(month="2025-01", n_sales=6, random_state=123)
    write_ledgerlab(outs, tmp_path)

    outdir = tmp_path / "out"
    summary = analyze_ch02(tmp_path, outdir, seed=123)

    assert summary.checks["transactions_balanced"] is True
    assert summary.checks["trial_balance_matches_source"] is True

    tidy_path = outdir / "business_ch02_gl_tidy.csv"
    tb_path = outdir / "business_ch02_trial_balance.csv"
    assert tidy_path.exists()
    assert tb_path.exists()

    tidy = pd.read_csv(tidy_path)
    for col in ["dc_amount", "normal_amount", "statement"]:
        assert col in tidy.columns
