"""
Tests for Chapter 17 mixed-model demo.

We mostly check that:
- the simulated dataset has the expected shape,
- pingouin.mixed_anova runs and returns the expected factors,
- the engineered Group × Time interaction is strong and in the right direction.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from scripts.psych_ch17_mixed_models import (
    MixedDesignData,
    compute_group_time_means,
    run_mixed_anova,
    simulate_mixed_design_dataset,
)


def test_simulation_shapes_and_levels() -> None:
    mixed: MixedDesignData = simulate_mixed_design_dataset(
        n_per_group=20,
        random_state=42,
    )
    wide, long = mixed.wide, mixed.long

    # 2 groups * 20 participants = 40 rows
    assert wide.shape[0] == 40
    # 3 time points per subject
    assert long.shape[0] == 40 * 3

    assert set(long["group"].unique()) == {"control", "treatment"}
    assert set(long["time"].unique()) == {"pre", "post", "followup"}

    # Wide format has the expected anxiety columns
    for col in ["anxiety_pre", "anxiety_post", "anxiety_followup"]:
        assert col in wide.columns


def test_mixed_anova_has_expected_effects() -> None:
    mixed = simulate_mixed_design_dataset(n_per_group=30, random_state=1)
    long_df = mixed.long

    aov = run_mixed_anova(long_df)

    # We expect rows for group, time, and the interaction (case-insensitive)
    effects_lower = {str(src).lower() for src in aov["Source"]}
    assert {"group", "time", "interaction"}.issubset(effects_lower)


    # Given the engineered means, the Group × Time interaction should be strong
    interaction_p = float(aov.loc[aov["Source"] == "Interaction", "p-unc"].iloc[0])
    assert interaction_p < 0.001


def test_treatment_improves_more_over_time() -> None:
    mixed = simulate_mixed_design_dataset(n_per_group=50, random_state=7)
    long_df = mixed.long
    means_df = compute_group_time_means(long_df)

    # Pivot for easier comparisons
    table = means_df.pivot(index="group", columns="time", values="mean_anxiety")

    # Control: small change; Treatment: large decrease from pre to post
    control_drop = table.loc["control", "pre"] - table.loc["control", "post"]
    treatment_drop = table.loc["treatment", "pre"] - table.loc["treatment", "post"]

    # Treatment drop should be meaningfully larger
    assert treatment_drop - control_drop > 8.0

    # Followup remains low for treatment relative to control
    assert table.loc["treatment", "followup"] + 5 < table.loc["control", "followup"]
