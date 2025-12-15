"""Tests for Track C Chapter 16 problem set (linear regression)."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch16_problem_set import (
    ProblemResult,
    exercise_1_strong_simple_regression,
    exercise_2_weak_noisy_regression,
    exercise_3_multiple_regression_incremental_r2,
    run_linear_regression,
)


def _check_basic_structure(result: ProblemResult, *, expected_cols: set[str]) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert set(result.data.columns) == expected_cols
    assert len(result.data) > 0

    assert isinstance(result.model_table, pd.DataFrame)
    assert set(result.model_table.columns) == {"term", "coef", "se", "t", "p"}

    # sanity checks on metrics
    assert 0.0 <= float(result.r2) <= 1.0


def test_run_linear_regression_table_shape() -> None:
    df = pd.DataFrame({"x": [0, 1, 2, 3], "y": [1, 3, 5, 7]})
    table, r2, sigma = run_linear_regression(df, y="y", x_cols=["x"])

    assert table.shape[0] == 2  # intercept + slope
    assert set(table["term"].tolist()) == {"Intercept", "x"}
    assert r2 > 0.95
    assert sigma >= 0.0


def test_exercise_1_strong_simple_regression() -> None:
    """Exercise 1 should have a clearly non-zero slope and decent R^2."""
    result = exercise_1_strong_simple_regression(random_state=123)
    _check_basic_structure(result, expected_cols={"x", "y"})

    slope_row = result.model_table[result.model_table["term"] == "x"].iloc[0]
    slope = float(slope_row["coef"])
    p_val = float(slope_row["p"])

    assert slope > 1.0
    assert p_val < 1e-6
    assert result.r2 > 0.35
    assert result.see is not None
    assert 0.5 < float(result.see) < 5.0


def test_exercise_2_weak_noisy_regression_low_r2() -> None:
    """Exercise 2 should have low explanatory power (small R^2)."""
    result = exercise_2_weak_noisy_regression(random_state=456)
    _check_basic_structure(result, expected_cols={"x", "y"})

    assert result.r2 < 0.10
    assert result.see is not None
    assert float(result.see) > 2.0  # noisy


def test_exercise_3_multiple_regression_incremental_r2() -> None:
    """Exercise 3: multiple regression should improve R^2 vs x1-only, and x2 should matter."""
    result = exercise_3_multiple_regression_incremental_r2(random_state=789)
    _check_basic_structure(result, expected_cols={"x1", "x2", "y"})

    assert "simple" in result.extra_tables
    assert "multiple" in result.extra_tables
    assert "r2_simple" in result.extra_metrics
    assert "r2_multiple" in result.extra_metrics
    assert "delta_r2" in result.extra_metrics

    r2_simple = float(result.extra_metrics["r2_simple"])
    r2_multiple = float(result.extra_metrics["r2_multiple"])
    delta = float(result.extra_metrics["delta_r2"])

    assert r2_multiple > r2_simple
    assert delta > 0.05

    # In the multiple model, x2 should usually be significant
    multiple_table = result.extra_tables["multiple"]
    x2_row = multiple_table[multiple_table["term"] == "x2"].iloc[0]
    assert float(x2_row["p"]) < 0.05
