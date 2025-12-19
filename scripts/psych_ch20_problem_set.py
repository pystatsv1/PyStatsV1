"""
Track C – Chapter 20 problem set (The Responsible Researcher).

This problem set practices three "capstone" ideas:

1) Power analysis (a priori) for an independent-samples t-test.
2) Meta-analysis (fixed vs random effects) with heterogeneity.
3) Questionable research practice demo: optional stopping inflates Type I error.

Outputs:
- Synthetic datasets: data/synthetic/
- Summaries + plots: outputs/track_c/
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
TRACK_C_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "track_c"


@dataclass(frozen=True)
class ProblemResult:
    """Container for one problem set exercise."""
    name: str
    data: pd.DataFrame
    summary_table: pd.DataFrame


def _ensure_dirs() -> None:
    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRACK_C_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# Exercise 1: Power analysis
# -------------------------
def power_ttest_ind(
    d: float,
    n_per_group: int,
    *,
    alpha: float = 0.05,
    two_sided: bool = True,
) -> float:
    """
    Power for an independent-samples t-test (equal n per group), using the
    noncentral t distribution.

    d: Cohen's d (standardized mean difference)
    n_per_group: sample size per group (integer >= 2)
    """
    if n_per_group < 2:
        raise ValueError("n_per_group must be >= 2")

    df = 2 * n_per_group - 2
    ncp = float(d) * np.sqrt(n_per_group / 2.0)

    if two_sided:
        tcrit = stats.t.ppf(1.0 - alpha / 2.0, df)
        cdf_pos = stats.nct.cdf(tcrit, df, ncp)
        cdf_neg = stats.nct.cdf(-tcrit, df, ncp)
        return float(1.0 - (cdf_pos - cdf_neg))

    tcrit = stats.t.ppf(1.0 - alpha, df)
    return float(1.0 - stats.nct.cdf(tcrit, df, ncp))


def required_n_ttest(
    d: float,
    *,
    target_power: float = 0.80,
    alpha: float = 0.05,
    two_sided: bool = True,
    n_min: int = 2,
    n_max: int = 5000,
) -> int:
    """Smallest n_per_group that achieves target_power for the independent t-test."""
    if not (0 < target_power < 1):
        raise ValueError("target_power must be in (0, 1)")

    lo, hi = n_min, n_max
    while lo < hi:
        mid = (lo + hi) // 2
        pwr = power_ttest_ind(d, mid, alpha=alpha, two_sided=two_sided)
        if pwr >= target_power:
            hi = mid
        else:
            lo = mid + 1
    return int(lo)


def _plot_power_curve(data: pd.DataFrame, outfile: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(data["n_per_group"], data["power"], marker="o")
    ax.set_xlabel("n per group")
    ax.set_ylabel("Power")
    ax.set_title(title)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def exercise_1_power_analysis(*, random_state: int = 123) -> ProblemResult:
    """
    Exercise 1: A priori power analysis.

    Target: detect a moderate effect (d=0.50) with 80% power (alpha=0.05, two-sided).
    """
    rng = np.random.default_rng(random_state)
    _ = rng  # keep signature consistent with other chapters (random_state always accepted)

    d = 0.50
    target_power = 0.80
    alpha = 0.05

    n_req = required_n_ttest(d, target_power=target_power, alpha=alpha, two_sided=True)
    achieved = power_ttest_ind(d, n_req, alpha=alpha, two_sided=True)

    n_grid = np.arange(10, 151, 5)
    powers = [power_ttest_ind(d, int(n), alpha=alpha, two_sided=True) for n in n_grid]
    curve = pd.DataFrame({"n_per_group": n_grid, "power": powers})

    summary = pd.DataFrame(
        [
            {
                "d": d,
                "alpha": alpha,
                "target_power": target_power,
                "n_required_per_group": n_req,
                "achieved_power_at_n": achieved,
            }
        ]
    )

    return ProblemResult("exercise_1_power_analysis", curve, summary)


# -------------------------
# Exercise 2: Meta-analysis
# -------------------------
def meta_analysis_fixed(effects: np.ndarray, variances: np.ndarray) -> dict[str, float]:
    w = 1.0 / variances
    est = float(np.sum(w * effects) / np.sum(w))
    se = float(np.sqrt(1.0 / np.sum(w)))
    z = float(est / se)
    p = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
    ci_lo = float(est - 1.96 * se)
    ci_hi = float(est + 1.96 * se)

    Q = float(np.sum(w * (effects - est) ** 2))
    df = int(len(effects) - 1)
    I2 = float(max(0.0, (Q - df) / Q)) if Q > 0 else 0.0

    return {
        "model": "fixed",
        "est": est,
        "se": se,
        "ci95_lo": ci_lo,
        "ci95_hi": ci_hi,
        "z": z,
        "p": p,
        "Q": Q,
        "df_Q": float(df),
        "I2": I2,
    }


def meta_tau2_dl(Q: float, variances: np.ndarray) -> float:
    """DerSimonian–Laird tau^2."""
    k = len(variances)
    w = 1.0 / variances
    c = float(np.sum(w) - (np.sum(w**2) / np.sum(w)))
    if c <= 0:
        return 0.0
    return float(max(0.0, (Q - (k - 1)) / c))


def meta_analysis_random(effects: np.ndarray, variances: np.ndarray) -> dict[str, float]:
    fixed = meta_analysis_fixed(effects, variances)
    tau2 = meta_tau2_dl(float(fixed["Q"]), variances)

    w = 1.0 / (variances + tau2)
    est = float(np.sum(w * effects) / np.sum(w))
    se = float(np.sqrt(1.0 / np.sum(w)))
    z = float(est / se)
    p = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
    ci_lo = float(est - 1.96 * se)
    ci_hi = float(est + 1.96 * se)

    return {
        "model": "random",
        "est": est,
        "se": se,
        "ci95_lo": ci_lo,
        "ci95_hi": ci_hi,
        "z": z,
        "p": p,
        "tau2": float(tau2),
        "I2": float(fixed["I2"]),
    }


def _plot_forest(studies: pd.DataFrame, summary: pd.DataFrame, outfile: Path, title: str) -> None:
    df = studies.copy()
    df["ci_lo"] = df["effect"] - 1.96 * df["se"]
    df["ci_hi"] = df["effect"] + 1.96 * df["se"]

    fig, ax = plt.subplots(figsize=(7, 0.45 * (len(df) + 4)))

    y = np.arange(len(df))[::-1]
    ax.hlines(y, df["ci_lo"], df["ci_hi"])
    ax.plot(df["effect"], y, marker="o", linestyle="None")

    ax.set_yticks(y)
    ax.set_yticklabels(df["study"].astype(str))
    ax.axvline(0.0, linestyle="--")

    # Add pooled estimates at bottom
    y_fixed = -1.5
    y_rand = -2.5

    fixed_row = summary[summary["model"] == "fixed"].iloc[0]
    rand_row = summary[summary["model"] == "random"].iloc[0]

    ax.hlines(y_fixed, fixed_row["ci95_lo"], fixed_row["ci95_hi"], linewidth=3)
    ax.plot(fixed_row["est"], y_fixed, marker="s", linestyle="None")
    ax.text(ax.get_xlim()[0], y_fixed, "Fixed", va="center")

    ax.hlines(y_rand, rand_row["ci95_lo"], rand_row["ci95_hi"], linewidth=3)
    ax.plot(rand_row["est"], y_rand, marker="s", linestyle="None")
    ax.text(ax.get_xlim()[0], y_rand, "Random", va="center")

    ax.set_title(title)
    ax.set_xlabel("Effect size (standardized)")
    ax.set_ylim(-3.5, len(df))
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def exercise_2_meta_analysis(*, random_state: int = 456) -> ProblemResult:
    """
    Exercise 2: Meta-analysis.

    Simulate multiple studies with heterogeneity, then compute:
    - Fixed-effect pooled estimate
    - Random-effects pooled estimate (DerSimonian–Laird)
    - Heterogeneity (Q, I^2, tau^2)
    """
    rng = np.random.default_rng(random_state)

    k = 10
    true_overall = 0.40
    between_sd = 0.30

    se = rng.uniform(0.06, 0.18, size=k)
    true_i = rng.normal(true_overall, between_sd, size=k)
    observed = rng.normal(true_i, se)
    var = se**2

    studies = pd.DataFrame(
        {
            "study": [f"S{i+1}" for i in range(k)],
            "effect": observed,
            "se": se,
            "var": var,
        }
    )

    fixed = meta_analysis_fixed(studies["effect"].to_numpy(), studies["var"].to_numpy())
    rand = meta_analysis_random(studies["effect"].to_numpy(), studies["var"].to_numpy())

    summary = pd.DataFrame([fixed, rand])
    return ProblemResult("exercise_2_meta_analysis", studies, summary)


# -----------------------------------------
# Exercise 3: Optional stopping demonstration
# -----------------------------------------
def simulate_optional_stopping(
    *,
    reps: int = 400,
    n_start: int = 20,
    n_max: int = 60,
    step: int = 10,
    alpha: float = 0.05,
    random_state: int | None = None,
) -> pd.DataFrame:
    """
    Under the null hypothesis (true mean = 0), repeatedly test a one-sample t-test
    while increasing N. This inflates the false-positive rate.
    """
    rng = np.random.default_rng(random_state)
    rows: list[dict[str, Any]] = []

    for i in range(1, reps + 1):
        n = n_start
        x = rng.normal(0.0, 1.0, size=n)
        p = float(stats.ttest_1samp(x, 0.0).pvalue)
        p_min = p
        stopped = p < alpha

        while (not stopped) and (n + step) <= n_max:
            x = np.concatenate([x, rng.normal(0.0, 1.0, size=step)])
            n += step
            p = float(stats.ttest_1samp(x, 0.0).pvalue)
            p_min = float(min(p_min, p))
            stopped = p < alpha

        rows.append(
            {
                "rep": i,
                "final_n": n,
                "final_p": p,
                "min_p": p_min,
                "stopped": stopped,
            }
        )

    return pd.DataFrame(rows)


def _plot_optional_stopping(data: pd.DataFrame, outfile: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(data["min_p"], bins=25)
    ax.axvline(0.05, linestyle="--")
    ax.set_xlabel("Minimum p observed (across looks)")
    ax.set_ylabel("Count")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def exercise_3_optional_stopping(*, random_state: int = 789) -> ProblemResult:
    """
    Exercise 3: Optional stopping inflates Type I error.

    Null is true (mean=0). Because we "peek" multiple times, the false-positive rate
    becomes much larger than alpha=0.05.
    """
    alpha = 0.05
    data = simulate_optional_stopping(
        reps=400,
        n_start=20,
        step=10,
        n_max=60,
        alpha=alpha,
        random_state=random_state,
    )
    false_pos_rate = float(data["stopped"].mean())
    summary = pd.DataFrame(
        [
            {
                "alpha": alpha,
                "reps": 400,
                "n_start": 20,
                "step": 10,
                "n_max": 60,
                "false_positive_rate": false_pos_rate,
                "mean_final_n": float(data["final_n"].mean()),
            }
        ]
    )
    return ProblemResult("exercise_3_optional_stopping", data, summary)


# -------------------------
# Save + CLI
# -------------------------
def _save_result(result: ProblemResult) -> None:
    _ensure_dirs()

    csv_path = SYNTHETIC_DATA_DIR / f"psych_ch20_{result.name}.csv"
    json_path = TRACK_C_OUTPUT_DIR / f"psych_ch20_{result.name}.json"
    plot_path = TRACK_C_OUTPUT_DIR / f"psych_ch20_{result.name}.png"

    result.data.to_csv(csv_path, index=False)

    payload = {
        "name": result.name,
        "summary_table": result.summary_table.to_dict(orient="records"),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if result.name == "exercise_1_power_analysis":
        _plot_power_curve(result.data, plot_path, title=result.name)
    elif result.name == "exercise_2_meta_analysis":
        _plot_forest(result.data, result.summary_table, plot_path, title=result.name)
    elif result.name == "exercise_3_optional_stopping":
        _plot_optional_stopping(result.data, plot_path, title=result.name)


def main() -> None:
    """Run all Ch20 Track C exercises and save outputs."""
    results = [
        exercise_1_power_analysis(random_state=123),
        exercise_2_meta_analysis(random_state=456),
        exercise_3_optional_stopping(random_state=789),
    ]

    for r in results:
        print(f"\n=== {r.name} ===")
        print(r.summary_table)
        _save_result(r)

    print("\nSaved:")
    print(f"- synthetic CSVs in: {SYNTHETIC_DATA_DIR}")
    print(f"- summaries/plots in: {TRACK_C_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
