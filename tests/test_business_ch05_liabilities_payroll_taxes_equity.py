from __future__ import annotations

import pathlib

from scripts.business_ch05_liabilities_payroll_taxes_equity import analyze_ch05
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch05_end_to_end(tmp_path: pathlib.Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    outputs = simulate_nso_v1(outdir=datadir, seed=123, start_month="2025-01", n_months=6)
    write_nso_v1(outputs, datadir)

    summary = analyze_ch05(datadir=datadir, outdir=outdir, seed=123)

    # Files exist
    assert (outdir / "business_ch05_summary.json").exists()
    assert (outdir / "business_ch05_wages_payable_rollforward.csv").exists()
    assert (outdir / "business_ch05_payroll_taxes_payable_rollforward.csv").exists()
    assert (outdir / "business_ch05_sales_tax_payable_rollforward.csv").exists()
    assert (outdir / "business_ch05_notes_payable_rollforward.csv").exists()
    assert (outdir / "business_ch05_liabilities_over_time.png").exists()

    # Key tie-outs are true
    checks = summary.checks
    assert checks["transactions_balanced"] is True
    assert checks["payroll_expense_ties_to_gl"] is True
    assert checks["payroll_tax_expense_ties_to_gl"] is True
    assert checks["wages_payable_rollforward_ties"] is True
    assert checks["payroll_taxes_payable_rollforward_ties"] is True
    assert checks["sales_tax_payable_rollforward_ties"] is True
    assert checks["interest_expense_ties_to_gl"] is True
    assert checks["notes_payable_rollforward_ties"] is True
    assert checks["accounts_payable_rollforward_ties"] is True
    assert checks["owner_contributions_tie_to_gl"] is True
    assert checks["owner_draws_tie_to_gl"] is True
