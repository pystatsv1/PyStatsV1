"""Tests for Chapter 18 ANCOVA lab."""


from scripts.psych_ch18_ancova import (
    simulate_ancova_dataset,
    run_ancova,
    run_one_way_anova,
)


def test_simulated_dataset_has_two_groups() -> None:
    dataset = simulate_ancova_dataset(n_per_group=30, random_state=42)
    df = dataset.df

    groups = sorted(df["group"].unique())
    assert groups == ["control", "treatment"]
    assert df.shape[0] == 60
    assert {"pre_score", "post_score"}.issubset(df.columns)


def test_covariate_is_correlated_with_outcome() -> None:
    dataset = simulate_ancova_dataset(n_per_group=80, random_state=7)
    df = dataset.df

    r = df["pre_score"].corr(df["post_score"])
    assert r > 0.3  # reasonably strong positive correlation


def test_ancova_detects_treatment_effect() -> None:
    dataset = simulate_ancova_dataset(
        n_per_group=60,
        treatment_effect=5.0,
        random_state=123,
    )
    df = dataset.df

    aov_one_way = run_one_way_anova(df)
    aov_ancova = run_ancova(df)

    group_mask_one = aov_one_way["Source"] == "group"
    group_mask_anc = aov_ancova["Source"] == "group"

    p_one_way = float(aov_one_way.loc[group_mask_one, "p-unc"].iloc[0])
    p_ancova = float(aov_ancova.loc[group_mask_anc, "p-unc"].iloc[0])


    # ANCOVA should show a significant group effect
    assert p_ancova < 0.05

    # And usually provides at least as strong evidence as the one-way ANOVA
    assert p_ancova <= p_one_way + 1e-6
