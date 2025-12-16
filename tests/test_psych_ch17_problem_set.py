"""Tests for Track C Chapter 17 problem set (mixed-model / mixed ANOVA)."""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch17_problem_set import (
    ProblemResult,
    exercise_1_strong_interaction,
    exercise_2_time_only,
    exercise_3_group_only,
    run_mixed_anova,
)


def _check_basic_structure(result: ProblemResult) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert set(result.data.columns) == {"subject", "group", "time", "score"}
    assert result.data["subject"].nunique() > 0
    assert result.anova_table.shape[0] >= 3
    assert "Source" in result.anova_table.columns
    assert "p-unc" in result.anova_table.columns
    assert "np2" in result.anova_table.columns


def _p(table: pd.DataFrame, source: str) -> float:
    row = table.loc[table["Source"].astype(str).str.lower() == source.lower()].iloc[0]
    return float(row["p-unc"])


def test_exercise_1_detects_interaction() -> None:
    """Exercise 1 should show a strong group×time interaction."""
    result = exercise_1_strong_interaction(random_state=123)
    _check_basic_structure(result)

    table = run_mixed_anova(result.data)
    assert _p(table, "Interaction") < 0.001


def test_exercise_2_time_only() -> None:
    """Exercise 2 should show time main effect, with no group effect or interaction."""
    result = exercise_2_time_only(random_state=456)
    _check_basic_structure(result)

    table = run_mixed_anova(result.data)
    assert _p(table, "time") < 0.01
    assert _p(table, "group") > 0.10
    assert _p(table, "Interaction") > 0.10


def test_exercise_3_group_only() -> None:
    """Exercise 3 should show group main effect, with no time effect or interaction."""
    result = exercise_3_group_only(random_state=789)
    _check_basic_structure(result)

    table = run_mixed_anova(result.data)
    assert _p(table, "group") < 0.001
    assert _p(table, "time") > 0.10
    assert _p(table, "Interaction") > 0.10
