from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1
from scripts.business_ch21_scenario_planning_sensitivity_stress import analyze_ch21


def test_business_ch21_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "data" / "synthetic" / "nso_v1"
    outdir = tmp_path / "outputs" / "track_d"
    outputs_sim = simulate_nso_v1(seed=123)
    write_nso_v1(outputs_sim, datadir)

    outputs = analyze_ch21(datadir=datadir, outdir=outdir, seed=123, horizon_months=12)

    # Core artifacts exist.
    assert outputs.scenario_pack_monthly_csv.exists()
    assert outputs.sensitivity_summary_csv.exists()
    assert outputs.assumptions_csv.exists()
    assert outputs.governance_template_csv.exists()
    assert outputs.design_json.exists()
    assert outputs.memo_md.exists()
    assert outputs.figures_manifest_csv.exists()

    # Scenario pack contract.
    pack = pd.read_csv(outputs.scenario_pack_monthly_csv)
    required_cols = {
        "month",
        "scenario",
        "sales_revenue",
        "net_income",
        "ending_cash",
        "buffer_target_monthly",
        "buffer_trigger",
    }
    assert required_cols.issubset(pack.columns)

    scenarios = set(pack["scenario"].astype(str).unique())
    assert {"Base", "Best", "Worst", "Stress_Revenue_Drop"}.issubset(scenarios)
    for s in ["Base", "Best", "Worst", "Stress_Revenue_Drop"]:
        n = int((pack["scenario"] == s).sum())
        assert n == 12

    # Sensitivity contract.
    sens = pd.read_csv(outputs.sensitivity_summary_csv)
    sens_cols = {"lever", "shock", "min_ending_cash", "months_below_buffer", "delta_min_cash_vs_base"}
    assert sens_cols.issubset(sens.columns)
    assert len(sens) >= 6

    # Design contract.
    design = json.loads(outputs.design_json.read_text(encoding="utf-8"))
    assert design.get("chapter") == "Track D — Chapter 21"
    assert design.get("horizon_months") == 12
    assert isinstance(design.get("scenarios"), list)

    # Figures match manifest.
    manifest = pd.read_csv(outputs.figures_manifest_csv)
    assert {"filename", "title", "kind"}.issubset(manifest.columns)
    figdir = outdir / "figures"
    for fname in manifest["filename"].astype(str).tolist():
        assert (figdir / fname).exists()
