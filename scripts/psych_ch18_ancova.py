"""Chapter 18 lab: One-way ANCOVA with a pre-test covariate.

This script simulates a simple psychology experiment with a control and
treatment group, a pre-test covariate, and a post-test outcome. It then
compares an ordinary one-way ANOVA on the post-test to an ANCOVA that
controls for the pre-test using pingouin.ancova.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg


DATA_DIR = Path("data") / "synthetic"
OUT_DIR = Path("outputs") / "track_b"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AncovaDataset:
    df: pd.DataFrame


def simulate_ancova_dataset(
    n_per_group: int = 40,
    pre_mean: float = 50.0,
    pre_sd: float = 10.0,
    slope_pre: float = 0.6,
    treatment_effect: float = 5.0,
    noise_sd: float = 8.0,
    random_state: int | None = 123,
) -> AncovaDataset:
    """Simulate a simple ANCOVA dataset with a pre-test covariate."""
    rng = np.random.default_rng(random_state)

    groups = np.repeat(["control", "treatment"], n_per_group)
    n = groups.size

    pre = rng.normal(loc=pre_mean, scale=pre_sd, size=n)

    group_effect = np.where(groups == "treatment", treatment_effect, 0.0)
    noise = rng.normal(loc=0.0, scale=noise_sd, size=n)

    post = 30.0 + slope_pre * pre + group_effect + noise

    df = pd.DataFrame(
        {
            "group": groups,
            "pre_score": pre,
            "post_score": post,
        }
    )

    return AncovaDataset(df=df)


def run_one_way_anova(df: pd.DataFrame) -> pd.DataFrame:
    """Run a simple one-way ANOVA on post_score ~ group."""
    aov = pg.anova(dv="post_score", between="group", data=df, detailed=True)
    return aov


def run_ancova(df: pd.DataFrame) -> pd.DataFrame:
    """Run ANCOVA: post_score ~ group + pre_score."""
    aov = pg.ancova(
        dv="post_score",
        covar="pre_score",
        between="group",
        data=df,
    )
    return aov


def compute_adjusted_means(df: pd.DataFrame) -> pd.DataFrame:
    """Compute adjusted post-test means at the grand mean of pre_score.

    We fit a linear model: post_score ~ pre_score + group (dummy-coded),
    then use the fitted coefficients to predict each group's mean at the
    overall mean of the covariate.

    This mirrors the ANCOVA model used above but uses a simple NumPy
    least-squares fit instead of pingouin.linear_regression, which
    can be fussy about mixed dtypes.
    """
    # Grand mean of the covariate
    grand_mean_pre = float(df["pre_score"].mean())

    # Dummy-code group: 0 = control, 1 = treatment
    group_dummy = (df["group"] == "treatment").astype(float)

    # Design matrix: [Intercept, pre_score, group_dummy]
    X = np.column_stack(
        [
            np.ones(len(df), dtype=float),
            df["pre_score"].to_numpy(dtype=float),
            group_dummy.to_numpy(dtype=float),
        ]
    )
    y = df["post_score"].to_numpy(dtype=float)

    # Ordinary least squares: beta = (X'X)^(-1) X'y
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    intercept, beta_pre, beta_group = map(float, beta)

    # Predicted means at grand_mean_pre for each group
    control_mean = intercept + beta_pre * grand_mean_pre          # group_dummy = 0
    treatment_mean = control_mean + beta_group                    # group_dummy = 1

    adjusted = pd.DataFrame(
        {
            "group": ["control", "treatment"],
            "adjusted_post": [control_mean, treatment_mean],
        }
    )

    return adjusted




def plot_adjusted_means(
    raw_means: pd.DataFrame,
    adjusted_means: pd.DataFrame,
    out_path: Path,
) -> None:
    """Plot raw vs adjusted group means for the post-test score."""
    groups = raw_means["group"]
    x = np.arange(groups.size)

    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.bar(
        x - width / 2,
        raw_means["raw_mean"],
        width=width,
        label="Raw means",
    )
    ax.bar(
        x + width / 2,
        adjusted_means["adjusted_post"],
        width=width,
        label="Adjusted means",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Post-test score")
    ax.set_title("Chapter 18 ANCOVA: Raw vs Adjusted Means")
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    print("Simulating ANCOVA dataset for Chapter 18...\n")

    dataset = simulate_ancova_dataset()
    df = dataset.df

    print("First 6 rows:")
    print(df.head(), "\n")

    print("One-way ANOVA on post_score ~ group")
    aov_one_way = run_one_way_anova(df)
    print(aov_one_way, "\n")

    print("ANCOVA on post_score ~ group + pre_score")
    aov_ancova = run_ancova(df)
    print(aov_ancova, "\n")

    # Raw and adjusted means
    raw_means = (
        df.groupby("group", as_index=False)["post_score"]
        .mean()
        .rename(columns={"post_score": "raw_mean"})
    )
    adjusted_means = compute_adjusted_means(df)

    print("Raw means:")
    print(raw_means, "\n")
    print("Adjusted means (at mean pre_score):")
    print(adjusted_means, "\n")

    data_path = DATA_DIR / "psych_ch18_ancova.csv"
    table_path = OUT_DIR / "ch18_ancova_table.csv"
    fig_path = OUT_DIR / "ch18_ancova_adjusted_means.png"

    df.to_csv(data_path, index=False)
    aov_ancova.to_csv(table_path, index=False)

    plot_adjusted_means(raw_means, adjusted_means, fig_path)

    print(f"Data saved to: {data_path}")
    print(f"ANCOVA table saved to: {table_path}")
    print(f"Adjusted means figure saved to: {fig_path}")
    print("\nChapter 18 ANCOVA lab complete.")


if __name__ == "__main__":
    main()
