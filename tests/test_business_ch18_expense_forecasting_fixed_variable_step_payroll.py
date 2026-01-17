from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from scripts.business_ch18_expense_forecasting_fixed_variable_step_payroll import analyze_ch18
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch18_outputs_exist_and_contract(tmp_path: Path) -> None:
    out = simulate_nso_v1(seed=123)
    write_nso_v1(out, tmp_path)

    outdir = tmp_path / "outputs"
    res = analyze_ch18(datadir=tmp_path, outdir=outdir, seed=123)

    assert res.expense_monthly_by_account_csv.exists()
    assert res.payroll_monthly_csv.exists()
    assert res.expense_behavior_map_csv.exists()
    assert res.payroll_scenarios_forecast_csv.exists()
    assert res.expense_forecast_detail_csv.exists()
    assert res.expense_forecast_summary_csv.exists()
    assert res.control_plan_template_csv.exists()
    assert res.design_json.exists()
    assert res.memo_md.exists()
    assert res.figures_manifest_csv.exists()

    hist = pd.read_csv(res.expense_monthly_by_account_csv)
    assert "month" in hist.columns
    assert len(hist) == 24

    # Key expense lines should be present (from the NSO chart of accounts)
    expected_cols = {
        "rent_expense",
        "utilities_expense",
        "payroll_expense",
        "payroll_tax_expense",
        "depreciation_expense",
        "interest_expense",
        "operating_expenses_total",
    }
    assert expected_cols.issubset(set(hist.columns))

    payroll = pd.read_csv(res.payroll_monthly_csv)
    assert set(payroll.columns) >= {"month", "gross_wages", "employer_tax", "total_payroll_cost"}
    assert payroll["month"].nunique() == 24

    fc_sum = pd.read_csv(res.expense_forecast_summary_csv)
    assert set(fc_sum.columns) >= {
        "month",
        "scenario",
        "rent_expense",
        "utilities_expense",
        "payroll_expense",
        "payroll_tax_expense",
        "depreciation_expense",
        "interest_expense",
        "operating_expenses_total",
        "controllable_expenses_total",
    }
    assert set(fc_sum["scenario"].astype(str)) == {"Lean", "Base", "Growth"}
    assert len(fc_sum) == 12 * 3

    design = json.loads(res.design_json.read_text(encoding="utf-8"))
    assert design["chapter"] == "Track D — Chapter 18"
    assert design["forecast_horizon_months"] == 12
    assert set(design["payroll_scenarios"].keys()) == {"Lean", "Base", "Growth"}

    mf = pd.read_csv(res.figures_manifest_csv)
    assert len(mf) >= 2
    figs_dir = outdir / "figures"
    for fname in mf["filename"].astype(str).tolist():
        assert (figs_dir / fname).exists()

    memo = res.memo_md.read_text(encoding="utf-8")
    assert "Chapter 18" in memo
    assert "Payroll" in memo
