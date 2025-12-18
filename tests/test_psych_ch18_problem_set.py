"""Tests for Track C Chapter 18 problem set (ANCOVA)."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch18_problem_set import (
    ProblemResult,
    exercise_1_true_group_effect,
    exercise_2_spurious_raw_difference,
    exercise_3_slopes_violation,
    run_ancova,
    run_slopes_test,
)


def _p_ancova(table: pd.DataFrame, source: str) -> float:
    row = table.loc[table["Source"] == source].iloc[0]
    return float(row["p-unc"])


def _p_term(table: pd.DataFrame, term: str) -> float:
    row = table.loc[table["term"] == term].iloc[0]
    return float(row["PR(>F)"])


def _check_basic_structure(result: ProblemResult) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert set(result.data.columns) == {"subject", "group", "pretest", "posttest"}
    assert len(result.data) > 0
    assert "Source" in result.ancova_table.columns
    assert "p-unc" in result.ancova_table.columns
    assert set(result.adjusted_means.columns) == {"group", "pretest_at", "adjusted_mean"}


def test_exercise_1_true_group_effect() -> None:
    """Exercise 1 should show a clear adjusted group effect and a strong covariate effect."""
    result = exercise_1_true_group_effect(random_state=123)
    _check_basic_structure(result)

    anc = run_ancova(result.data)
    assert _p_ancova(anc, "group") < 0.01
    assert _p_ancova(anc, "pretest") < 0.001


def test_exercise_2_spurious_raw_difference_group_nonsig_in_ancova() -> None:
    """Exercise 2 should have pretest imbalance; ANCOVA group effect should be non-significant."""
    result = exercise_2_spurious_raw_difference(random_state=456)
    _check_basic_structure(result)

    # raw means differ (typically Treatment higher due to pretest shift)
    means = result.data.groupby("group", observed=True)["posttest"].mean()
    assert float(means["Treatment"] - means["Control"]) > 1.0

    anc = run_ancova(result.data)
    assert _p_ancova(anc, "group") > 0.10
    assert _p_ancova(anc, "pretest") < 0.001


def test_exercise_3_detects_slopes_violation() -> None:
    """Exercise 3 should show significant pretest×group interaction in the slopes test."""
    result = exercise_3_slopes_violation(random_state=789)
    _check_basic_structure(result)

    slopes = run_slopes_test(result.data)
    # statsmodels names the interaction as: pretest:C(group)
    assert _p_term(slopes, "pretest:C(group)") < 0.01
