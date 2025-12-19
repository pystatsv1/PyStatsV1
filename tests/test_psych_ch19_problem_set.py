"""Tests for Track C Chapter 19 problem set (Non-Parametric Statistics)."""

from __future__ import annotations

import pandas as pd
from scipy.stats import chi2_contingency, chisquare, kruskal, mannwhitneyu

from scripts.psych_ch19_problem_set import (
    ProblemResult,
    exercise_1_chi_square_gof,
    exercise_2_chi_square_independence,
    exercise_3_mwu_and_kruskal,
)


def _check_basic_result(r: ProblemResult) -> None:
    assert isinstance(r.name, str)
    assert isinstance(r.data, pd.DataFrame)
    assert isinstance(r.summary, dict)
    assert len(r.data) > 0


def test_exercise_1_gof_significant() -> None:
    """Exercise 1 should show a clear GOF departure."""
    r = exercise_1_chi_square_gof(random_state=123)
    _check_basic_result(r)

    assert set(r.data.columns) == {"category", "observed", "expected"}
    chi2, p = chisquare(r.data["observed"].to_numpy(), r.data["expected"].to_numpy())
    assert p < 0.001
    assert float(r.summary["p_value"]) < 0.001


def test_exercise_2_independence_association() -> None:
    """Exercise 2 should show condition × outcome association (chi-square independence)."""
    r = exercise_2_chi_square_independence(random_state=456)
    _check_basic_result(r)

    assert set(r.data.columns) == {"subject", "condition", "outcome"}
    cont = pd.crosstab(r.data["condition"], r.data["outcome"])
    chi2, p, _, _ = chi2_contingency(cont.to_numpy(), correction=False)

    assert p < 0.001
    assert float(r.summary["p_value"]) < 0.001
    assert float(r.summary["cramers_v"]) > 0.20


def test_exercise_3_mwu_and_kruskal() -> None:
    """Exercise 3 should show A < B < C with significant MWU and Kruskal-Wallis."""
    r = exercise_3_mwu_and_kruskal(random_state=789)
    _check_basic_result(r)

    assert set(r.data.columns) == {"subject", "group", "score"}

    # MWU: A vs B
    ab = r.data[r.data["group"].isin(["A", "B"])]
    a = ab.loc[ab["group"] == "A", "score"].to_numpy()
    b = ab.loc[ab["group"] == "B", "score"].to_numpy()
    _, p_u = mannwhitneyu(a, b, alternative="two-sided")
    assert p_u < 0.01

    # Kruskal: A vs B vs C
    A = r.data.loc[r.data["group"] == "A", "score"].to_numpy()
    B = r.data.loc[r.data["group"] == "B", "score"].to_numpy()
    C = r.data.loc[r.data["group"] == "C", "score"].to_numpy()
    _, p_kw = kruskal(A, B, C)
    assert p_kw < 0.001

    # Median ordering sanity check
    meds = r.data.groupby("group", observed=True)["score"].median()
    assert float(meds["A"]) < float(meds["B"]) < float(meds["C"])
