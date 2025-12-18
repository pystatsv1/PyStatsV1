"""
Track C – Chapter 18 problem set (ANCOVA).

We simulate a classic ANCOVA design:
- Between-subjects factor: group (Control vs Treatment)
- Covariate: pretest
- DV: posttest

Students practice:
1) Interpreting the covariate-adjusted group effect
2) Recognizing a spurious raw group difference caused by pretest imbalance
3) Checking the homogeneity of regression slopes assumption (group × covariate)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
TRACK_C_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "track_c"


@dataclass(frozen=True)
class ProblemResult:
    """Container for one problem set exercise."""
    name: str
    data: pd.DataFrame
    ancova_table: pd.DataFrame
    adjusted_means: pd.DataFrame
    slopes_test: pd.DataFrame


def _ensure_dirs() -> None:
    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRACK_C_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def simulate_ancova_dataset(
    *,
    n_per_group: int,
    pretest_shift: dict[str, float],
    group_effect: dict[str, float],
    slope: dict[str, float],
    pretest_mean: float = 50.0,
    pretest_sd: float = 10.0,
    base_post: float = 60.0,
    error_sd: float = 6.0,
    random_state: int | None = None,
) -> pd.DataFrame:
    """
    Simulate ANCOVA data with a pretest covariate and posttest outcome.

    posttest = base_post + slope[group]*(pretest - pretest_mean) + group_effect[group] + error
    """
    rng = np.random.default_rng(random_state)

    groups = ["Control", "Treatment"]
    rows: list[dict[str, Any]] = []
    subject_id = 0

    for g in groups:
        mu_pre = pretest_mean + float(pretest_shift[g])
        pre = rng.normal(mu_pre, pretest_sd, size=n_per_group)

        for p in pre:
            subject_id += 1
            subj = f"S{subject_id:03d}"
            y = (
                base_post
                + float(slope[g]) * (float(p) - pretest_mean)
                + float(group_effect[g])
                + rng.normal(0.0, error_sd)
            )
            rows.append(
                {"subject": subj, "group": g, "pretest": float(p), "posttest": float(y)}
            )

    df = pd.DataFrame(rows)
    df["group"] = pd.Categorical(df["group"], categories=groups, ordered=True)
    return df


def run_ancova(data: pd.DataFrame) -> pd.DataFrame:
    """Run ANCOVA: posttest ~ group + pretest."""
    return pg.ancova(data=data, dv="posttest", covar="pretest", between="group")


def run_slopes_test(data: pd.DataFrame) -> pd.DataFrame:
    """
    Test homogeneity of regression slopes via interaction:
    posttest ~ pretest * group
    """
    model = smf.ols("posttest ~ pretest * C(group)", data=data).fit()
    table = anova_lm(model, typ=2).reset_index().rename(columns={"index": "term"})
    return table


def adjusted_means_at_covariate_mean(data: pd.DataFrame) -> pd.DataFrame:
    """
    Compute adjusted means (predicted posttest) for each group at the overall mean pretest.
    """
    cov_mean = float(data["pretest"].mean())
    model = smf.ols("posttest ~ pretest + C(group)", data=data).fit()

    groups = list(data["group"].cat.categories)
    pred_rows: list[dict[str, Any]] = []
    for g in groups:
        new = pd.DataFrame({"pretest": [cov_mean], "group": [g]})
        pred = float(model.predict(new).iloc[0])
        pred_rows.append({"group": g, "pretest_at": cov_mean, "adjusted_mean": pred})

    return pd.DataFrame(pred_rows)


def _plot_scatter_with_lines(data: pd.DataFrame, outfile: Path, title: str) -> None:
    """
    Scatter pretest vs posttest with fitted lines per group.
    (Uses interaction model so assumption violations are visible.)
    """
    model = smf.ols("posttest ~ pretest * C(group)", data=data).fit()
    x_min, x_max = float(data["pretest"].min()), float(data["pretest"].max())
    xs = np.linspace(x_min, x_max, 50)

    fig, ax = plt.subplots(figsize=(7, 4))

    for g in data["group"].cat.categories:
        sub = data[data["group"] == g]
        ax.scatter(sub["pretest"], sub["posttest"], alpha=0.6, label=str(g))

        new = pd.DataFrame({"pretest": xs, "group": [g] * len(xs)})
        ys = model.predict(new)
        ax.plot(xs, ys)

    ax.set_xlabel("Pretest (covariate)")
    ax.set_ylabel("Posttest (DV)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def exercise_1_true_group_effect(*, random_state: int = 123) -> ProblemResult:
    """
    Exercise 1: True Treatment advantage after controlling for pretest.
    Expect: significant group effect + significant covariate effect.
    """
    data = simulate_ancova_dataset(
        n_per_group=80,
        random_state=random_state,
        pretest_shift={"Control": 0.0, "Treatment": 0.0},
        group_effect={"Control": 0.0, "Treatment": 8.0},
        slope={"Control": 0.60, "Treatment": 0.60},
        error_sd=6.0,
    )
    anc = run_ancova(data)
    adj = adjusted_means_at_covariate_mean(data)
    slopes = run_slopes_test(data)
    return ProblemResult("exercise_1_true_group_effect", data, anc, adj, slopes)


def exercise_2_spurious_raw_difference(*, random_state: int = 456) -> ProblemResult:
    """
    Exercise 2: Spurious raw group difference caused by pretest imbalance.
    Treatment starts higher on pretest; there is NO true group effect on posttest.
    Expect: group effect non-significant in ANCOVA; covariate significant.
    """
    data = simulate_ancova_dataset(
        n_per_group=100,
        random_state=random_state,
        pretest_shift={"Control": 0.0, "Treatment": 6.0},
        group_effect={"Control": 0.0, "Treatment": 0.0},
        slope={"Control": 0.70, "Treatment": 0.70},
        error_sd=6.5,
    )
    anc = run_ancova(data)
    adj = adjusted_means_at_covariate_mean(data)
    slopes = run_slopes_test(data)
    return ProblemResult("exercise_2_spurious_raw_difference", data, anc, adj, slopes)


def exercise_3_slopes_violation(*, random_state: int = 789) -> ProblemResult:
    """
    Exercise 3: Violation of homogeneity of regression slopes.
    Control and Treatment have different pretest→posttest slopes.
    Expect: significant pretest×group interaction in slopes test.
    """
    data = simulate_ancova_dataset(
        n_per_group=90,
        random_state=random_state,
        pretest_shift={"Control": 0.0, "Treatment": 0.0},
        group_effect={"Control": 0.0, "Treatment": 0.0},
        slope={"Control": 0.30, "Treatment": 0.95},
        error_sd=6.0,
    )
    anc = run_ancova(data)
    adj = adjusted_means_at_covariate_mean(data)
    slopes = run_slopes_test(data)
    return ProblemResult("exercise_3_slopes_violation", data, anc, adj, slopes)


def _save_result(result: ProblemResult) -> None:
    _ensure_dirs()

    csv_path = SYNTHETIC_DATA_DIR / f"psych_ch18_{result.name}.csv"
    json_path = TRACK_C_OUTPUT_DIR / f"psych_ch18_{result.name}.json"
    plot_path = TRACK_C_OUTPUT_DIR / f"psych_ch18_{result.name}.png"

    result.data.to_csv(csv_path, index=False)

    payload = {
        "name": result.name,
        "ancova_table": result.ancova_table.to_dict(orient="records"),
        "adjusted_means": result.adjusted_means.to_dict(orient="records"),
        "slopes_test": result.slopes_test.to_dict(orient="records"),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    _plot_scatter_with_lines(result.data, plot_path, title=result.name)


def main() -> None:
    """Run all Ch18 Track C exercises and save outputs."""
    results = [
        exercise_1_true_group_effect(random_state=123),
        exercise_2_spurious_raw_difference(random_state=456),
        exercise_3_slopes_violation(random_state=789),
    ]

    for r in results:
        print(f"\n=== {r.name} ===")
        print(r.ancova_table)
        print("\nAdjusted means:")
        print(r.adjusted_means)
        print("\nSlopes test:")
        print(r.slopes_test)
        _save_result(r)

    print("\nSaved:")
    print(f"- synthetic CSVs in: {SYNTHETIC_DATA_DIR}")
    print(f"- summaries/plots in: {TRACK_C_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
