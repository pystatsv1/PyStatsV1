from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from scripts.business_ch20_integrated_forecasting_three_statements import analyze_ch20
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch20_outputs_exist_and_reconcile(tmp_path: Path) -> None:
    out = simulate_nso_v1(seed=123)
    write_nso_v1(out, tmp_path)

    outdir = tmp_path / "outputs"
    res = analyze_ch20(datadir=tmp_path, outdir=outdir, seed=123)

    assert res.pnl_forecast_monthly_csv.exists()
    assert res.balance_sheet_forecast_monthly_csv.exists()
    assert res.cash_flow_forecast_monthly_csv.exists()
    assert res.assumptions_csv.exists()
    assert res.design_json.exists()
    assert res.memo_md.exists()
    assert res.figures_manifest_csv.exists()

    pnl = pd.read_csv(res.pnl_forecast_monthly_csv)
    assert set(pnl.columns) >= {"month", "sales_revenue", "cogs", "operating_expenses", "net_income"}
    assert len(pnl) == 12
    assert pnl["month"].nunique() == 12

    bs = pd.read_csv(res.balance_sheet_forecast_monthly_csv)
    required_bs = {
        "month",
        "cash",
        "accounts_receivable",
        "inventory",
        "net_ppe",
        "accounts_payable",
        "notes_payable",
        "owner_capital",
        "retained_earnings",
        "owner_draw",
        "total_assets",
        "total_liabilities",
        "total_equity",
        "total_liabilities_equity",
        "balance_check",
    }
    assert required_bs.issubset(set(bs.columns))
    assert len(bs) == 12

    # Balance sheet should tie (within small numerical tolerance).
    assert (bs["balance_check"].abs() < 1e-6).all()

    cf = pd.read_csv(res.cash_flow_forecast_monthly_csv)
    required_cf = {
        "month",
        "beginning_cash",
        "ending_cash_balance_sheet",
        "ending_cash_from_bridge",
        "tieout_delta",
        "reconciliation_residual",
    }
    assert required_cf.issubset(set(cf.columns))
    assert len(cf) == 12
    assert (cf["tieout_delta"].abs() < 1e-6).all()

    design = json.loads(res.design_json.read_text(encoding="utf-8"))
    assert design["chapter"] == "Track D — Chapter 20"
    assert int(design["horizon_months"]) == 12

    mf = pd.read_csv(res.figures_manifest_csv)
    assert len(mf) >= 2
    figs_dir = outdir / "figures"
    for fname in mf["filename"].astype(str).tolist():
        assert (figs_dir / fname).exists()

    memo = res.memo_md.read_text(encoding="utf-8")
    assert "three statements" in memo.lower()
    assert "cash" in memo.lower()
