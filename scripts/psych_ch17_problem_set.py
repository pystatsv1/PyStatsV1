"""
Track C – Chapter 17 problem set (Mixed-Model Designs / Mixed ANOVA).

We simulate a classic mixed design:
- Between-subjects factor: group (Control vs Treatment)
- Within-subjects factor: time (T1, T2, T3)
- DV: score

Then we run a Mixed ANOVA (Pingouin) and ask students to interpret:
- main effect of time
- main effect of group
- interaction (group × time)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
TRACK_C_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "track_c"


@dataclass(frozen=True)
class ProblemResult:
    """Container for one problem set exercise."""
    name: str
    data: pd.DataFrame
    anova_table: pd.DataFrame
    cell_means: pd.DataFrame


def _ensure_dirs() -> None:
    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRACK_C_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def simulate_mixed_design_dataset(
    *,
    n_per_group: int,
    means: dict[str, dict[str, float]],
    subject_sd: float = 6.0,
    error_sd: float = 3.0,
    random_state: int | None = None,
) -> pd.DataFrame:
    """Simulate long-format data for a mixed design with subject random intercepts."""
    rng = np.random.default_rng(random_state)

    groups = ["Control", "Treatment"]
    times = ["T1", "T2", "T3"]

    rows: list[dict[str, Any]] = []
    subject_id = 0

    for g in groups:
        for _ in range(n_per_group):
            subject_id += 1
            subj = f"S{subject_id:03d}"
            random_intercept = rng.normal(0.0, subject_sd)

            for t in times:
                mu = float(means[g][t])
                y = mu + random_intercept + rng.normal(0.0, error_sd)
                rows.append({"subject": subj, "group": g, "time": t, "score": y})

    df = pd.DataFrame(rows)
    # Make factors explicit + stable ordering
    df["group"] = pd.Categorical(df["group"], categories=groups, ordered=True)
    df["time"] = pd.Categorical(df["time"], categories=times, ordered=True)
    return df


def _simulate_time_only_no_interaction_dataset(
    *,
    n_per_group: int,
    time_means: dict[str, float],
    subject_sd: float = 6.0,
    error_sd: float = 3.0,
    random_state: int | None = None,
) -> pd.DataFrame:
    """
    Simulate a mixed-design dataset with a *time main effect only*.

    Key idea: generate one set of subject trajectories (random intercept + within-subject noise)
    and then copy those trajectories for the other group. This makes:
      - group effect = 0 (exactly)
      - interaction = 0 (exactly)
    while still allowing a strong time main effect.
    """
    rng = np.random.default_rng(random_state)

    groups = ["Control", "Treatment"]
    times = ["T1", "T2", "T3"]

    # Random intercepts + within-subject noise for ONE group's subjects
    random_intercepts = rng.normal(0.0, subject_sd, size=n_per_group)
    errors = rng.normal(0.0, error_sd, size=(n_per_group, len(times)))

    time_vec = np.array([float(time_means[t]) for t in times], dtype=float)
    # scores[i, j] = mean_at_time_j + subject_intercept_i + error_ij
    scores = time_vec[None, :] + random_intercepts[:, None] + errors

    rows: list[dict[str, Any]] = []
    for g, prefix in [("Control", "C"), ("Treatment", "T")]:
        for i in range(n_per_group):
            subj = f"{prefix}{i + 1:03d}"
            for j, t in enumerate(times):
                rows.append(
                    {
                        "subject": subj,
                        "group": g,
                        "time": t,
                        "score": float(scores[i, j]),
                    }
                )

    df = pd.DataFrame(rows)
    df["group"] = pd.Categorical(df["group"], categories=groups, ordered=True)
    df["time"] = pd.Categorical(df["time"], categories=times, ordered=True)
    return df


def run_mixed_anova(data: pd.DataFrame) -> pd.DataFrame:
    """Run mixed ANOVA: score ~ group (between) × time (within) with subject id."""
    table = pg.mixed_anova(
        data=data,
        dv="score",
        within="time",
        between="group",
        subject="subject",
    )
    return table


def _cell_means(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(["group", "time"], observed=True)["score"]
        .mean()
        .reset_index()
        .rename(columns={"score": "mean_score"})
    )


def _plot_means(cell_means: pd.DataFrame, outfile: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    for g in cell_means["group"].unique():
        sub = cell_means[cell_means["group"] == g]
        ax.plot(sub["time"].astype(str), sub["mean_score"], marker="o", label=str(g))
    ax.set_xlabel("Time")
    ax.set_ylabel("Mean score")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def exercise_1_strong_interaction(*, random_state: int = 123) -> ProblemResult:
    """
    Exercise 1: Strong group×time interaction.
    Control stays flat; Treatment improves sharply over time.
    """
    data = simulate_mixed_design_dataset(
        n_per_group=25,
        random_state=random_state,
        means={
            "Control": {"T1": 50, "T2": 50, "T3": 50},
            "Treatment": {"T1": 50, "T2": 60, "T3": 70},
        },
    )
    table = run_mixed_anova(data)
    means = _cell_means(data)
    return ProblemResult("exercise_1_strong_interaction", data, table, means)


def exercise_2_time_only(*, random_state: int = 456) -> ProblemResult:
    """
    Exercise 2: Main effect of time only.
    Both groups improve similarly; no group effect, no interaction.
    """
    data = _simulate_time_only_no_interaction_dataset(
        n_per_group=25,
        random_state=random_state,
        time_means={"T1": 50, "T2": 56, "T3": 62},
        # Keep time effect strong and noise modest so p(time) is reliably < 0.01
        subject_sd=6.0,
        error_sd=3.0,
    )
    table = run_mixed_anova(data)
    means = _cell_means(data)
    return ProblemResult("exercise_2_time_only", data, table, means)


def exercise_3_group_only(*, random_state: int = 789) -> ProblemResult:
    """
    Exercise 3: Main effect of group only (parallel lines).
    Treatment is higher overall; no time effect; no interaction.
    """
    data = simulate_mixed_design_dataset(
        n_per_group=25,
        random_state=random_state,
        means={
            "Control": {"T1": 50, "T2": 50, "T3": 50},
            "Treatment": {"T1": 64, "T2": 64, "T3": 64},
        },
    )
    table = run_mixed_anova(data)
    means = _cell_means(data)
    return ProblemResult("exercise_3_group_only", data, table, means)


def _save_result(result: ProblemResult) -> None:
    _ensure_dirs()

    csv_path = SYNTHETIC_DATA_DIR / f"psych_ch17_{result.name}.csv"
    json_path = TRACK_C_OUTPUT_DIR / f"psych_ch17_{result.name}.json"
    plot_path = TRACK_C_OUTPUT_DIR / f"psych_ch17_{result.name}.png"

    result.data.to_csv(csv_path, index=False)

    payload = {
        "name": result.name,
        "anova_table": result.anova_table.to_dict(orient="records"),
        "cell_means": result.cell_means.to_dict(orient="records"),
    }
    json_path.write_text(pd.Series(payload).to_json(), encoding="utf-8")

    _plot_means(result.cell_means, plot_path, title=result.name)


def main() -> None:
    """Run all Ch17 Track C exercises and save outputs."""
    results = [
        exercise_1_strong_interaction(random_state=123),
        exercise_2_time_only(random_state=456),
        exercise_3_group_only(random_state=789),
    ]

    for r in results:
        print(f"\n=== {r.name} ===")
        print(r.anova_table)
        _save_result(r)

    print("\nSaved:")
    print(f"- synthetic CSVs in: {SYNTHETIC_DATA_DIR}")
    print(f"- summaries/plots in: {TRACK_C_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
