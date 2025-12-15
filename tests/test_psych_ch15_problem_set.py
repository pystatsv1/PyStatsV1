"""Tests for Track C Chapter 15 problem set (correlation)."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch15_problem_set import (
    ProblemResult,
    exercise_1_strong_positive,
    exercise_2_near_zero,
    exercise_3_third_variable_partial,
    pearson_corr,
    partial_corr,
)


def _check_basic_structure(result: ProblemResult) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert len(result.data) > 0


def test_exercise_1_strong_positive() -> None:
    """Exercise 1 should produce a clear strong positive Pearson r."""
    result = exercise_1_strong_positive(random_state=123)
    _check_basic_structure(result)

    pr = pearson_corr(result.data, "x", "y")
    assert pr.p < 1e-6
    assert pr.r > 0.70
    assert pr.ci95_lo > 0.60


def test_exercise_2_near_zero() -> None:
    """Exercise 2 should produce a small |r| and usually non-significant p."""
    result = exercise_2_near_zero(random_state=456)
    _check_basic_structure(result)

    pr = pearson_corr(result.data, "x", "y")
    assert abs(pr.r) < 0.15
    assert pr.p > 0.10


def test_exercise_3_partial_controls_spurious() -> None:
    """Exercise 3: raw x-y correlation high; partial correlation ~0 when controlling z."""
    result = exercise_3_third_variable_partial(random_state=789)
    _check_basic_structure(result)

    pr = pearson_corr(result.data, "x", "y")
    pc = partial_corr(result.data, "x", "y", controls=["z"])

    assert pr.r > 0.50
    assert pr.p < 1e-10

    assert abs(pc.r_partial) < 0.15
    assert pc.p > 0.10
