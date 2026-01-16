"""
Track C – Chapter 19 problem set (Non-Parametric Statistics).

We cover common non-parametric / categorical tests used when assumptions fail:
1) Chi-square goodness-of-fit (GOF)
2) Chi-square test of independence (contingency tables)
3) Rank-based group comparisons: Mann–Whitney U and Kruskal–Wallis

Each exercise simulates a dataset, runs the appropriate test, and saves:
- synthetic CSV in data/synthetic/
- JSON summary + plot in outputs/track_c/
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, chisquare, kruskal, mannwhitneyu


# Matplotlib 3.9 renamed `labels` -> `tick_labels` for Axes.boxplot.
# This import works both when run via `python -m scripts...` and when executed
# as a plain script from the `scripts/` folder.
try:
    from scripts._mpl_compat import ax_boxplot
except ImportError:  # pragma: no cover
    from _mpl_compat import ax_boxplot  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
TRACK_C_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "track_c"


@dataclass(frozen=True)
class ProblemResult:
    """Container for one problem set exercise."""
    name: str
    data: pd.DataFrame
    summary: dict[str, Any]


def _ensure_dirs() -> None:
    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRACK_C_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _cramers_v(contingency: pd.DataFrame) -> float:
    """
    Cramér's V effect size for chi-square independence.
    """
    chi2, _, _, _ = chi2_contingency(contingency.to_numpy(), correction=False)
    n = float(contingency.to_numpy().sum())
    r, k = contingency.shape
    denom = n * (min(r, k) - 1)
    if denom <= 0:
        return 0.0
    return float(np.sqrt(chi2 / denom))


def _epsilon_squared_kw(h_stat: float, n_total: int, k_groups: int) -> float:
    """
    Epsilon-squared effect size for Kruskal–Wallis:
    eps^2 = (H - k + 1) / (n - k)
    """
    denom = n_total - k_groups
    if denom <= 0:
        return 0.0
    return float((h_stat - k_groups + 1) / denom)


def _plot_gof(df: pd.DataFrame, outfile: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(df))
    ax.bar(x - 0.2, df["observed"], width=0.4, label="Observed")
    ax.bar(x + 0.2, df["expected"], width=0.4, label="Expected")
    ax.set_xticks(x)
    ax.set_xticklabels(df["category"].astype(str))
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def _plot_contingency(cont: pd.DataFrame, outfile: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    mat = cont.to_numpy()
    im = ax.imshow(mat, aspect="auto")
    ax.set_xticks(np.arange(cont.shape[1]))
    ax.set_yticks(np.arange(cont.shape[0]))
    ax.set_xticklabels([str(c) for c in cont.columns])
    ax.set_yticklabels([str(i) for i in cont.index])
    ax.set_xlabel(cont.columns.name or "Column")
    ax.set_ylabel(cont.index.name or "Row")
    ax.set_title(title)

    # annotate cell counts
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, str(int(mat[i, j])), ha="center", va="center")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def _plot_boxplot(df: pd.DataFrame, outfile: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    groups = list(df["group"].cat.categories)
    data = [df.loc[df["group"] == g, "score"].to_numpy() for g in groups]
    ax_boxplot(ax, data, tick_labels=[str(g) for g in groups], showfliers=False)
    ax.set_xlabel("Group")
    ax.set_ylabel("Score")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def exercise_1_chi_square_gof(*, random_state: int = 123) -> ProblemResult:
    """
    Exercise 1: Chi-square goodness-of-fit.
    Observed category counts differ from a theoretical expected distribution.
    """
    rng = np.random.default_rng(random_state)

    categories = ["A", "B", "C", "D"]

    # Expected proportions: uniform
    n = 400
    expected = np.array([0.25, 0.25, 0.25, 0.25]) * n

    # Observed counts: intentionally biased away from uniform
    # (deterministic via multinomial draw)
    obs = rng.multinomial(n=n, pvals=[0.40, 0.20, 0.25, 0.15])

    df = pd.DataFrame(
        {"category": categories, "observed": obs.astype(int), "expected": expected.astype(int)}
    )

    chi2, p = chisquare(f_obs=df["observed"].to_numpy(), f_exp=df["expected"].to_numpy())

    summary = {
        "test": "chi_square_gof",
        "chi2": float(chi2),
        "p_value": float(p),
        "n": int(n),
        "categories": categories,
    }
    return ProblemResult("exercise_1_chi_square_gof", df, summary)


def exercise_2_chi_square_independence(*, random_state: int = 456) -> ProblemResult:
    """
    Exercise 2: Chi-square test of independence.
    Two categorical variables are associated (condition × outcome).
    """
    rng = np.random.default_rng(random_state)

    conditions = ["Control", "Treatment"]
    outcomes = ["No", "Yes"]

    # Strong association:
    # Control: mostly "No"
    # Treatment: mostly "Yes"
    n_per = 200
    control_yes = rng.binomial(n=n_per, p=0.30)
    treat_yes = rng.binomial(n=n_per, p=0.70)

    rows: list[dict[str, Any]] = []
    sid = 0

    def _append_block(cond: str, yes_count: int, total: int) -> None:
        nonlocal sid
        no_count = total - yes_count
        for _ in range(yes_count):
            sid += 1
            rows.append({"subject": f"S{sid:04d}", "condition": cond, "outcome": "Yes"})
        for _ in range(no_count):
            sid += 1
            rows.append({"subject": f"S{sid:04d}", "condition": cond, "outcome": "No"})

    _append_block("Control", int(control_yes), n_per)
    _append_block("Treatment", int(treat_yes), n_per)

    df = pd.DataFrame(rows)
    df["condition"] = pd.Categorical(df["condition"], categories=conditions, ordered=True)
    df["outcome"] = pd.Categorical(df["outcome"], categories=outcomes, ordered=True)

    cont = pd.crosstab(df["condition"], df["outcome"])
    chi2, p, dof, expected = chi2_contingency(cont.to_numpy(), correction=False)
    v = _cramers_v(cont)

    summary = {
        "test": "chi_square_independence",
        "chi2": float(chi2),
        "p_value": float(p),
        "dof": int(dof),
        "cramers_v": float(v),
        "observed": cont.to_dict(),
        "expected": pd.DataFrame(expected, index=cont.index, columns=cont.columns).to_dict(),
        "n": int(df.shape[0]),
    }
    return ProblemResult("exercise_2_chi_square_independence", df, summary)


def exercise_3_mwu_and_kruskal(*, random_state: int = 789) -> ProblemResult:
    """
    Exercise 3: Mann–Whitney U (2 groups) and Kruskal–Wallis (3 groups)
    using skewed distributions (lognormal) to mimic assumption violations.

    A < B < C in typical scores.
    """
    rng = np.random.default_rng(random_state)

    groups = ["A", "B", "C"]
    n = 90

    # Skewed (lognormal) with increasing location parameter
    a = rng.lognormal(mean=0.0, sigma=0.7, size=n)
    b = rng.lognormal(mean=0.5, sigma=0.7, size=n)
    c = rng.lognormal(mean=1.0, sigma=0.7, size=n)

    rows: list[dict[str, Any]] = []
    sid = 0

    def _add(g: str, arr: np.ndarray) -> None:
        nonlocal sid
        for val in arr:
            sid += 1
            rows.append({"subject": f"S{sid:04d}", "group": g, "score": float(val)})

    _add("A", a)
    _add("B", b)
    _add("C", c)

    df = pd.DataFrame(rows)
    df["group"] = pd.Categorical(df["group"], categories=groups, ordered=True)

    # Mann–Whitney U: A vs B
    ab = df[df["group"].isin(["A", "B"])].copy()
    x = ab.loc[ab["group"] == "A", "score"].to_numpy()
    y = ab.loc[ab["group"] == "B", "score"].to_numpy()
    u_stat, p_u = mannwhitneyu(x, y, alternative="two-sided")

    # Rank-biserial correlation (simple version):
    # RBC = 1 - 2U/(n1*n2) using U for group A vs B
    n1, n2 = len(x), len(y)
    rbc = float(1.0 - (2.0 * float(u_stat)) / (n1 * n2))

    # Kruskal–Wallis: A vs B vs C
    h_stat, p_kw = kruskal(a, b, c)
    eps2 = _epsilon_squared_kw(float(h_stat), n_total=3 * n, k_groups=3)

    medians = (
        df.groupby("group", observed=True)["score"]
        .median()
        .reset_index()
        .rename(columns={"score": "median_score"})
    )

    summary = {
        "test_mwu": {"u": float(u_stat), "p_value": float(p_u), "rank_biserial": float(rbc)},
        "test_kruskal": {"h": float(h_stat), "p_value": float(p_kw), "epsilon2": float(eps2)},
        "medians": medians.to_dict(orient="records"),
        "n_per_group": int(n),
    }
    return ProblemResult("exercise_3_mwu_and_kruskal", df, summary)


def _save_result(result: ProblemResult) -> None:
    _ensure_dirs()

    csv_path = SYNTHETIC_DATA_DIR / f"psych_ch19_{result.name}.csv"
    json_path = TRACK_C_OUTPUT_DIR / f"psych_ch19_{result.name}.json"
    plot_path = TRACK_C_OUTPUT_DIR / f"psych_ch19_{result.name}.png"

    result.data.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(result.summary, indent=2), encoding="utf-8")

    # Exercise-specific plots
    if result.name == "exercise_1_chi_square_gof":
        _plot_gof(result.data, plot_path, title=result.name)
    elif result.name == "exercise_2_chi_square_independence":
        cont = pd.crosstab(result.data["condition"], result.data["outcome"])
        _plot_contingency(cont, plot_path, title=result.name)
    else:
        _plot_boxplot(result.data, plot_path, title=result.name)


def main() -> None:
    """Run all Ch19 Track C exercises and save outputs."""
    results = [
        exercise_1_chi_square_gof(random_state=123),
        exercise_2_chi_square_independence(random_state=456),
        exercise_3_mwu_and_kruskal(random_state=789),
    ]

    for r in results:
        print(f"\n=== {r.name} ===")
        print(r.summary)
        _save_result(r)

    print("\nSaved:")
    print(f"- synthetic CSVs in: {SYNTHETIC_DATA_DIR}")
    print(f"- summaries/plots in: {TRACK_C_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
