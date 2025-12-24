# SPDX-License-Identifier: MIT
# test_business_ch10_probability_risk.py

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.business_ch10_probability_risk import analyze_ch10
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_analyze_ch10_writes_expected_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    sim = simulate_nso_v1(start_month="2025-01", n_months=12, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    outputs = analyze_ch10(datadir=datadir, outdir=outdir, seed=123)

    assert outputs.manifest_path.exists()
    assert outputs.memo_path.exists()
    assert outputs.summary_path.exists()
    assert outputs.figures_dir.exists()

    manifest = pd.read_csv(outputs.manifest_path)
    assert {"filename", "chart_type", "title", "x_label", "y_label", "guardrail_note", "data_source"}.issubset(
        set(manifest.columns)
    )

    # Expect the core Chapter 10 figures to be present
    expected_files = {
        "ch10_cash_flow_hist.png",
        "ch10_cash_buffer_ecdf.png",
        "ch10_bad_debt_loss_ecdf.png",
    }
    assert expected_files.issubset(set(manifest["filename"].tolist()))

    for p in outputs.figure_paths:
        assert p.exists()

    summary = json.loads(outputs.summary_path.read_text(encoding="utf-8"))

    assert summary["chapter"] == "business_ch10_probability_risk"
    assert summary["cash_buffer"]["confidence"] == 0.95

    # Buffer should be non-negative and finite.
    buf = float(summary["cash_buffer"]["buffer_p95"])
    assert buf >= 0.0

    # Bad debt stats should include expected loss and p90 worst-case loss.
    assert "bad_debt" in summary
    assert "expected_loss" in summary["bad_debt"]
    assert "worst_case_loss_p90" in summary["bad_debt"]


def test_risk_memo_contains_operational_probability_language(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    sim = simulate_nso_v1(start_month="2025-01", n_months=12, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    outputs = analyze_ch10(datadir=datadir, outdir=outdir, seed=123)
    memo = outputs.memo_path.read_text(encoding="utf-8")

    # We want the translation: probability -> "1 out of every N" wording.
    assert "out of every" in memo

    # Memo should be compact.
    bullet_lines = [ln for ln in memo.splitlines() if ln.startswith("-")]
    assert len(bullet_lines) <= 10
