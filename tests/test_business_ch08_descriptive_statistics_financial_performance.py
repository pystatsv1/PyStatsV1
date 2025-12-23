# SPDX-License-Identifier: MIT
# test_business_ch08_descriptive_statistics_financial_performance.py

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch08_descriptive_statistics_financial_performance import analyze_ch08
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_analyze_ch08_writes_expected_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    # Simulator returns dataframes; we must write them to disk for Ch08 to read.
    sim = simulate_nso_v1(start_month="2025-01", n_months=8, random_state=123)
    write_nso_v1(sim, datadir)

    # Run chapter and write artifacts
    analyze_ch08(datadir=datadir, outdir=outdir, seed=123)

    # Core outputs exist
    kpi_path = outdir / "gl_kpi_monthly.csv"
    ar_m_path = outdir / "ar_monthly_metrics.csv"
    slices_path = outdir / "ar_payment_slices.csv"
    stats_path = outdir / "ar_days_stats.csv"
    summary_path = outdir / "ch08_summary.json"

    assert kpi_path.exists()
    assert ar_m_path.exists()
    assert slices_path.exists()
    assert stats_path.exists()
    assert summary_path.exists()

    # KPI table
    kpi = pd.read_csv(kpi_path)
    assert {
        "month",
        "revenue",
        "cogs",
        "gross_profit",
        "gross_margin_pct",
        "net_income",
        "net_margin_pct",
        "gross_margin_pct_roll_mean_w3",
        "gross_margin_pct_roll_std_w3",
    }.issubset(set(kpi.columns))
    assert kpi["month"].is_monotonic_increasing

    # A/R monthly metrics
    ar_m = pd.read_csv(ar_m_path)
    assert {
        "month",
        "credit_sales",
        "collections",
        "ar_begin",
        "ar_end",
        "avg_ar",
        "ar_turnover",
        "dso",
    }.issubset(set(ar_m.columns))
    assert (ar_m["dso"].fillna(0) >= 0).all()

    # Payment slices
    slices = pd.read_csv(slices_path)
    assert {"customer", "invoice_id", "payment_date", "amount_applied", "days_outstanding"}.issubset(
        set(slices.columns)
    )
    if not slices.empty:
        assert (slices["amount_applied"] > 0).all()
        assert (slices["days_outstanding"] >= 0).all()

    # Days stats
    stats = pd.read_csv(stats_path)
    assert {"customer", "mean_days", "median_days", "p90_days", "total_paid"}.issubset(set(stats.columns))
    assert (stats["total_paid"].fillna(0) >= 0).all()
