from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.business_ch12_hypothesis_testing_decisions import analyze_ch12
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_analyze_ch12_writes_expected_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    sim = simulate_nso_v1(start_month="2025-01", n_months=12, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    outputs = analyze_ch12(datadir=datadir, outdir=outdir, seed=123)

    assert outputs.manifest_path.exists()
    assert outputs.memo_path.exists()
    assert outputs.summary_path.exists()
    assert outputs.design_path.exists()
    assert outputs.figures_dir.exists()

    manifest = pd.read_csv(outputs.manifest_path)
    assert {"filename", "chart_type", "title", "x_label", "y_label", "guardrail_note", "data_source"}.issubset(
        set(manifest.columns)
    )

    expected_files = {
        "ch12_cycle_time_means_bar.png",
        "ch12_promo_bootstrap_hist.png",
    }
    assert expected_files.issubset(set(manifest["filename"].tolist()))

    for p in outputs.figure_paths:
        assert p.exists()

    summary = json.loads(outputs.summary_path.read_text(encoding="utf-8"))
    assert summary["chapter"] == "business_ch12_hypothesis_testing_decisions"

    assert "promotion_test" in summary
    assert "cycle_time_test" in summary

    assert 0.0 <= float(summary["promotion_test"]["p_value"]) <= 1.0
    assert 0.0 <= float(summary["cycle_time_test"]["p_value"]) <= 1.0

    # We expect the teaching setup to have a non-trivial uplift and cycle-time reduction.
    assert float(summary["promotion_test"]["uplift_pct_assumed"]) > 0.0
    assert float(summary["cycle_time_test"]["reduction_days_assumed"]) > 0.0


def test_ch12_is_deterministic_for_seed(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"

    sim = simulate_nso_v1(start_month="2025-01", n_months=12, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    a = analyze_ch12(datadir=datadir, outdir=out1, seed=123)
    b = analyze_ch12(datadir=datadir, outdir=out2, seed=123)

    sa = json.loads(a.summary_path.read_text(encoding="utf-8"))
    sb = json.loads(b.summary_path.read_text(encoding="utf-8"))

    assert sa == sb
