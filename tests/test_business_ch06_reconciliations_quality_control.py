# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch06_reconciliations_quality_control import analyze_ch06, write_ch06_outputs
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch06_reconciliations_quality_control(tmp_path: Path) -> None:
    ds_dir = tmp_path / "nso_v1"
    outs = simulate_nso_v1(random_state=123, n_months=6)
    write_nso_v1(outs, ds_dir)

    out_dir = tmp_path / "derived" / "business" / "ch06"
    result = analyze_ch06(datadir=ds_dir)
    write_ch06_outputs(result, outdir=out_dir)

    expected = {
        "ar_rollforward.csv",
        "bank_recon_matches.csv",
        "bank_recon_exceptions.csv",
        "ch06_summary.json",
    }
    assert expected.issubset({p.name for p in out_dir.iterdir()})

    exc = pd.read_csv(out_dir / "bank_recon_exceptions.csv")
    assert "exception_type" in exc.columns

    # Simulator injects:
    # - fee row (no GL link) => bank_unmatched_item
    # - duplicate bank_txn_id => bank_duplicate_txn_id
    assert "bank_unmatched_item" in set(exc["exception_type"].astype(str))
    assert "bank_duplicate_txn_id" in set(exc["exception_type"].astype(str))

    ar_roll = pd.read_csv(out_dir / "ar_rollforward.csv")
    assert ar_roll["diff"].abs().max() < 1e-6
