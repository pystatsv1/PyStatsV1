"""Tests for Track C Chapter 12 problem set (one-way ANOVA)."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch12_problem_set import (
    ProblemResult,
    exercise_1_moderate_effect,
    exercise_2_small_effect,
    exercise_3_unequal_n_strong_effect,
    run_one_way_anova,
)


def _check_basic_structure(result: ProblemResult) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert set(result.data.columns) == {"group", "score"}
    assert len(result.data) > 0
    assert result.anova_table.shape[0] == 1
    assert "p-unc" in result.anova_table.columns
    assert "eta2" in result.anova_table.columns


def test_exercise_1_detects_moderate_effect() -> None:
    """Exercise 1 should usually yield a significant omnibus F."""
    result = exercise_1_moderate_effect(random_state=123)
    _check_basic_structure(result)

    table = run_one_way_anova(result.data)
    row = table.iloc[0]
    p_val = float(row["p-unc"])
    eta2 = float(row["eta2"])

    assert p_val < 0.05
    assert eta2 > 0.05


def test_exercise_2_small_effect_often_non_significant() -> None:
    """Exercise 2 should have a smaller effect, often non-significant."""
    result = exercise_2_small_effect(random_state=456)
    _check_basic_structure(result)

    table = run_one_way_anova(result.data)
    row = table.iloc[0]
    eta2 = float(row["eta2"])

    # We allow borderline cases; just ensure the effect size is small.
    assert eta2 < 0.06
    assert 0.01 <= eta2 <= 0.06


def test_exercise_3_unequal_n_strong_effect() -> None:
    """Exercise 3 should show a clear, strong effect despite unequal n."""
    result = exercise_3_unequal_n_strong_effect(random_state=789)
    _check_basic_structure(result)

    table = run_one_way_anova(result.data)
    row = table.iloc[0]
    p_val = float(row["p-unc"])
    eta2 = float(row["eta2"])

    assert p_val < 0.01
    assert eta2 > 0.10
