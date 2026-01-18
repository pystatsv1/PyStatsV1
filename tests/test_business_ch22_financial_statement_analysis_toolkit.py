from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch22_financial_statement_analysis_toolkit import analyze_ch22
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch22_outputs_and_schema(tmp_path: Path) -> None:
    # Arrange: generate deterministic NSO v1 synthetic data
    datadir = tmp_path / "data" / "synthetic" / "nso_v1"
    outdir = tmp_path / "outputs" / "track_d"

    outputs = simulate_nso_v1(seed=123)
    write_nso_v1(outputs, outdir=datadir)

    # Act
    out = analyze_ch22(datadir=datadir, outdir=outdir, seed=123)

    # Assert: expected artifacts exist
    for p in [
        out.ratios_monthly_csv,
        out.common_size_is_csv,
        out.common_size_bs_csv,
        out.variance_bridge_latest_csv,
        out.assumptions_csv,
        out.design_json,
        out.memo_md,
        out.figures_manifest_csv,
    ]:
        assert p.exists(), f"Missing artifact: {p}"

    ratios = pd.read_csv(out.ratios_monthly_csv)
    required_ratio_cols = {
        "month",
        "revenue",
        "net_income",
        "gross_margin",
        "operating_margin",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
        "dso_days",
        "dio_days",
        "dpo_days",
        "cash_conversion_cycle_days",
        "asset_turnover_annual",
        "roa_annual",
    }
    assert required_ratio_cols.issubset(set(ratios.columns))
    assert len(ratios) >= 12

    cs_is = pd.read_csv(out.common_size_is_csv)
    assert {"month", "line", "amount", "pct_of_revenue"}.issubset(set(cs_is.columns))

    cs_bs = pd.read_csv(out.common_size_bs_csv)
    assert {"month", "line", "amount", "pct_of_total_assets"}.issubset(
        set(cs_bs.columns)
    )

    bridge = pd.read_csv(out.variance_bridge_latest_csv)
    assert {"component", "amount"}.issubset(set(bridge.columns))
    assert bridge.iloc[0]["component"].startswith("Start")
    assert bridge.iloc[-1]["component"].startswith("End")

    # Figures exist and match manifest
    manifest = pd.read_csv(out.figures_manifest_csv)
    required_manifest_cols = {
        "filename",
        "chart_type",
        "title",
        "x_label",
        "y_label",
        "data_source",
        "guardrail_note",
    }
    assert required_manifest_cols.issubset(set(manifest.columns))
    assert len(manifest) >= 3

    figdir = outdir / "figures"
    for fn in manifest["filename"].tolist():
        assert (figdir / fn).exists(), f"Missing figure in manifest: {fn}"

    # A tiny schema sanity check: chart types should be populated.
    assert manifest["chart_type"].astype(str).str.len().min() > 0
