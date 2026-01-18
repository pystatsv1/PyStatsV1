# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.business_ch23_communicating_results_governance import analyze_ch23
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch23_templates_exist_and_schema(tmp_path: Path) -> None:
    # Arrange: generate deterministic NSO v1 synthetic data
    datadir = tmp_path / "data" / "synthetic" / "nso_v1"
    outdir = tmp_path / "outputs" / "track_d"

    outputs = simulate_nso_v1(seed=123)
    write_nso_v1(outputs, outdir=datadir)

    # Act
    out = analyze_ch23(datadir=datadir, outdir=outdir, seed=123)

    # Assert: artifacts exist
    for p in [
        out.memo_template_md,
        out.kpi_governance_template_csv,
        out.dashboard_spec_template_csv,
        out.red_team_checklist_md,
        out.design_json,
    ]:
        assert p.exists(), f"Missing artifact: {p}"

    # KPI governance schema
    kpi = pd.read_csv(out.kpi_governance_template_csv)
    required_cols = {
        "kpi_name",
        "definition",
        "formula",
        "source_table",
        "source_columns",
        "owner_role",
        "update_cadence",
        "threshold_green",
        "threshold_yellow",
        "threshold_red",
        "notes",
    }
    assert required_cols.issubset(set(kpi.columns))
    assert len(kpi) >= 8

    # Memo template contains core sections
    memo = out.memo_template_md.read_text(encoding="utf-8")
    for needle in [
        "Executive Update",
        "What happened",
        "Why it happened",
        "What we recommend next",
        "Risks",
        "Assumptions",
    ]:
        assert needle in memo

    # Design file includes expected fields and lists artifacts
    design = json.loads(out.design_json.read_text(encoding="utf-8"))
    assert design["chapter"].startswith("Track D")
    assert design["seed"] == 123
    artifact_names = {Path(p).name for p in design["artifacts"]}
    assert out.memo_template_md.name in artifact_names
    assert out.kpi_governance_template_csv.name in artifact_names
