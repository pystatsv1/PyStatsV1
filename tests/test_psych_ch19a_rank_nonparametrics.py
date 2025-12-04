"""
Tests for Chapter 19a: rank-based non-parametric alternatives.

We check that:

1. Mann–Whitney detects a group shift and the median is higher
   in the treatment group.
2. Wilcoxon signed-rank detects a positive shift from pre to post.
3. Kruskal–Wallis detects differences among three ordered groups.
"""

from __future__ import annotations

import pandas as pd

from scripts.psych_ch19a_rank_nonparametrics import (
    run_kruskal,
    run_mannwhitney,
    run_wilcoxon,
    simulate_independent_groups_nonparametric,
    simulate_kruskal_nonparametric,
    simulate_paired_nonparametric,
)


def test_mannwhitney_detects_group_difference() -> None:
    """Mann–Whitney should detect a difference with the simulated effect."""
    df = simulate_independent_groups_nonparametric(
        n_per_group=50,
        effect_size=0.6,
        random_state=42,
    )
    results = run_mannwhitney(df)

    p_val = float(results.loc[0, "p-val"])
    median_control = df.loc[df["group"] == "control", "score"].median()
    median_treatment = df.loc[df["group"] == "treatment", "score"].median()

    assert p_val < 0.05
    assert median_treatment > median_control


def test_wilcoxon_detects_positive_shift() -> None:
    """Wilcoxon signed-rank should detect a positive pre-to-post shift."""
    df_long, df_wide = simulate_paired_nonparametric(
        n=50,
        effect_size=0.6,
        random_state=123,
    )
    # Silence "unused" warning: we mainly care that df_long is well-formed
    assert isinstance(df_long, pd.DataFrame)

    results = run_wilcoxon(df_wide)
    p_val = float(results.loc[0, "p-val"])

    median_pre = df_wide["pre"].median()
    median_post = df_wide["post"].median()

    assert p_val < 0.05
    assert median_post > median_pre


def test_kruskal_detects_group_ordering() -> None:
    """Kruskal–Wallis should detect ordered group differences."""
    df = simulate_kruskal_nonparametric(
        n_per_group=40,
        random_state=999,
    )
    results = run_kruskal(df)

    p_val = float(results.loc[0, "p-unc"])
    means = df.groupby("group")["score"].mean()

    # Expect low < medium < high on average
    assert p_val < 0.05
    assert means["low"] < means["medium"] < means["high"]
