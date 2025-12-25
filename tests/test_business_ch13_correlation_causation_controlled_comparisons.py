from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.business_ch13_correlation_causation_controlled_comparisons import analyze_ch13
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_ch13_writes_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "data"
    outdir = tmp_path / "out"

    nso = simulate_nso_v1(start_month="2025-01", n_months=24, random_state=123)
    write_nso_v1(nso, outdir=datadir)

    outputs = analyze_ch13(datadir=datadir, outdir=outdir, seed=123)

    assert outputs.design_path.exists()
    assert outputs.summary_path.exists()
    assert outputs.memo_path.exists()
    assert outputs.manifest_path.exists()
    assert outputs.figures_dir.exists()

    design = json.loads(outputs.design_path.read_text(encoding="utf-8"))
    summary = json.loads(outputs.summary_path.read_text(encoding="utf-8"))

    assert design["chapter"] == "ch13"
    assert summary["chapter"] == "ch13"
    assert summary["n_months"] >= 12
    assert "correlations" in summary

    manifest = pd.read_csv(outputs.manifest_path)
    assert len(manifest) == 3
