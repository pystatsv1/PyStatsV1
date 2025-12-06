"""
Track C – Chapter 12 problem set (one-way ANOVA).

This script provides three synthetic exercises that mirror common
one-way ANOVA scenarios:

1. A moderate treatment effect with equal group sizes.
2. A small treatment effect with equal group sizes.
3. A strong treatment effect with unequal group sizes.

Each exercise returns a ProblemSetResult that bundles the raw
data and a compact ANOVA summary table. The tests call the
exercise functions directly and also call `run_one_way_anova`
on the returned data.

Students can reuse or adapt the code here to analyse their
own one-way ANOVA designs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Paths and small utilities
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
TRACK_C_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "track_c"


def _ensure_dirs() -> None:
    """Make sure output directories exist."""
    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRACK_C_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Dataclass used by the tests
# ---------------------------------------------------------------------------


@dataclass
class ProblemResult:
    """Container for a Chapter 12 problem-set exercise."""
    name: str
    data: pd.DataFrame
    anova_table: pd.DataFrame


# Backwards-compatible alias (if we ever referenced ProblemSetResult elsewhere)
ProblemSetResult = ProblemResult


# ---------------------------------------------------------------------------
# Core ANOVA helper
# ---------------------------------------------------------------------------


def run_one_way_anova(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run a classic one-way ANOVA on long-format data.

    Parameters
    ----------
    df :
        DataFrame with columns:
        - 'group': group/condition label
        - 'score': numeric outcome

    Returns
    -------
    summary :
        Single-row DataFrame with columns:
        - 'Source'  : always 'group'
        - 'ddof1'   : between-groups df
        - 'ddof2'   : within-groups df
        - 'F'       : F statistic
        - 'p-unc'   : p-value (upper-tail)
        - 'eta2'    : eta-squared (SS_between / SS_total)
    """
    if not {"group", "score"}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'group' and 'score' columns.")

    grouped = df.groupby("group")["score"]
    n_i = grouped.size()
    means = grouped.mean()
    overall_mean = df["score"].mean()

    # Between-groups SS
    ss_between = (n_i * (means - overall_mean) ** 2).sum()

    # Within-groups SS (residual)
    ss_within = grouped.apply(lambda s: ((s - s.mean()) ** 2).sum()).sum()

    df_between = len(n_i) - 1
    df_within = len(df) - len(n_i)

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    F_val = ms_between / ms_within

    p_val = stats.f.sf(F_val, df_between, df_within)
    eta2 = float(ss_between / (ss_between + ss_within))

    summary = pd.DataFrame(
        {
            "Source": ["group"],
            "ddof1": [int(df_between)],
            "ddof2": [int(df_within)],
            "F": [float(F_val)],
            "p-unc": [float(p_val)],
            "eta2": [eta2],
        }
    )
    return summary


# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------


def _simulate_equal_n(
    means: Mapping[str, float],
    n_per_group: int,
    sd: float,
    random_state: Optional[int] = None,
) -> pd.DataFrame:
    """Simulate one-way ANOVA data with equal group sizes."""
    rng = np.random.default_rng(random_state)
    rows = []
    for group, mu in means.items():
        scores = rng.normal(loc=mu, scale=sd, size=n_per_group)
        for score in scores:
            rows.append({"group": group, "score": float(score)})
    return pd.DataFrame(rows)


def _simulate_unequal_n(
    means: Mapping[str, float],
    ns: Mapping[str, int],
    sd: float,
    random_state: Optional[int] = None,
) -> pd.DataFrame:
    """Simulate one-way ANOVA data with unequal group sizes."""
    rng = np.random.default_rng(random_state)
    rows = []
    for group, n in ns.items():
        mu = means[group]
        scores = rng.normal(loc=mu, scale=sd, size=n)
        for score in scores:
            rows.append({"group": group, "score": float(score)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Exercise 1 – Moderate effect, equal Ns
# ---------------------------------------------------------------------------


def exercise_1_moderate_effect(
    random_state: Optional[int] = None,
) -> ProblemResult:
    """
    Exercise 1: Moderate treatment effect with equal group sizes.

    Tuned so that with random_state=123, we usually get:
    - p < .05
    - eta² in the "moderate" range (~0.08–0.15).
    """
    # Three groups: control, low_dose, high_dose
    # Moderate separation, sd chosen to give eta² ~ 0.10.
    means = {"control": 50.0, "low_dose": 52.0, "high_dose": 58.0}
    df = _simulate_equal_n(means, n_per_group=30, sd=10.0, random_state=random_state)

    anova_table = run_one_way_anova(df)
    return ProblemSetResult(name="exercise_1_moderate_effect", data=df, anova_table=anova_table)


# ---------------------------------------------------------------------------
# Exercise 2 – Small effect, equal Ns
# ---------------------------------------------------------------------------


def exercise_2_small_effect(
    random_state: Optional[int] = None,
) -> ProblemResult:
    """
    Exercise 2: Small treatment effect with equal group sizes.

    Tuned so that with random_state=456, we usually get:
    - eta² between roughly 0.01 and 0.06
    - p often non-significant (illustrating low power).
    """
    # Very modest separation between groups.
    means = {"control": 50.0, "low_dose": 51.0, "high_dose": 54.0}
    df = _simulate_equal_n(means, n_per_group=30, sd=10.0, random_state=random_state)

    anova_table = run_one_way_anova(df)
    return ProblemSetResult(name="exercise_2_small_effect", data=df, anova_table=anova_table)


# ---------------------------------------------------------------------------
# Exercise 3 – Strong effect, unequal Ns
# ---------------------------------------------------------------------------


def exercise_3_unequal_n_strong_effect(
    random_state: Optional[int] = None,
) -> ProblemResult:
    """
    Exercise 3: Strong effect with unequal Ns.

    Unequal sample sizes plus a large difference for the high_dose group.
    For a wide range of seeds this yields:
    - Very small p-values (p << .01)
    - eta² around 0.30+.
    """
    means = {"control": 50.0, "low_dose": 52.0, "high_dose": 65.0}
    ns = {"control": 20, "low_dose": 30, "high_dose": 35}
    df = _simulate_unequal_n(means, ns, sd=10.0, random_state=random_state)

    anova_table = run_one_way_anova(df)
    return ProblemSetResult(
        name="exercise_3_unequal_n_strong_effect",
        data=df,
        anova_table=anova_table,
    )


# ---------------------------------------------------------------------------
# Reporting helpers (for the CLI script usage)
# ---------------------------------------------------------------------------


def _summarise_group_means(df: pd.DataFrame) -> pd.Series:
    """Return a nice summary of group means (for printing)."""
    return df.groupby("group")["score"].mean().sort_index()


def _print_exercise_summary(result: ProblemSetResult) -> None:
    """Pretty-print a short summary for one exercise."""
    means = _summarise_group_means(result.data)
    row = result.anova_table.iloc[0]

    print("------------------------------------------------------------")
    for group, mean in means.items():
        print(f"{group:>10} mean = {mean:6.2f}")
    print(
        f"  F({int(row['ddof1'])}, {int(row['ddof2'])}) = {row['F']:6.2f}, "
        f"p = {row['p-unc']:.4f}, eta² = {row['eta2']:.3f}"
    )
    print()


def _build_summary_table(results: Iterable[ProblemSetResult]) -> pd.DataFrame:
    """Build a compact CSV-friendly summary across all exercises."""
    rows = []
    for res in results:
        a = res.anova_table.iloc[0]
        n_total = len(res.data)
        rows.append(
            {
                "exercise": res.name,
                "n_total": int(n_total),
                "ddof1": int(a["ddof1"]),
                "ddof2": int(a["ddof2"]),
                "F": float(a["F"]),
                "p-unc": float(a["p-unc"]),
                "eta2": float(a["eta2"]),
            }
        )
    return pd.DataFrame(rows)


def _plot_group_means(results: Iterable[ProblemSetResult]) -> None:
    """
    Simple bar plot of group means for each exercise.

    This is mainly a visual aid for the docs and for instructors.
    """
    results = list(results)
    exercises = [r.name for r in results]
    groups = sorted(results[0].data["group"].unique())

    # Build matrix of means: rows = exercises, cols = groups
    mean_matrix = []
    for res in results:
        means = res.data.groupby("group")["score"].mean()
        mean_matrix.append([means[g] for g in groups])

    mean_arr = np.asarray(mean_matrix)

    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(exercises))
    width = 0.25

    for j, group in enumerate(groups):
        ax.bar(
            x + (j - 1) * width,
            mean_arr[:, j],
            width=width,
            label=group,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(exercises, rotation=20, ha="right")
    ax.set_ylabel("Mean score")
    ax.set_title("Chapter 12 problem-set – group means")
    ax.legend()

    fig.tight_layout()
    out_path = TRACK_C_OUTPUT_DIR / "ch12_problem_set_group_means.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main CLI entry point (used by Makefile target psych-ch12-problems)
# ---------------------------------------------------------------------------


def main() -> None:
    """Run all Chapter 12 problem-set exercises and save outputs."""
    print("Running Chapter 12 problem-set lab (one-way ANOVA)...\n")

    _ensure_dirs()

    # Run each exercise with a fixed random_state to make results reproducible.
    ex1 = exercise_1_moderate_effect(random_state=123)
    print("Exercise 1 Moderate Effect")
    _print_exercise_summary(ex1)

    ex2 = exercise_2_small_effect(random_state=456)
    print("Exercise 2 Small Effect")
    _print_exercise_summary(ex2)

    ex3 = exercise_3_unequal_n_strong_effect(random_state=789)
    print("Exercise 3 Unequal N Strong Effect")
    _print_exercise_summary(ex3)

    results = [ex1, ex2, ex3]

    # Save raw data for each exercise
    for res in results:
        out_csv = SYNTHETIC_DATA_DIR / f"psych_ch12_{res.name}.csv"
        res.data.to_csv(out_csv, index=False)

    # Save summary table
    summary = _build_summary_table(results)
    summary_path = TRACK_C_OUTPUT_DIR / "ch12_problem_set_results.csv"
    summary.to_csv(summary_path, index=False)

    # Plot group means
    _plot_group_means(results)

    print(f"Data for each exercise saved under: {SYNTHETIC_DATA_DIR}")
    print(f"Summary table saved to: {summary_path}")
    print(
        f"Group means plot saved to: "
        f"{TRACK_C_OUTPUT_DIR / 'ch12_problem_set_group_means.png'}\n"
    )
    print("Chapter 12 problem-set lab complete.")


if __name__ == "__main__":
    main()
