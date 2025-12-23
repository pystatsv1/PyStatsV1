# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

# import pandas as pd

from scripts.business_ch07_preparing_accounting_data_for_analysis import analyze_ch07
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_ch07_writes_tidy_and_monthly(tmp_path: Path) -> None:
    outdir = tmp_path / "nso_v1"
    outputs = simulate_nso_v1(start_month="2025-01", n_months=6, random_state=123)
    write_nso_v1(outputs, outdir)

    result = analyze_ch07(outdir)

    # --- gl_tidy
    tidy = result.gl_tidy
    assert not tidy.empty
    for col in [
        "gl_line_id",
        "txn_id",
        "date",
        "month",
        "account_id",
        "account_name",
        "account_type",
        "normal_side",
        "debit",
        "credit",
        "raw_amount",
        "amount",
    ]:
        assert col in tidy.columns

    # Signed amount should equal raw_amount for debit-normal accounts, and flip for credit-normal.
    debit_norm = tidy[tidy["normal_side"].astype(str).str.lower() == "debit"]
    if not debit_norm.empty:
        assert (debit_norm["amount"] - debit_norm["raw_amount"]).abs().max() < 1e-6

    credit_norm = tidy[tidy["normal_side"].astype(str).str.lower() == "credit"]
    if not credit_norm.empty:
        assert (credit_norm["amount"] + credit_norm["raw_amount"]).abs().max() < 1e-6

    # --- monthly summary
    monthly = result.gl_monthly_summary
    assert not monthly.empty
    for col in ["month", "account_id", "account_name", "account_type", "normal_side", "n_lines", "debit", "credit", "net_change"]:
        assert col in monthly.columns

    # Rollup consistency: sum of net_change equals sum of tidy amounts (for the same period)
    assert abs(float(monthly["net_change"].sum()) - float(tidy["amount"].sum())) < 1e-6


def test_ch07_summary_contains_quality_fields(tmp_path: Path) -> None:
    outdir = tmp_path / "nso_v1"
    outputs = simulate_nso_v1(start_month="2025-01", n_months=3, random_state=123)
    write_nso_v1(outputs, outdir)

    result = analyze_ch07(outdir)
    summary = result.summary

    assert "metrics" in summary
    assert "checks" in summary
    assert "data_dictionary" in summary

    # Common metrics
    assert summary["metrics"]["n_gl_lines"] > 0
    assert summary["metrics"]["n_accounts"] > 0

    # Quality checks present
    assert "all_gl_dates_parse" in summary["checks"]
    assert "coa_join_coverage_ok" in summary["checks"]
