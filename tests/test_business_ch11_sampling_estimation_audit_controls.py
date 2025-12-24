# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.business_ch11_sampling_estimation_audit_controls import analyze_ch11
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_analyze_ch11_writes_expected_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "out"

    sim = simulate_nso_v1(start_month="2025-01", n_months=12, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    outputs = analyze_ch11(datadir=datadir, outdir=outdir, seed=123)

    assert outputs.sampling_plan_path.exists()
    assert outputs.memo_path.exists()
    assert outputs.summary_path.exists()
    assert outputs.manifest_path.exists()
    assert outputs.figures_dir.exists()

    manifest = pd.read_csv(outputs.manifest_path)
    assert {"filename", "chart_type", "title", "x_label", "y_label", "guardrail_note", "data_source"}.issubset(
        set(manifest.columns)
    )

    expected_files = {"ch11_strata_sampling_bar.png", "ch11_error_rate_ci.png"}
    assert expected_files.issubset(set(manifest["filename"].tolist()))

    for p in outputs.figure_paths:
        assert p.exists()

    plan = json.loads(outputs.sampling_plan_path.read_text(encoding="utf-8"))
    assert "population_n" in plan and plan["population_n"] > 0
    assert "sample_n" in plan and plan["sample_n"] >= 0
    assert "selected_invoice_ids" in plan

    summary = json.loads(outputs.summary_path.read_text(encoding="utf-8"))
    assert summary["chapter"] == "business_ch11_sampling_estimation_audit_controls"
    assert summary["ci"]["confidence"] == 0.95
    assert summary["ci"]["method"] == "wilson"
    assert 0.0 <= float(summary["ci"]["ci_low"]) <= 1.0
    assert 0.0 <= float(summary["ci"]["ci_high"]) <= 1.0

    # Worked example should be present and well-formed
    we = summary["worked_example"]
    assert we["n"] == 50
    assert we["k_errors"] == 2
    assert we["confidence"] == 0.95


def test_ch11_sampling_is_deterministic_for_seed(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"

    sim = simulate_nso_v1(start_month="2025-01", n_months=12, random_state=123)
    write_nso_v1(sim, outdir=datadir)

    a = analyze_ch11(datadir=datadir, outdir=out1, seed=123)
    b = analyze_ch11(datadir=datadir, outdir=out2, seed=123)

    plan_a = json.loads(a.sampling_plan_path.read_text(encoding="utf-8"))
    plan_b = json.loads(b.sampling_plan_path.read_text(encoding="utf-8"))

    assert plan_a["selected_invoice_ids"] == plan_b["selected_invoice_ids"]
