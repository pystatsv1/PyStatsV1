from __future__ import annotations

from pathlib import Path

from scripts.business_ch03_statements_as_summaries import analyze_ch03
from scripts.sim_business_ledgerlab import simulate_ledgerlab_month, write_ledgerlab


def test_ch03_creates_bridge_and_reconciles(tmp_path: Path) -> None:
    outs = simulate_ledgerlab_month(month="2025-01", n_sales=6, random_state=123)
    write_ledgerlab(outs, tmp_path)

    outdir = tmp_path / "out"
    summary = analyze_ch03(tmp_path, outdir, seed=123)

    # Key outputs exist
    assert (outdir / "business_ch03_summary.json").exists()
    assert (outdir / "business_ch03_statement_bridge.csv").exists()
    assert (outdir / "business_ch03_trial_balance.csv").exists()
    assert (outdir / "business_ch03_net_income_vs_cash_change.png").exists()

    # Core reconciliations should pass on simulated data
    assert summary.checks["transactions_balanced"] is True
    assert summary.checks["trial_balance_matches_source"] is True
    assert summary.checks["income_statement_ties_to_trial_balance"] is True
    assert summary.checks["balance_sheet_equation_balances"] is True
    assert summary.checks["cash_flow_ties_to_balance_sheet_cash"] is True
