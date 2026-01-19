"""Guardrails for Track D PyPI run strip.

These Track D chapters are included in the full docs build and should always
include the standard Track D "run strip" so learners can reproduce outputs
from the PyPI-installed workbook.
"""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


SOURCES = {
    "docs/source/business_ch21_scenario_planning_sensitivity_stress.rst": "d21",
    "docs/source/business_ch22_financial_statement_analysis_toolkit.rst": "d22",
    "docs/source/business_ch23_communicating_results_governance.rst": "d23",
}


@pytest.mark.parametrize("rel_path, run_id", SOURCES.items())
def test_track_d_run_strip_present(rel_path: str, run_id: str) -> None:
    text = (ROOT / rel_path).read_text(encoding="utf-8")
    assert f".. |trackd_run| replace:: {run_id}" in text
    assert ".. include:: _includes/track_d_run_strip.rst" in text
