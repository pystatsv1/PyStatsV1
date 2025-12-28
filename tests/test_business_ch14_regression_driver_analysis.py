from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch14_regression_driver_analysis import analyze_ch14
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch14_outputs_exist_and_manifest_has_figures(tmp_path: Path) -> None:
    # Arrange: create NSO synthetic inputs in tmp_path
    out = simulate_nso_v1(seed=123)
    write_nso_v1(out, tmp_path)

    outdir = tmp_path / "outputs"
    res = analyze_ch14(datadir=tmp_path, outdir=outdir, seed=123)

    # core artifacts exist
    assert res.driver_table_csv.exists()
    assert res.design_json.exists()
    assert res.summary_json.exists()
    assert res.memo_md.exists()
    assert res.figures_manifest_csv.exists()

    # manifest has at least 2 figures and files exist
    mf = pd.read_csv(res.figures_manifest_csv)
    assert len(mf) >= 2

    figs_dir = outdir / "figures"
    for fname in mf["filename"].tolist():
        assert (figs_dir / fname).exists()