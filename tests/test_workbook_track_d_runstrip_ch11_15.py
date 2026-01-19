from __future__ import annotations

from pathlib import Path


def test_track_d_run_strip_present_ch11_15() -> None:
    """Guardrail: keep the Track D 'PyPI run strip' present for chapters 11–15."""

    repo_root = Path(__file__).resolve().parents[1]

    chapters = {
        "docs/source/business_ch11_sampling_estimation_audit_controls.rst": "d11",
        "docs/source/business_ch12_hypothesis_testing_decisions.rst": "d12",
        "docs/source/business_ch13_correlation_causation_controlled_comparisons.rst": "d13",
        "docs/source/business_ch14_regression_driver_analysis.rst": "d14",
        "docs/source/business_ch15_forecasting_foundations.rst": "d15",
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
