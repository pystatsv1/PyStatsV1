"""
Chapter 10 Track C problem set – independent-samples t-test.

This module provides small, reusable helpers for the Chapter 10 problem set in
the Psychology track. Each exercise is implemented as a deterministic function
that you can run, inspect, and adapt to your own data.

Run as a script:

    python -m scripts.psych_ch10_problem_set
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg


DATA_DIR = Path("data") / "synthetic"
OUTPUT_DIR = Path("outputs") / "track_c"


@dataclass
class IndependentTResult:
    """Container for one independent-samples t-test scenario."""

    label: str
    data: pd.DataFrame
    t_table: pd.DataFrame


def simulate_independent_t_dataset(
    n_per_group: int,
    effect_size: float,
    random_state: int,
) -> pd.DataFrame:
    """
    Simulate a simple independent-groups experiment.

    Parameters
    ----------
    n_per_group:
        Number of participants in each group.
    effect_size:
        Cohen's d for the treatment effect (treatment minus control).
    random_state:
        Seed for the random number generator.

    Returns
    -------
    DataFrame with columns:
        - "group": "control" or "treatment"
        - "score": numeric outcome variable
    """
    rng = np.random.default_rng(random_state)

    # Baseline mean and standard deviation
    mu_control = 50.0
    sigma = 10.0

    # Treatment mean shifted by d * sigma
    mu_treatment = mu_control + effect_size * sigma

    control_scores = rng.normal(loc=mu_control, scale=sigma, size=n_per_group)
    treatment_scores = rng.normal(
        loc=mu_treatment,
        scale=sigma,
        size=n_per_group,
    )

    df = pd.DataFrame(
        {
            "group": (["control"] * n_per_group)
            + (["treatment"] * n_per_group),
            "score": np.concatenate([control_scores, treatment_scores]),
        }
    )

    return df


def run_independent_t(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run an independent-samples t-test using Pingouin.

    Parameters
    ----------
    df:
        DataFrame with columns "group" and "score".

    Returns
    -------
    Pingouin t-test results as a one-row DataFrame, with additional columns:

        - "mean_control"
        - "mean_treatment"
        - "mean_diff"
    """
    control = df.loc[df["group"] == "control", "score"]
    treatment = df.loc[df["group"] == "treatment", "score"]

    # Pass treatment as x and control as y so that cohen-d is positive
    # when the treatment group has higher scores.
    results = pg.ttest(treatment, control, paired=False)

    mean_control = float(control.mean())
    mean_treatment = float(treatment.mean())
    mean_diff = float(mean_treatment - mean_control)

    results = results.copy()
    results["mean_control"] = mean_control
    results["mean_treatment"] = mean_treatment
    results["mean_diff"] = mean_diff

    return results


def exercise_1_large_sample() -> IndependentTResult:
    """Exercise 1: Moderate effect, reasonably large sample size."""
    df = simulate_independent_t_dataset(
        n_per_group=40,
        effect_size=0.6,
        random_state=10,
    )
    t_table = run_independent_t(df)
    return IndependentTResult(label="exercise_1_large_sample", data=df, t_table=t_table)


def exercise_2_small_sample() -> IndependentTResult:
    """Exercise 2: Same effect size, but much smaller sample (low power)."""
    df = simulate_independent_t_dataset(
        n_per_group=10,
        effect_size=0.6,
        random_state=20,
    )
    t_table = run_independent_t(df)
    return IndependentTResult(label="exercise_2_small_sample", data=df, t_table=t_table)


def exercise_3_large_effect() -> IndependentTResult:
    """Exercise 3: Strong treatment effect with moderate sample size."""
    df = simulate_independent_t_dataset(
        n_per_group=25,
        effect_size=1.0,
        random_state=30,
    )
    t_table = run_independent_t(df)
    return IndependentTResult(label="exercise_3_large_effect", data=df, t_table=t_table)


def _save_scenario_data(scenarios: List[IndependentTResult]) -> None:
    """Save per-exercise datasets to CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for scenario in scenarios:
        out_path = DATA_DIR / f"psych_ch10_{scenario.label}.csv"
        scenario.data.to_csv(out_path, index=False)


def _save_summary_table(scenarios: List[IndependentTResult]) -> Path:
    """Combine the t-tables into a single summary CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: List[pd.DataFrame] = []
    for scenario in scenarios:
        table = scenario.t_table.copy()
        table.insert(0, "exercise", scenario.label)
        rows.append(table)

    summary = pd.concat(rows, ignore_index=True)
    out_path = OUTPUT_DIR / "ch10_problem_set_results.csv"
    summary.to_csv(out_path, index=False)
    return out_path


def _plot_group_means(scenarios: List[IndependentTResult]) -> Path:
    """Create a simple bar plot of group means across exercises."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records: List[Dict[str, object]] = []
    for scenario in scenarios:
        df = scenario.data
        means = df.groupby("group")["score"].mean().reset_index()
        for _, row in means.iterrows():
            records.append(
                {
                    "exercise": scenario.label,
                    "group": row["group"],
                    "mean_score": float(row["score"]),
                }
            )

    summary_df = pd.DataFrame.from_records(records)

    fig, ax = plt.subplots(figsize=(8, 4))

    # Pivot for easy grouped plotting
    pivot = summary_df.pivot(index="exercise", columns="group", values="mean_score")
    pivot.plot(kind="bar", ax=ax)

    ax.set_ylabel("Mean score")
    ax.set_title("Chapter 10 problem set – group means by exercise")
    ax.legend(title="Group")
    fig.tight_layout()

    out_path = OUTPUT_DIR / "ch10_problem_set_group_means.png"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def main() -> None:
    """Run all Chapter 10 problem-set exercises and save outputs."""
    print("Running Chapter 10 problem-set lab (independent-samples t-test)...\n")

    scenarios = [
        exercise_1_large_sample(),
        exercise_2_small_sample(),
        exercise_3_large_effect(),
    ]

    for scenario in scenarios:
        label = scenario.label
        t_table = scenario.t_table

        print(f"{label.replace('_', ' ').title()}")
        print("-" * 60)

        # t_table is a one-row DataFrame; grab that row explicitly
        row = t_table.iloc[0]

        mean_control = float(row["mean_control"])
        mean_treatment = float(row["mean_treatment"])
        mean_diff = float(row["mean_diff"])
        t_val = float(row["T"])
        df = float(row["dof"])
        p_val = float(row["p-val"])
        d = float(row["cohen-d"])

        print(f"  mean_control   = {mean_control:6.2f}")
        print(f"  mean_treatment = {mean_treatment:6.2f}")
        print(f"  mean_diff      = {mean_diff:6.2f}")
        print(f"  t({df:.0f}) = {t_val:6.2f}, p = {p_val:.4f}, d = {d:5.2f}")
        print()

    _save_scenario_data(scenarios)
    summary_path = _save_summary_table(scenarios)
    plot_path = _plot_group_means(scenarios)

    print(f"Data for each exercise saved under: {DATA_DIR}")
    print(f"Summary table saved to: {summary_path}")
    print(f"Group means plot saved to: {plot_path}")
    print("\nChapter 10 problem-set lab complete.")


if __name__ == "__main__":
    main()
