"""Tests for Track C Chapter 14 problem set (repeated-measures ANOVA)."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch14_problem_set import (
    ProblemResult,
    exercise_1_clear_time_effect,
    exercise_2_no_time_effect,
    exercise_3_correlated_errors_sphericity_risk,
    run_repeated_measures_anova,
)


def _check_basic_structure(result: ProblemResult) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert set(result.data.columns) == {"subject", "time", "score"}
    assert len(result.data) > 0

    assert isinstance(result.anova_table, pd.DataFrame)
    assert result.anova_table.shape[0] == 1
    assert "p-unc" in result.anova_table.columns
    assert "np2" in result.anova_table.columns


def test_exercise_1_detects_clear_time_effect() -> None:
    """Exercise 1 should yield a strong, significant time effect."""
    result = exercise_1_clear_time_effect(random_state=123)
    _check_basic_structure(result)

    table = run_repeated_measures_anova(result.data)
    row = table.iloc[0]
    p_val = float(row["p-unc"])
    np2 = float(row["np2"])

    assert p_val < 0.001
    assert np2 > 0.20


def test_exercise_2_no_time_effect() -> None:
    """Exercise 2 should be non-significant with tiny effect size."""
    result = exercise_2_no_time_effect(random_state=456)
    _check_basic_structure(result)

    table = run_repeated_measures_anova(result.data)
    row = table.iloc[0]
    p_val = float(row["p-unc"])
    np2 = float(row["np2"])

    assert p_val > 0.20
    assert np2 < 0.05


def test_exercise_3_correlated_errors_still_detectable() -> None:
    """Exercise 3 should show a clear time effect; GG columns are optional."""
    result = exercise_3_correlated_errors_sphericity_risk(random_state=789)
    _check_basic_structure(result)

    table = run_repeated_measures_anova(result.data)
    row = table.iloc[0]
    p_val = float(row["p-unc"])
    np2 = float(row["np2"])

    assert p_val < 0.001
    assert np2 > 0.15

    # If pingouin is available in the environment, we may also have GG correction columns.
    if "p-GG-corr" in table.columns:
        assert float(row["p-GG-corr"]) < 0.05
    if "eps-GG" in table.columns:
        assert 0.0 < float(row["eps-GG"]) <= 1.0
