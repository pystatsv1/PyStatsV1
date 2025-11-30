"""Chapter 13: 2x2 factorial design and two-way ANOVA (Track B).

This module simulates a balanced 2x2 Training x Context design on stress scores,
computes the two-way ANOVA (main effects + interaction), and optionally
computes simple main effects of Training within each Context.

It is intentionally limited to balanced between-subjects designs to keep the
math transparent for the Track B mini-book.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TwoWayAnovaResult:
    """Container for two-way ANOVA results (balanced design)."""

    levels_A: List[str]
    levels_B: List[str]
    n_per_cell: int
    N: int

    ss_A: float
    ss_B: float
    ss_AB: float
    ss_within: float
    ss_total: float

    df_A: int
    df_B: int
    df_AB: int
    df_within: int
    df_total: int

    ms_A: float
    ms_B: float
    ms_AB: float
    ms_within: float

    F_A: float
    p_A: float
    F_B: float
    p_B: float
    F_AB: float
    p_AB: float

    eta2_A: float
    eta2_B: float
    eta2_AB: float


@dataclass
class SimpleMainEffectResult:
    """Simple main effect of Training within a single Context level."""

    context: str
    n_control: int
    n_cbt: int
    mean_control: float
    mean_cbt: float
    t_stat: float
    df: int
    p_value: float


def simulate_two_way_stress_study(
    n_per_cell: int = 25,
    mean_control_low: float = 18.0,
    mean_control_high: float = 23.0,
    mean_cbt_low: float = 17.0,
    mean_cbt_high: float = 19.0,
    sd: float = 3.5,
    random_state: int | np.random.Generator | None = 2025,
) -> pd.DataFrame:
    """Simulate a balanced 2x2 Training x Context stress study.

    Parameters
    ----------
    n_per_cell:
        Number of participants in each Training x Context cell.
    mean_control_low, mean_control_high, mean_cbt_low, mean_cbt_high:
        Cell means for stress_score.
    sd:
        Common within-cell standard deviation.
    random_state:
        Seed or Generator for reproducibility.

    Returns
    -------
    DataFrame with columns: training, context, stress_score.
    """
    rng = np.random.default_rng(random_state)

    rows: list[dict[str, object]] = []
    cells = [
        ("control", "low_stress", mean_control_low),
        ("control", "high_stress", mean_control_high),
        ("cbt", "low_stress", mean_cbt_low),
        ("cbt", "high_stress", mean_cbt_high),
    ]

    for training, context, mu in cells:
        scores = rng.normal(loc=mu, scale=sd, size=n_per_cell)
        for score in scores:
            rows.append(
                {
                    "training": training,
                    "context": context,
                    "stress_score": float(score),
                }
            )

    return pd.DataFrame(rows)


def _check_balanced(df: pd.DataFrame) -> int:
    """Verify equal n per Training x Context cell and return that n."""
    counts = df.groupby(["training", "context"])["stress_score"].size()
    unique_counts = counts.unique()
    if len(unique_counts) != 1:
        raise ValueError(
            "Two-way ANOVA helpers assume a balanced design "
            "(equal n in every Training x Context cell)."
        )
    return int(unique_counts[0])


def two_way_anova(df: pd.DataFrame) -> TwoWayAnovaResult:
    """Compute a two-way ANOVA for a balanced 2x2 Training x Context design.

    The decomposition uses:
        SS_total = SS_A + SS_B + SS_AB + SS_within

    where A = Training, B = Context.
    """
    n_per_cell = _check_balanced(df)

    levels_A = sorted(df["training"].unique().tolist())
    levels_B = sorted(df["context"].unique().tolist())
    a = len(levels_A)
    b = len(levels_B)
    N = len(df)

    if a * b * n_per_cell != N:
        raise ValueError(
            "Balanced 2x2 design expected (a * b * n_per_cell must equal N)."
        )

    y = df["stress_score"].to_numpy()
    grand_mean = float(y.mean())
    # Total sum of squares
    ss_total = float(np.sum((y - grand_mean) ** 2))

    # Cell means and counts
    cell_groups = df.groupby(["training", "context"])["stress_score"]
    cell_means = cell_groups.mean()
    cell_counts = cell_groups.size()

    # Between-cells SS (A + B + AB)
    ss_between_cells = sum(
        cell_counts.loc[(i, j)]
        * (cell_means.loc[(i, j)] - grand_mean) ** 2
        for i in levels_A
        for j in levels_B
    )

    # Main effect of A (Training)
    A_groups = df.groupby("training")["stress_score"]
    A_means = A_groups.mean()
    A_counts = A_groups.size()
    ss_A = sum(
        A_counts[level] * (A_means[level] - grand_mean) ** 2
        for level in levels_A
    )

    # Main effect of B (Context)
    B_groups = df.groupby("context")["stress_score"]
    B_means = B_groups.mean()
    B_counts = B_groups.size()
    ss_B = sum(
        B_counts[level] * (B_means[level] - grand_mean) ** 2
        for level in levels_B
    )

    # Interaction SS = between-cells SS - main effects
    ss_AB = ss_between_cells - ss_A - ss_B

    # Within-cell (error) SS
    ss_within = 0.0
    for i in levels_A:
        for j in levels_B:
            scores = df[(df["training"] == i) & (df["context"] == j)][
                "stress_score"
            ].to_numpy()
            cell_mean = cell_means.loc[(i, j)]
            ss_within += float(np.sum((scores - cell_mean) ** 2))

    # Degrees of freedom
    df_A = a - 1
    df_B = b - 1
    df_AB = (a - 1) * (b - 1)
    df_within = N - a * b
    df_total = N - 1

    # Mean squares
    ms_A = ss_A / df_A
    ms_B = ss_B / df_B
    ms_AB = ss_AB / df_AB
    ms_within = ss_within / df_within

    # F and p-values (right-tailed tests)
    F_A = ms_A / ms_within
    F_B = ms_B / ms_within
    F_AB = ms_AB / ms_within

    p_A = float(stats.f.sf(F_A, df_A, df_within))
    p_B = float(stats.f.sf(F_B, df_B, df_within))
    p_AB = float(stats.f.sf(F_AB, df_AB, df_within))

    # Eta-squared style effect sizes
    eta2_A = ss_A / ss_total if ss_total > 0 else float("nan")
    eta2_B = ss_B / ss_total if ss_total > 0 else float("nan")
    eta2_AB = ss_AB / ss_total if ss_total > 0 else float("nan")

    return TwoWayAnovaResult(
        levels_A=levels_A,
        levels_B=levels_B,
        n_per_cell=n_per_cell,
        N=N,
        ss_A=ss_A,
        ss_B=ss_B,
        ss_AB=ss_AB,
        ss_within=ss_within,
        ss_total=ss_total,
        df_A=df_A,
        df_B=df_B,
        df_AB=df_AB,
        df_within=df_within,
        df_total=df_total,
        ms_A=ms_A,
        ms_B=ms_B,
        ms_AB=ms_AB,
        ms_within=ms_within,
        F_A=F_A,
        p_A=p_A,
        F_B=F_B,
        p_B=p_B,
        F_AB=F_AB,
        p_AB=p_AB,
        eta2_A=eta2_A,
        eta2_B=eta2_B,
        eta2_AB=eta2_AB,
    )


def compute_simple_main_effects_training_within_context(
    df: pd.DataFrame,
) -> list[SimpleMainEffectResult]:
    """Compute simple main effects of Training within each Context level.

    Uses independent-samples t-tests (equal variances) within each context.
    """
    results: list[SimpleMainEffectResult] = []

    for context_level, sub in df.groupby("context"):
        control = sub[sub["training"] == "control"]["stress_score"].to_numpy()
        cbt = sub[sub["training"] == "cbt"]["stress_score"].to_numpy()

        if len(control) == 0 or len(cbt) == 0:
            continue

        t_stat, p_val = stats.ttest_ind(control, cbt, equal_var=True)
        df_t = len(control) + len(cbt) - 2

        results.append(
            SimpleMainEffectResult(
                context=context_level,
                n_control=len(control),
                n_cbt=len(cbt),
                mean_control=float(control.mean()),
                mean_cbt=float(cbt.mean()),
                t_stat=float(t_stat),
                df=int(df_t),
                p_value=float(p_val),
            )
        )

    return results


def _print_results(
    anova: TwoWayAnovaResult,
    simple_effects: Optional[list[SimpleMainEffectResult]] = None,
) -> None:
    """Pretty-print ANOVA table and simple main effects."""
    print("Two-way ANOVA on stress scores (Training × Context)")
    print("---------------------------------------------------")
    print(f"Levels (training): {', '.join(anova.levels_A)}")
    print(f"Levels (context):  {', '.join(anova.levels_B)}")
    print(f"n per cell: {anova.n_per_cell}, N = {anova.N}\n")

    print("ANOVA table:")
    print(
        f"  SS_A  (Training)       = {anova.ss_A:8.2f}, "
        f"df_A  = {anova.df_A:2d}, MS_A  = {anova.ms_A:6.2f}, "
        f"F_A  = {anova.F_A:5.2f}, p_A  = {anova.p_A:6.3f}"
    )
    print(
        f"  SS_B  (Context)        = {anova.ss_B:8.2f}, "
        f"df_B  = {anova.df_B:2d}, MS_B  = {anova.ms_B:6.2f}, "
        f"F_B  = {anova.F_B:5.2f}, p_B  = {anova.p_B:6.3f}"
    )
    print(
        f"  SS_AB (Interaction)    = {anova.ss_AB:8.2f}, "
        f"df_AB = {anova.df_AB:2d}, MS_AB = {anova.ms_AB:6.2f}, "
        f"F_AB = {anova.F_AB:5.2f}, p_AB = {anova.p_AB:6.3f}"
    )
    print(
        f"  SS_within              = {anova.ss_within:8.2f}, "
        f"df_within = {anova.df_within:3d}, MS_within = {anova.ms_within:6.2f}"
    )
    print(
        f"  SS_total               = {anova.ss_total:8.2f}, "
        f"df_total  = {anova.df_total:3d}\n"
    )

    print("Effect sizes (eta-squared style):")
    print(f"  eta^2_Training    = {anova.eta2_A:.3f}")
    print(f"  eta^2_Context     = {anova.eta2_B:.3f}")
    print(f"  eta^2_Interaction = {anova.eta2_AB:.3f}\n")

    if simple_effects:
        print("Simple main effects (Training within each Context):")
        for res in simple_effects:
            print(
                f"  Training within {res.context}: "
                f"t({res.df}) = {res.t_stat:5.2f}, p = {res.p_value:6.3f}"
            )
        print()


def _plot_interaction(
    df: pd.DataFrame,
    output_path: str | Path | None = None,
) -> Path | None:
    """Plot mean stress by Context with separate lines for Training."""
    means = (
        df.groupby(["context", "training"])["stress_score"]
        .mean()
        .unstack("training")
        .sort_index()
    )

    contexts = means.index.tolist()
    training_levels = means.columns.tolist()

    plt.figure()
    for training in training_levels:
        plt.plot(
            contexts,
            means[training].values,
            marker="o",
            label=training,
        )

    plt.xlabel("Context")
    plt.ylabel("Mean stress_score")
    plt.title("Interaction plot: Training × Context")
    plt.legend()
    plt.tight_layout()

    if output_path is None:
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()

    return output_path


def main(
    n_per_cell: int = 25,
    random_state: int = 2025,
    csv_out: str | None = "data/synthetic/psych_ch13_two_way_stress.csv",
    plot_out: str | None = "outputs/track_b/ch13_training_by_context.png",
) -> None:
    """Entry point for the Chapter 13 lab script."""
    df = simulate_two_way_stress_study(
        n_per_cell=n_per_cell,
        random_state=random_state,
    )

    anova = two_way_anova(df)
    simple_effects = compute_simple_main_effects_training_within_context(df)

    _print_results(anova, simple_effects)

    if csv_out is not None:
        csv_path = Path(csv_out)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"\nData written to: {csv_path}")

    if plot_out is not None:
        plot_path = _plot_interaction(df, plot_out)
        if plot_path is not None:
            print(f"Interaction plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
