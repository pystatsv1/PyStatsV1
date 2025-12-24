# SPDX-License-Identifier: MIT
# test_business_ch09_reporting_style_contract.py

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch09_reporting_style_contract import analyze_ch09
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_analyze_ch09_writes_expected_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    sim = simulate_nso_v1(start_month="2025-01", n_months=8, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    outputs = analyze_ch09(datadir=datadir, outdir=outdir, seed=123)

    assert outputs.contract_path.exists()
    assert outputs.manifest_path.exists()
    assert outputs.memo_path.exists()
    assert outputs.summary_path.exists()
    assert outputs.figures_dir.exists()

    manifest = pd.read_csv(outputs.manifest_path)
    assert {"filename", "chart_type", "title", "x_label", "y_label", "guardrail_note", "data_source"}.issubset(
        set(manifest.columns)
    )
    assert len(outputs.figure_paths) >= 3
    for p in outputs.figure_paths:
        assert p.exists()
