"""
Deterministic tests for Chapter 10 independent-samples t-test helpers.

We check:
- basic structure of the generated synthetic data
- correctness of pooled-variance formulas vs. hand calculation
- pooled t-test + p-value against scipy.stats.ttest_ind (equal_var=True)
- Welch t-test + p-value against scipy.stats.ttest_ind_from_stats (equal_var=False)
- basic properties of the Welch df (should be < pooled df when variances differ)
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from scripts.psych_ch10_independent_t import (
    compute_pooled_sd,
    compute_pooled_t,
    compute_pooled_variance,
    compute_se_difference_from_pooled,
    compute_welch_df,
    compute_welch_standard_error,
    compute_welch_t,
    generate_independent_groups,
)


def test_generate_independent_groups_basic_shape() -> None:
    rng = np.random.default_rng(42)
    df = generate_independent_groups(rng, n_per_group=10)

    # 2 groups * 10 participants each
    assert df.shape[0] == 20
    assert set(df["condition"].unique()) == {"control", "treatment"}
    assert "stress_score" in df.columns

    # no missing values in stress_score
    assert df["stress_score"].isna().sum() == 0


def test_pooled_variance_matches_hand_calculation() -> None:
    sd1 = 10.0
    sd2 = 8.0
    n1 = 20
    n2 = 30

    # Hand calculation of pooled variance
    numer = (n1 - 1) * (sd1**2) + (n2 - 1) * (sd2**2)
    denom = n1 + n2 - 2
    expected_sp2 = numer / denom

    sp2 = compute_pooled_variance(sd1, sd2, n1, n2)
    assert np.isclose(sp2, expected_sp2)


def test_pooled_t_and_pvalue_match_scipy_equal_var() -> None:
    # Simple deterministic data
    x = np.array([10.0, 12.0, 9.0, 11.0, 13.0])
    y = np.array([8.0, 7.0, 9.0, 6.0, 10.0])

    mean1 = float(x.mean())
    mean2 = float(y.mean())
    sd1 = float(x.std(ddof=1))
    sd2 = float(y.std(ddof=1))
    n1 = x.size
    n2 = y.size

    # Our pooled t-test
    sp = compute_pooled_sd(sd1, sd2, n1, n2)
    se_diff = compute_se_difference_from_pooled(sp, n1, n2)
    t_pooled = compute_pooled_t(mean1, mean2, se_diff)
    df_pooled = n1 + n2 - 2
    p_pooled = 2.0 * stats.t.sf(abs(t_pooled), df=df_pooled)

    # SciPy's equal-variances t-test
    t_scipy, p_scipy = stats.ttest_ind(x, y, equal_var=True)

    assert np.isclose(t_pooled, t_scipy, atol=1e-12)
    assert np.isclose(p_pooled, p_scipy, atol=1e-12)


def test_welch_t_and_pvalue_match_scipy_from_stats() -> None:
    # Same deterministic data as above
    x = np.array([10.0, 12.0, 9.0, 11.0, 13.0])
    y = np.array([8.0, 7.0, 9.0, 6.0, 10.0])

    mean1 = float(x.mean())
    mean2 = float(y.mean())
    sd1 = float(x.std(ddof=1))
    sd2 = float(y.std(ddof=1))
    n1 = x.size
    n2 = y.size

    se_welch = compute_welch_standard_error(sd1, sd2, n1, n2)
    t_welch = compute_welch_t(mean1, mean2, se_welch)
    df_welch = compute_welch_df(sd1, sd2, n1, n2)
    p_welch = 2.0 * stats.t.sf(abs(t_welch), df=df_welch)

    # SciPy's Welch t-test from summary stats
    t_scipy, p_scipy = stats.ttest_ind_from_stats(
        mean1=mean1,
        std1=sd1,
        nobs1=n1,
        mean2=mean2,
        std2=sd2,
        nobs2=n2,
        equal_var=False,
    )

    assert np.isclose(t_welch, t_scipy, atol=1e-12)
    assert np.isclose(p_welch, p_scipy, atol=1e-12)


def test_welch_df_is_less_than_pooled_df_when_variances_differ() -> None:
    sd1 = 10.0
    sd2 = 20.0
    n1 = 15
    n2 = 40

    df_pooled = n1 + n2 - 2
    df_welch = compute_welch_df(sd1, sd2, n1, n2)

    # With unequal variances and unequal n, Welch df should be < pooled df
    assert df_welch < df_pooled
