# SPDX-License-Identifier: MIT
# test_business_ch09_reporting_style_contract.py

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch09_reporting_style_contract import _make_executive_memo, analyze_ch09
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

    # Bridge chart (net income waterfall) should be present
    assert (manifest["filename"] == "net_income_bridge.png").any()
    assert len(outputs.figure_paths) >= 3
    for p in outputs.figure_paths:
        assert p.exists()


def test_make_executive_memo_flags_unstable_percent_metrics_and_extreme_dso() -> None:
    # Construct small, deterministic inputs that trigger guardrails.
    kpi = pd.DataFrame(
        {
            "month": ["2025-01", "2025-02", "2025-03"],
            # tiny latest revenue makes margins/growth unstable vs typical (median = 80)
            "revenue": [100_000.0, 80.0, 50.0],
            "net_income": [10_000.0, 5.0, -10.0],
            "gross_margin_pct": [0.40, 0.25, 0.20],
            "net_margin_pct": [0.10, 0.05, -0.20],
            "revenue_growth_pct": [pd.NA, -0.9992, -0.375],
        }
    )

    ar_monthly = pd.DataFrame({"month": ["2025-03"], "dso": [150.0], "collections_rate": [0.20]})
    ar_days_stats = pd.DataFrame({"customer": ["ALL"], "median_days": [28.0], "p90_days": [75.0]})

    memo = _make_executive_memo(kpi=kpi, ar_monthly=ar_monthly, ar_days_stats=ar_days_stats)

    # Percent metrics should be flagged when the denominator is small.
    assert "Gross margin:" in memo and "flag: denominator small" in memo
    assert "Net margin:" in memo and "flag: denominator small" in memo
    assert "MoM revenue growth:" in memo and "flag: denominator small" in memo

    # Extreme DSO should be flagged as needing investigation.
    assert "DSO (approx):" in memo and "needs investigation" in memo

    # Memo must remain 10 bullets max.
    bullet_lines = [ln for ln in memo.splitlines() if ln.startswith("-")]
    assert len(bullet_lines) <= 10
