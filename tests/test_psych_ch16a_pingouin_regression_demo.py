"""
Tests for Chapter 16a Pingouin regression appendix demo.

We check that:

- The regression tables have the expected structure.
- Key coefficients have the expected *signs*.
- The partial correlation exam_score ~ study_hours | stress, motivation
  is positive and reasonably strong.
"""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch16_regression import simulate_psych_regression_dataset
from scripts.psych_ch16a_pingouin_regression_demo import (
    build_pingouin_regression_tables,
    compute_partial_corr_exam_study,
    run_ch16a_demo,
)


def test_build_pingouin_regression_tables_structure_and_signs() -> None:
    """Regression tables should have expected columns and coefficient signs."""
    df = simulate_psych_regression_dataset(n=300, random_state=123)

    raw_table, standardized_table = build_pingouin_regression_tables(df)

    # Basic shape checks
    assert isinstance(raw_table, pd.DataFrame)
    assert isinstance(standardized_table, pd.DataFrame)
    assert {"names", "coef", "se", "T", "pval", "r2", "adj_r2"}.issubset(
        set(raw_table.columns)
    )
    assert {"names", "coef", "se", "T", "pval", "r2", "adj_r2"}.issubset(
        set(standardized_table.columns)
    )

    # Coefficients signs in the raw table
    raw_coeffs = dict(zip(raw_table["names"], raw_table["coef"]))

    # We expect:
    # - study_hours: positive
    # - sleep_hours: positive
    # - stress: negative
    # (Motivation sign may depend on the simulation; check only the main three.)
    assert raw_coeffs["study_hours"] > 0
    assert raw_coeffs["sleep_hours"] > 0
    assert raw_coeffs["stress"] < 0

    # R^2 should be reasonably large (model explains a good chunk of variance)
    r2 = float(raw_table["r2"].iloc[0])
    assert 0.5 < r2 < 1.0


def test_partial_corr_exam_study_reasonable() -> None:
    """Partial correlation exam_score ~ study_hours | stress, motivation should be positive."""
    df = simulate_psych_regression_dataset(n=300, random_state=456)

    partial = compute_partial_corr_exam_study(df)
    # Pingouin returns a 1-row DataFrame
    assert partial.shape[0] == 1

    r = float(partial["r"].iloc[0])
    p = float(partial["p-val"].iloc[0])

    # Expect a positive and non-trivial partial correlation
    assert r > 0.3
    assert p < 0.001


def test_run_ch16a_demo_end_to_end(tmp_path, monkeypatch) -> None:
    """End-to-end smoke test: the demo should run and return expected keys.

    We also redirect TRACK_B outputs to a temporary directory so the test
    does not depend on local paths.
    """
    # Monkeypatch the TRACK_B_DIR inside the module to write into tmp_path
    import scripts.psych_ch16a_pingouin_regression_demo as demo_mod

    demo_mod.TRACK_B_DIR = tmp_path
    tmp_path.mkdir(parents=True, exist_ok=True)

    results = run_ch16a_demo(n=120, random_state=999)

    assert set(results.keys()) == {
        "df",
        "raw_table",
        "standardized_table",
        "partial_corr",
    }

    # Check that CSV outputs exist
    raw_path = tmp_path / "ch16a_regression_raw.csv"
    std_path = tmp_path / "ch16a_regression_standardized.csv"
    partial_path = tmp_path / "ch16a_partial_corr_exam_study.csv"

    for pth in (raw_path, std_path, partial_path):
        assert pth.exists()
        df_loaded = pd.read_csv(pth)
        assert not df_loaded.empty
