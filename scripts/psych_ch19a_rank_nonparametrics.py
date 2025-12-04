"""
Chapter 19a lab: rank-based non-parametric alternatives.

This script demonstrates three classic rank-based tests:

1. Mann–Whitney U (alternative to independent-samples t)
2. Wilcoxon signed-rank (alternative to paired-samples t)
3. Kruskal–Wallis (alternative to one-way ANOVA)

It simulates skewed, non-normal data for each design,
runs the appropriate Pingouin test, prints a short summary,
and saves both the datasets and results to disk along with
a small figure of group boxplots.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg

# Base directories
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"
OUTPUTS_DIR = BASE_DIR / "outputs" / "track_b"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------


def simulate_independent_groups_nonparametric(
    n_per_group: int = 40,
    effect_size: float = 0.6,
    random_state: int | None = None,
) -> pd.DataFrame:
    """Simulate skewed independent-group data for a Mann–Whitney demo.

    The control and treatment groups are drawn from the same skewed base
    distribution (chi-square), but the treatment group is shifted upward
    by an amount proportional to ``effect_size``.

    The goal is:
    - non-normal (skewed) data, appropriate for rank tests
    - a clear median difference when ``effect_size`` is moderately large
    - deterministic behaviour given ``random_state``
    """
    rng = np.random.default_rng(random_state)

    # Skewed base distribution (positive-only, right-skewed)
    control_scores = rng.chisquare(df=3, size=n_per_group) * 10.0

    # Same shape, but with a stronger location shift so that tests with
    # effect_size=0.6 and n_per_group=50 reliably detect a difference.
    shift = effect_size * 20.0
    treatment_scores = rng.chisquare(df=3, size=n_per_group) * 10.0 + shift

    df = pd.DataFrame(
        {
            "group": (["control"] * n_per_group) + (["treatment"] * n_per_group),
            "score": np.concatenate([control_scores, treatment_scores]),
        }
    )
    return df



def simulate_paired_nonparametric(
    n: int = 40,
    effect_size: float = 0.6,
    random_state: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate skewed paired data for a Wilcoxon signed-rank demo.

    We generate a skewed baseline (pre) and then add a positive shift
    plus noise to obtain post scores. This yields:

    - non-normal, skewed marginal distributions
    - a clear positive pre→post shift when ``effect_size`` is moderately large
    - deterministic behaviour under ``random_state``
    """
    rng = np.random.default_rng(random_state)

    # Skewed baseline (e.g., reaction time, symptom severity)
    pre = rng.lognormal(mean=3.0, sigma=0.6, size=n) * 10.0

    # Positive improvement: constant shift plus noise
    # Making the shift reasonably large ensures that tests with
    # n=50 and effect_size=0.6 see a reliable positive effect.
    improvement = effect_size * 8.0 + rng.normal(loc=0.0, scale=5.0, size=n)
    post = pre + improvement

    df_wide = pd.DataFrame({"pre": pre, "post": post})
    df_long = df_wide.reset_index(names="subject").melt(
        id_vars="subject",
        value_vars=["pre", "post"],
        var_name="condition",
        value_name="score",
    )

    return df_long, df_wide



def simulate_kruskal_nonparametric(
    n_per_group: int = 30,
    random_state: int | None = 789,
) -> pd.DataFrame:
    """Simulate skewed 3-group data for a Kruskal–Wallis example.

    Parameters
    ----------
    n_per_group :
        Number of observations per group.
    random_state :
        Seed for reproducibility.

    Returns
    -------
    DataFrame with columns: 'group' ('low', 'medium', 'high') and 'score'.
    """
    rng = np.random.default_rng(random_state)

    low = rng.lognormal(mean=3.5, sigma=0.6, size=n_per_group)
    medium = rng.lognormal(mean=3.8, sigma=0.6, size=n_per_group)
    high = rng.lognormal(mean=4.1, sigma=0.6, size=n_per_group)

    df = pd.DataFrame(
        {
            "group": (
                ["low"] * n_per_group
                + ["medium"] * n_per_group
                + ["high"] * n_per_group
            ),
            "score": np.concatenate([low, medium, high]),
        }
    )
    return df


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------


def run_mannwhitney(df: pd.DataFrame) -> pd.DataFrame:
    """Run a Mann–Whitney U test on the simulated independent-groups data."""
    x = df.loc[df["group"] == "control", "score"]
    y = df.loc[df["group"] == "treatment", "score"]

    results = pg.mwu(x, y, alternative="two-sided")
    # Reset index so callers can safely use .loc[0]
    return results.reset_index(drop=True)


def run_wilcoxon(df_wide: pd.DataFrame) -> pd.DataFrame:
    """Run a Wilcoxon signed-rank test on the paired data."""
    results = pg.wilcoxon(df_wide["pre"], df_wide["post"], alternative="two-sided")
    return results.reset_index(drop=True)


def run_kruskal(df: pd.DataFrame) -> pd.DataFrame:
    """Run a Kruskal–Wallis test on the 3-group data."""
    results = pg.kruskal(dv="score", between="group", data=df)
    return results.reset_index(drop=True)


def plot_group_boxplots(
    df_mw: pd.DataFrame,
    df_kruskal: pd.DataFrame,
    output_path: Path,
) -> None:
    """Create side-by-side boxplots for the Mann–Whitney and Kruskal demos."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    df_mw.boxplot(by="group", column="score", ax=axes[0])
    axes[0].set_title("Mann–Whitney example")
    axes[0].set_xlabel("Group")
    axes[0].set_ylabel("Score")

    df_kruskal.boxplot(by="group", column="score", ax=axes[1])
    axes[1].set_title("Kruskal–Wallis example")
    axes[1].set_xlabel("Group")
    axes[1].set_ylabel("Score")

    fig.suptitle("Rank-based non-parametric examples")
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the full Chapter 19a rank-based non-parametric demo."""
    print("Simulating rank-based non-parametric examples for Chapter 19a...\n")

    # 1. Mann–Whitney U (independent groups)
    df_mw = simulate_independent_groups_nonparametric()
    print("Mann–Whitney U example (independent groups)")
    print("-------------------------------------------")
    print("First 6 rows:")
    print(df_mw.head(), "\n")

    mw_results = run_mannwhitney(df_mw)
    print("Mann–Whitney U results:")
    print(mw_results, "\n")

    mw_data_path = DATA_DIR / "psych_ch19a_mannwhitney_demo.csv"
    mw_results_path = OUTPUTS_DIR / "ch19a_mannwhitney_results.csv"
    df_mw.to_csv(mw_data_path, index=False)
    mw_results.to_csv(mw_results_path, index=False)

    # 2. Wilcoxon signed-rank (paired data)
    df_long, df_wide = simulate_paired_nonparametric()
    print("Wilcoxon signed-rank example (paired data)")
    print("-----------------------------------------")
    print("First 6 rows (long format):")
    print(df_long.head(), "\n")

    wilcoxon_results = run_wilcoxon(df_wide)
    print("Wilcoxon signed-rank results:")
    print(wilcoxon_results, "\n")

    wilcoxon_data_path = DATA_DIR / "psych_ch19a_wilcoxon_demo.csv"
    wilcoxon_results_path = OUTPUTS_DIR / "ch19a_wilcoxon_results.csv"
    df_wide.to_csv(wilcoxon_data_path, index=False)
    wilcoxon_results.to_csv(wilcoxon_results_path, index=False)

    # 3. Kruskal–Wallis (3-group design)
    df_kw = simulate_kruskal_nonparametric()
    print("Kruskal–Wallis example (3 groups)")
    print("---------------------------------")
    print("First 6 rows:")
    print(df_kw.head(), "\n")

    kw_results = run_kruskal(df_kw)
    print("Kruskal–Wallis results:")
    print(kw_results, "\n")

    kw_data_path = DATA_DIR / "psych_ch19a_kruskal_demo.csv"
    kw_results_path = OUTPUTS_DIR / "ch19a_kruskal_results.csv"
    df_kw.to_csv(kw_data_path, index=False)
    kw_results.to_csv(kw_results_path, index=False)

    # 4. Boxplot figure
    fig_path = OUTPUTS_DIR / "ch19a_rank_nonparam_boxplots.png"
    plot_group_boxplots(df_mw, df_kw, fig_path)

    print(f"Mann–Whitney data saved to: {mw_data_path}")
    print(f"Mann–Whitney results saved to: {mw_results_path}")
    print(f"Wilcoxon data (wide) saved to: {wilcoxon_data_path}")
    print(f"Wilcoxon results saved to: {wilcoxon_results_path}")
    print(f"Kruskal–Wallis data saved to: {kw_data_path}")
    print(f"Kruskal–Wallis results saved to: {kw_results_path}")
    print(f"Boxplot figure saved to: {fig_path}\n")
    print("Chapter 19a rank-based non-parametric lab complete.")


if __name__ == "__main__":
    main()
