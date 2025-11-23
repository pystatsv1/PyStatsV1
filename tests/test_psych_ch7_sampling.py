# SPDX-License-Identifier: MIT
"""Tests for Chapter 7 sampling-distribution helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.sim_psych_ch7_sampling import (
    DEFAULT_SAMPLE_N,
    draw_sample_means,
    generate_population,
)


def test_generate_population_shape_and_nonnegative():
    """Population generator should return a 1-column, non-negative Series."""
    n = 1_000
    df = generate_population(n=n, seed=123)
    assert df.shape == (n, 1)
    assert "stress_score" in df.columns
    # Gamma-based stress scores should be non-negative
    assert (df["stress_score"] >= 0).all()


def test_sample_means_length_and_center():
    """Sample means should have correct length and be centered near the population mean."""
    pop_df = generate_population(n=5_000, seed=123)
    population = pop_df["stress_score"]

    reps = 400
    sample_means = draw_sample_means(
        population=population,
        n=DEFAULT_SAMPLE_N,
        reps=reps,
        seed=999,
    )

    assert len(sample_means) == reps

    pop_mean = population.mean()
    means_mean = sample_means.mean()

    # With a few hundred reps, the mean of the sample means should be
    # reasonably close to the population mean.
    assert abs(means_mean - pop_mean) < 0.5


def test_sample_means_standard_error_reasonable():
    """Empirical SD of sample means should be close to theoretical SE."""
    pop_df = generate_population(n=5_000, seed=321)
    population = pop_df["stress_score"]

    n = DEFAULT_SAMPLE_N
    reps = 500
    sample_means = draw_sample_means(
        population=population,
        n=n,
        reps=reps,
        seed=2024,
    )

    pop_sd = population.std(ddof=1)
    theoretical_se = pop_sd / np.sqrt(n)
    empirical_se = sample_means.std(ddof=1)

    # Allow a fairly generous tolerance; this is a stochastic check, not an equality.
    assert empirical_se > 0
    assert theoretical_se > 0
    assert abs(empirical_se - theoretical_se) / theoretical_se < 0.35
