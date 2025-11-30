"""Deterministic tests for Chapter 13 (two-way ANOVA, Track B)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.psych_ch13_two_way_anova import (
    compute_simple_main_effects_training_within_context,
    simulate_two_way_stress_study,
    two_way_anova,
)


def test_simulation_reproducible() -> None:
    """The two-way simulator should be deterministic given a fixed seed."""
    df1 = simulate_two_way_stress_study(
        n_per_cell=25,
        random_state=2025,
    )
    df2 = simulate_two_way_stress_study(
        n_per_cell=25,
        random_state=2025,
    )
    assert df1.equals(df2)

    df3 = simulate_two_way_stress_study(
        n_per_cell=25,
        random_state=2026,
    )
    assert not df1.equals(df3)


def test_two_way_anova_structure_and_identities() -> None:
    """Basic sanity checks for the two-way ANOVA decomposition."""
    df = simulate_two_way_stress_study(
        n_per_cell=25,
        random_state=2025,
    )
    result = two_way_anova(df)

    # Design: balanced 2x2 with n_per_cell participants per cell.
    assert result.n_per_cell == 25
    assert result.N == len(df)

    assert len(result.levels_A) == 2
    assert len(result.levels_B) == 2

    a = len(result.levels_A)
    b = len(result.levels_B)

    # Degrees of freedom
    assert result.df_A == a - 1
    assert result.df_B == b - 1
    assert result.df_AB == (a - 1) * (b - 1)
    assert result.df_total == result.N - 1
    assert result.df_within == result.N - a * b

    # Sum of squares identity (allow tiny numerical error)
    ss_sum = result.ss_A + result.ss_B + result.ss_AB + result.ss_within
    assert abs(result.ss_total - ss_sum) < 1e-6

    # Mean squares relationships
    assert np.isclose(result.ms_A, result.ss_A / result.df_A)
    assert np.isclose(result.ms_B, result.ss_B / result.df_B)
    assert np.isclose(result.ms_AB, result.ss_AB / result.df_AB)
    assert np.isclose(result.ms_within, result.ss_within / result.df_within)

    # F-statistic relationships
    assert np.isclose(result.F_A, result.ms_A / result.ms_within)
    assert np.isclose(result.F_B, result.ms_B / result.ms_within)
    assert np.isclose(result.F_AB, result.ms_AB / result.ms_within)

    # Effect sizes in a sensible range
    for eta in (result.eta2_A, result.eta2_B, result.eta2_AB):
        assert (0.0 <= eta <= 1.0) or np.isnan(eta)


def test_simple_main_effects_properties() -> None:
    """Simple main effects of Training within each Context should be sensible."""
    df = simulate_two_way_stress_study(
        n_per_cell=25,
        random_state=2025,
    )
    simple_effects = compute_simple_main_effects_training_within_context(df)

    # One result per context level.
    contexts = sorted(df["context"].unique().tolist())
    assert len(simple_effects) == len(contexts)

    seen_contexts = sorted(res.context for res in simple_effects)
    assert seen_contexts == contexts

    for res in simple_effects:
        assert res.n_control > 0
        assert res.n_cbt > 0

        # Sample size check within each context.
        n_in_context = len(df[df["context"] == res.context])
        assert res.n_control + res.n_cbt == n_in_context

        # t and p look like real test statistics.
        assert isinstance(res.t_stat, float)
        assert isinstance(res.p_value, float)
        assert 0.0 <= res.p_value <= 1.0

        # df for independent-samples t-test with equal variances.
        assert res.df == res.n_control + res.n_cbt - 2
