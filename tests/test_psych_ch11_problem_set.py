"""Deterministic tests for Chapter 11 Track C problem set."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch11_problem_set import (
    ProblemResult,
    exercise_moderate_effect,
    exercise_small_effect,
    generate_ch11_problem_set,
)
from scripts.psych_ch11_paired_t import PairedTResult


def test_exercise_shapes_and_types() -> None:
    """Each exercise should return a ProblemResult with matching n."""
    res = exercise_moderate_effect(random_state=2025)

    assert isinstance(res, ProblemResult)
    assert isinstance(res.data, pd.DataFrame)
    assert isinstance(res.result, PairedTResult)

    cols = set(res.data.columns)
    # simulate_paired_training_study uses these column names
    assert {"score_pre", "score_post"} <= cols
    assert "diff" in cols

    # n from the result should match the number of rows in the DataFrame
    assert res.data.shape[0] == res.result.n


def test_generate_all_exercises() -> None:
    """generate_ch11_problem_set should return three named exercises."""
    results = generate_ch11_problem_set()
    assert len(results) == 3

    names = {res.name for res in results}
    assert {"moderate_effect", "small_effect", "no_effect"} <= names


def test_reproducibility() -> None:
    """Using the same seed should give identical data."""
    r1 = exercise_small_effect(random_state=123)
    r2 = exercise_small_effect(random_state=123)
    assert r1.data.equals(r2.data)
