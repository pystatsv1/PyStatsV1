from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from scripts.business_ch19_cash_flow_forecasting_direct_method_13_week import analyze_ch19
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch19_outputs_exist_and_contract(tmp_path: Path) -> None:
    out = simulate_nso_v1(seed=123)
    write_nso_v1(out, tmp_path)

    outdir = tmp_path / "outputs"
    res = analyze_ch19(datadir=tmp_path, outdir=outdir, seed=123)

    assert res.cash_history_weekly_csv.exists()
    assert res.cash_forecast_13w_scenarios_csv.exists()
    assert res.cash_assumptions_csv.exists()
    assert res.cash_governance_template_csv.exists()
    assert res.design_json.exists()
    assert res.memo_md.exists()
    assert res.figures_manifest_csv.exists()

    hist = pd.read_csv(res.cash_history_weekly_csv)
    assert set(hist.columns) >= {
        "week_start",
        "cash_in_total",
        "cash_out_total",
        "net_cash_flow",
        "ending_cash",
    }
    # We expect substantial history (NSO v1 is 24 months of activity)
    assert len(hist) >= 60

    fc = pd.read_csv(res.cash_forecast_13w_scenarios_csv)
    required_fc_cols = {
        "week_start",
        "scenario",
        "beginning_cash",
        "cash_in_total",
        "cash_out_total",
        "net_cash_flow",
        "ending_cash",
        "buffer_target",
        "buffer_trigger",
    }
    assert required_fc_cols.issubset(set(fc.columns))

    scenarios = sorted(fc["scenario"].astype(str).unique().tolist())
    assert scenarios == ["Base", "Stress_Delayed_Collections", "Stress_Supplier_Terms_Tighten"]

    for s in scenarios:
        df = fc.loc[fc["scenario"].astype(str) == s].copy()
        assert len(df) == 13
        assert df["week_start"].nunique() == 13

    design = json.loads(res.design_json.read_text(encoding="utf-8"))
    assert design["chapter"] == "Track D — Chapter 19"
    assert int(design["horizon_weeks"]) == 13
    assert design["scenarios"] == scenarios

    mf = pd.read_csv(res.figures_manifest_csv)
    assert len(mf) >= 2
    figs_dir = outdir / "figures"
    for fname in mf["filename"].astype(str).tolist():
        assert (figs_dir / fname).exists()

    memo = res.memo_md.read_text(encoding="utf-8")
    assert "13-week" in memo
    assert "direct method" in memo.lower()
