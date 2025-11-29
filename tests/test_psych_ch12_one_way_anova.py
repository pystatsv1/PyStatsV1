"""Deterministic tests for Chapter 12 (one-way ANOVA, Track B)."""

from __future__ import annotations

from scipy import stats

from scripts.psych_ch12_one_way_anova import (
    bonferroni_pairwise_t,
    one_way_anova,
    simulate_one_way_stress_study,
)


def test_simulation_reproducible() -> None:
    """The one-way simulator should be deterministic given a fixed seed."""
    df1 = simulate_one_way_stress_study(
        n_per_group=30,
        random_state=2025,
    )
    df2 = simulate_one_way_stress_study(
        n_per_group=30,
        random_state=2025,
    )
    assert df1.equals(df2)

    df3 = simulate_one_way_stress_study(
        n_per_group=30,
        random_state=2026,
    )
    assert not df1.equals(df3)


def test_anova_known_values() -> None:
    """Regression test: one-way ANOVA for a fixed seed and n_per_group.

    This locks down the ANOVA calculations so future refactors cannot change
    the statistics silently.
    """
    df = simulate_one_way_stress_study(
        n_per_group=30,
        random_state=2025,
    )
    result = one_way_anova(df)

    # Design: 3 groups of 30 participants each.
    assert result.k == 3
    assert result.N == 90
    assert result.df_between == 2
    assert result.df_within == 87
    assert result.df_total == 89

    # Sums of Squares (regression targets for seed 2025)
    assert abs(result.ss_between - 132.5888203569578) < 1e-9
    assert abs(result.ss_within - 6750.4923824362995) < 1e-9
    assert abs(result.ss_total - 6883.081202793257) < 1e-9

    # Mean Squares
    assert abs(result.ms_between - 66.2944101784789) < 1e-9
    assert abs(result.ms_within - 77.59186646478506) < 1e-9

    # F, p, and effect size
    assert abs(result.F - 0.8543989621459424) < 1e-12
    assert abs(result.p_value - 0.4290780410952785) < 1e-15
    assert abs(result.eta_sq - 0.019263003944098647) < 1e-12

    # Cross-check against SciPy's f_oneway.
    # Group order from groupby() is deterministic for our simulated data.
    grouped = [grp["stress_score"].to_numpy() for _, grp in df.groupby("group")]
    scipy_F, scipy_p = stats.f_oneway(*grouped)

    assert abs(result.F - scipy_F) < 1e-10
    assert abs(result.p_value - scipy_p) < 1e-12


def test_pairwise_bonferroni_properties() -> None:
    """Pairwise Bonferroni tests should have sensible properties."""
    df = simulate_one_way_stress_study(
        n_per_group=30,
        random_state=2025,
    )
    pairwise = bonferroni_pairwise_t(df)

    # We have 3 groups, so 3 pairwise comparisons.
    assert len(pairwise) == 3

    # Every comparison should have Bonferroni p >= uncorrected p.
    for res in pairwise:
        assert res.p_bonferroni >= res.p_uncorrected
        assert 0.0 <= res.p_uncorrected <= 1.0
        assert 0.0 <= res.p_bonferroni <= 1.0

    # Lock down one of the comparisons as a regression target.
    # Sort by (group1, group2) to make the ordering deterministic.
    pairwise_sorted = sorted(
        pairwise,
        key=lambda r: (r.group1, r.group2),
    )
    first = pairwise_sorted[0]

    assert (first.group1, first.group2) == ("cbt", "control")
    assert first.df == 58
    assert abs(first.t_stat - -1.1116162691262785) < 1e-12
    assert abs(first.p_uncorrected - 0.2708898839448614) < 1e-14
    # There are 3 comparisons, so Bonferroni multiplies p by 3.
    assert abs(first.p_bonferroni - 0.8126696518345842) < 1e-14
