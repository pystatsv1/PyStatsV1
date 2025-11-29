"""Deterministic tests for Chapter 11 (paired-samples t-test, Track B)."""

from __future__ import annotations


from scripts.psych_ch11_paired_t import (
    mis_specified_independent_t,
    paired_t_test_from_wide,
    simulate_paired_training_study,
)


def test_simulation_reproducible() -> None:
    """The simulator should be deterministic for a given seed."""
    df1 = simulate_paired_training_study(n=40, random_state=2025)
    df2 = simulate_paired_training_study(n=40, random_state=2025)
    assert df1.equals(df2)

    # Different seeds should produce different data (with overwhelming
    # probability); we only check that not *all* values match.
    df3 = simulate_paired_training_study(n=40, random_state=2026)
    assert not df1.equals(df3)


def test_simulation_basic_structure() -> None:
    """The simulated DataFrame should have the expected structure."""
    n = 40
    df = simulate_paired_training_study(n=n, random_state=2025)

    assert df.shape == (n, 4)
    assert list(df.columns) == ["participant_id", "score_pre", "score_post", "diff"]

    # Participant IDs should be 1..n, in order.
    assert df["participant_id"].iloc[0] == 1
    assert df["participant_id"].iloc[-1] == n

    # In expectation, post scores should be larger than pre on average.
    assert df["score_post"].mean() > df["score_pre"].mean()


def test_paired_t_known_values() -> None:
    """Regression test: paired t-test results for a fixed seed and n.

    This locks down the numerical results for (n=40, seed=2025) so that any
    future refactors must preserve the statistical calculations.
    """
    df = simulate_paired_training_study(n=40, random_state=2025)
    result = paired_t_test_from_wide(df)

    # Degrees of freedom and sample size
    assert result.n == 40
    assert result.df == 39

    # These values were obtained once via SciPy and are now treated as
    # regression targets. Tight tolerances ensure we notice accidental changes.
    assert abs(result.mean_diff - 5.43752870408188) < 1e-10
    assert abs(result.sd_diff - 9.167828757528428) < 1e-10
    assert abs(result.se_diff - 1.4495610036090687) < 1e-12
    assert abs(result.t_stat - 3.751155481241357) < 1e-12
    assert abs(result.p_value_two_sided - 0.000571764776521276) < 1e-15
    assert abs(result.ci_low - 2.5055148240424434) < 1e-12
    assert abs(result.ci_high - 8.369542584121318) < 1e-12

    # Cohen's d_z should be the mean difference in SD units of the differences.
    assert abs(result.dz - 0.5931097589073854) < 1e-12
    # And it should equal mean_diff / sd_diff numerically.
    assert abs(result.dz - (result.mean_diff / result.sd_diff)) < 1e-12


def test_paired_vs_independent_mis_specified() -> None:
    """The mis-specified independent t-test should be less powerful.

    For the same synthetic dataset, ignoring the pairing should produce a
    smaller absolute t-statistic than the correct paired analysis.
    """
    df = simulate_paired_training_study(n=40, random_state=2025)

    paired = paired_t_test_from_wide(df)
    indep = mis_specified_independent_t(df)

    # Mis-specified independent t must have smaller |t| than the paired t.
    assert abs(indep["t_stat"]) < abs(paired.t_stat)

    # Lock down the approximate independent t results as regression targets.
    assert abs(indep["t_stat"] - 2.0840888986502177) < 1e-12
    assert abs(indep["p_value_two_sided"] - 0.04042589862419336) < 1e-14
