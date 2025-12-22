from __future__ import annotations

from pathlib import Path

from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_nso_v1_writes_required_tables(tmp_path: Path) -> None:
    outs = simulate_nso_v1(start_month="2025-01", n_months=6, random_state=123)
    write_nso_v1(outs, tmp_path)

    required = [
        "chart_of_accounts.csv",
        "gl_journal.csv",
        "trial_balance_monthly.csv",
        "statements_is_monthly.csv",
        "statements_bs_monthly.csv",
        "statements_cf_monthly.csv",
        "inventory_movements.csv",
        "fixed_assets.csv",
        "depreciation_schedule.csv",
        "nso_v1_meta.json",
         # --- Chapter 5 additions ---
         "payroll_events.csv",
         "sales_tax_events.csv",
         "debt_schedule.csv",
         "equity_events.csv",
         "ap_events.csv",
         # --- Chapter 6 additions ---
         "ar_events.csv",
         "bank_statement.csv",
    ]
    for f in required:
        assert (tmp_path / f).exists()
