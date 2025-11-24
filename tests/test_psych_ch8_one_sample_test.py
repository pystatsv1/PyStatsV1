"""Deterministic tests for Chapter 8 one-sample t-test helpers."""

from __future__ import annotations

import numpy as np

from scripts.psych_ch8_one_sample_test import (
    StressPopulation,
    compute_t_stat,
    estimate_two_sided_p,
    generate_stress_population,
    recenter_population,
    simulate_null_t_distribution,
)


def test_generate_stress_population_basic_properties() -> None:
    """Population should have the requested size and reasonable moments."""
    rng = np.random.default_rng(123)
    pop = generate_stress_population(n=10_000, rng=rng)

    assert isinstance(pop, StressPopulation)
    assert len(pop.scores) == 10_000
    # Rough checks: mean and SD in sensible ranges
    assert 15.0 < pop.mean < 25.0
    assert 5.0 < pop.sd < 15.0


def test_compute_t_stat_matches_manual_computation() -> None:
    """compute_t_stat should match the textbook formula."""
    sample = np.array([18.0, 20.0, 22.0, 24.0])
    mu0 = 20.0

    xbar = float(sample.mean())
    s = float(sample.std(ddof=1))
    expected_t = (xbar - mu0) / (s / np.sqrt(sample.size))

    t_val = compute_t_stat(sample, mu0=mu0)
    assert np.isclose(t_val, expected_t)


def test_recenter_population_sets_mean_close_to_mu0() -> None:
    """Recentering should shift the mean to the specified null value."""
    rng = np.random.default_rng(456)
    pop = generate_stress_population(n=5_000, rng=rng)
    mu0 = 25.0

    pop_h0 = recenter_population(pop, mu0=mu0)
    assert np.isclose(pop_h0.mean, mu0, atol=0.05)


def test_simulate_null_t_distribution_centered_at_zero() -> None:
    """Null t distribution should be roughly centered at zero."""
    rng = np.random.default_rng(789)
    pop = generate_stress_population(n=8_000, rng=rng)
    mu0 = 20.0
    pop_h0 = recenter_population(pop, mu0=mu0)

    t_null = simulate_null_t_distribution(
        pop_under_h0=pop_h0,
        n=25,
        mu0=mu0,
        n_sim=2_000,
        rng=rng,
    )

    assert t_null.shape == (2_000,)
    # Mean close to 0 under H0
    assert abs(t_null.mean()) < 0.1
    # Non-degenerate spread
    assert 0.5 < t_null.std(ddof=1) < 2.5


def test_estimate_two_sided_p_monotone_in_t_obs() -> None:
    """Larger |t_obs| should lead to smaller estimated p-values."""
    rng = np.random.default_rng(1010)
    pop = generate_stress_population(n=8_000, rng=rng)
    mu0 = 20.0
    pop_h0 = recenter_population(pop, mu0=mu0)

    t_null = simulate_null_t_distribution(
        pop_under_h0=pop_h0,
        n=25,
        mu0=mu0,
        n_sim=3_000,
        rng=rng,
    )

    p_small = estimate_two_sided_p(t_obs=0.5, t_null=t_null)
    p_medium = estimate_two_sided_p(t_obs=1.5, t_null=t_null)
    p_large = estimate_two_sided_p(t_obs=3.0, t_null=t_null)

    # As |t_obs| increases, p-values should decrease
    assert p_small >= p_medium >= p_large
