"""Tests for Chapter 16b Pingouin regression diagnostics (including Anscombe)."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from scripts.psych_ch16b_pingouin_regression_diagnostics import (
    compute_regression_diagnostics,
    make_anscombe_quartet,
    run_ch16b_demo,
    simulate_regression_dataset,
    summarize_anscombe,
)


def test_regression_diagnostics_basic_properties() -> None:
    """Diagnostics should have expected columns and leverage properties."""
    df = simulate_regression_dataset(n=120, random_state=42)
    predictors = ["study_hours", "sleep_hours", "stress", "motivation"]
    outcome = "exam_score"

    diagnostics, summary = compute_regression_diagnostics(
        df=df,
        predictors=predictors,
        outcome=outcome,
    )

    # Shape and required columns
    assert len(diagnostics) == len(df)
    for col in ["fitted", "residual", "std_residual", "leverage", "cooks_distance"]:
        assert col in diagnostics.columns

    # Average leverage should be approximately p / n
    # where p = number of parameters (intercept + predictors)
    n = len(df)
    p = len(predictors) + 1
    avg_leverage = diagnostics["leverage"].mean()
    expected = p / n
    assert math.isclose(avg_leverage, expected, rel_tol=0.1)

    # R^2 should be in a reasonable range (not degenerate)
    r2_values = summary.loc[1:, "r2"].to_numpy()
    assert np.all(r2_values > 0.3)
    assert np.all(r2_values < 0.99)


def test_run_ch16b_demo_creates_outputs(tmp_path: Path, monkeypatch) -> None:
    """End-to-end demo should create diagnostics, plots, and Anscombe outputs."""
    # Redirect data and outputs into a temporary directory
    monkeypatch.chdir(tmp_path)

    # Basic run
    run_ch16b_demo(n=80, random_state=7)

    output_dir = Path("outputs") / "track_b"
    assert output_dir.exists()

    expected_files = [
        "ch16b_regression_diagnostics.csv",
        "ch16b_influential_points.csv",
        "ch16b_residuals_vs_fitted.png",
        "ch16b_leverage_vs_cooks.png",
        "ch16b_anscombe_summary.csv",
        "ch16b_anscombe_quartet.png",
    ]

    for name in expected_files:
        path = output_dir / name
        assert path.exists(), f"Missing expected output: {path}"
        assert path.stat().st_size > 0, f"Empty output file: {path}"


def test_anscombe_quartet_statistics_nearly_identical() -> None:
    """Anscombe datasets should have nearly identical summary statistics."""
    df = make_anscombe_quartet()
    summary = summarize_anscombe(df)

    # We expect 4 datasets: I, II, III, IV
    assert summary["dataset"].tolist() == ["I", "II", "III", "IV"]
    assert (summary["n"] == 11).all()

    # Check max differences across datasets for key stats.
    for col, tol in [
        ("mean_x", 0.05),
        ("mean_y", 0.05),
        ("var_x", 0.2),
        ("var_y", 0.3),
        ("r", 0.02),
        ("slope", 0.05),
        ("intercept", 0.2),
    ]:
        values = summary[col].to_numpy()
        assert values.max() - values.min() < tol, f"{col} varies too much"
