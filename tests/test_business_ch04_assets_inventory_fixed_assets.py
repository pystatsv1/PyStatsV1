from __future__ import annotations

from pathlib import Path

from scripts.business_ch04_assets_inventory_fixed_assets import analyze_ch04
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_ch04_runs_and_ties_out(tmp_path: Path) -> None:
    datadir = tmp_path / "data"
    outdir = tmp_path / "out"

    outs = simulate_nso_v1(start_month="2025-01", n_months=6, random_state=123)
    write_nso_v1(outs, datadir)

    summary = analyze_ch04(datadir, outdir, seed=123)

    # outputs exist
    assert (outdir / "business_ch04_summary.json").exists()
    assert (outdir / "business_ch04_inventory_rollforward.csv").exists()
    assert (outdir / "business_ch04_margin_bridge.csv").exists()
    assert (outdir / "business_ch04_depreciation_rollforward.csv").exists()

    # tie-outs
    assert summary.checks["inventory_subledger_ties_to_gl_inventory"] is True
    assert summary.checks["cogs_subledger_ties_to_gl_cogs"] is True
    assert summary.checks["depreciation_schedule_ties_to_gl_dep_expense"] is True
    assert summary.checks["accum_dep_ties_to_gl_accum_dep"] is True
