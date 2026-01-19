from __future__ import annotations

from pathlib import Path


def test_track_d_run_strip_present_ch06_10() -> None:
    """Guardrail: keep the Track D 'PyPI run strip' present for chapters 6–10."""

    repo_root = Path(__file__).resolve().parents[1]

    chapters = {
        "docs/source/business_ch06_reconciliations_quality_control.rst": "d06",
        "docs/source/business_ch07_preparing_accounting_data_for_analysis.rst": "d07",
        "docs/source/business_ch08_descriptive_statistics_financial_performance.rst": "d08",
        "docs/source/business_ch09_reporting_style_contract.rst": "d09",
        "docs/source/business_ch10_probability_risk.rst": "d10",
    }

    for relpath, run in chapters.items():
        path = repo_root / relpath
        assert path.exists(), f"Missing expected Track D chapter file: {relpath}"

        text = path.read_text(encoding="utf-8")
        assert f".. |trackd_run| replace:: {run}" in text, (
            f"Missing run substitution for {relpath}. Expected run id: {run}"
        )
        assert ".. include:: _includes/track_d_run_strip.rst" in text, (
            f"Missing run-strip include in {relpath}."
        )
