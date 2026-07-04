"""Tests for Track C Chapter 20 problem set (responsible researcher capstone)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.psych_ch20_problem_set import (
    ProblemResult,
    exercise_1_power_analysis,
    exercise_2_meta_analysis,
    exercise_3_optional_stopping,
    power_ttest_ind,
    required_n_ttest,
)


def _check_basic_structure(result: ProblemResult) -> None:
    assert isinstance(result.data, pd.DataFrame)
    assert isinstance(result.summary_table, pd.DataFrame)
    assert len(result.summary_table) >= 1


def test_exercise_1_power_analysis_reasonable_n() -> None:
    """Exercise 1 should yield a reasonable n for d=0.5, power=0.8."""
    result = exercise_1_power_analysis(random_state=123)
    _check_basic_structure(result)

    row = result.summary_table.iloc[0]
    n_req = int(row["n_required_per_group"])
    achieved = float(row["achieved_power_at_n"])

    # Classic ballpark: ~64 per group for d=0.5 @ 80% power (two-sided alpha=.05)
    assert 55 <= n_req <= 75
    assert achieved >= 0.80

    # Cross-check helper functions directly
    n_req2 = required_n_ttest(0.5, target_power=0.80, alpha=0.05, two_sided=True)
    assert n_req2 == n_req == 64
    assert power_ttest_ind(0.5, n_req2, alpha=0.05, two_sided=True) >= 0.80


def test_power_helper_stays_finite_at_large_sample_sizes() -> None:
    """The tiny opposite tail must not turn a stable power result into NaN."""
    power = power_ttest_ind(0.5, 1000, alpha=0.05, two_sided=True)
    assert np.isfinite(power)
    assert 0.999 < power <= 1.0


def test_two_sided_power_is_symmetric_in_effect_direction() -> None:
    positive = power_ttest_ind(0.5, 64, alpha=0.05, two_sided=True)
    negative = power_ttest_ind(-0.5, 64, alpha=0.05, two_sided=True)
    assert positive == pytest.approx(negative, rel=0.0, abs=1e-12)


def test_required_n_rejects_an_unreachable_target_within_n_max() -> None:
    with pytest.raises(ValueError, match="cannot be reached within n_max=20"):
        required_n_ttest(0.1, target_power=0.99, alpha=0.05, two_sided=True, n_max=20)


def test_exercise_2_meta_analysis_has_heterogeneity() -> None:
    """Exercise 2 should show meaningful heterogeneity and a positive pooled effect."""
    result = exercise_2_meta_analysis(random_state=456)
    _check_basic_structure(result)

    summary = result.summary_table.set_index("model")
    fixed = summary.loc["fixed"]
    rand = summary.loc["random"]

    assert float(fixed["est"]) > 0.15
    assert float(fixed["I2"]) > 0.30  # heterogeneity present

    # Random-effects should estimate some tau^2 (often > 0)
    assert float(rand["tau2"]) >= 0.0
    assert float(rand["I2"]) == float(fixed["I2"])


def test_exercise_3_optional_stopping_inflates_type1() -> None:
    """Optional stopping should inflate false positives above alpha=0.05."""
    result = exercise_3_optional_stopping(random_state=789)
    _check_basic_structure(result)

    row = result.summary_table.iloc[0]
    fpr = float(row["false_positive_rate"])

    # With 5 looks (20,30,40,50,60), false positive rate should be well above 0.05.
    assert 0.10 <= fpr <= 0.20
