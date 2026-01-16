"""Intro Stats 4 — Confidence intervals (formula + bootstrap).

Computes two 95% confidence intervals (CIs) for the *difference in means*
(treatment minus control):

1) Welch t-based CI (classic, formula-based)
2) Bootstrap percentile CI (simulation-based)

Also writes a per-group mean CI table and saves a quick plot showing those group
mean CIs.

Inputs
------
- data/intro_stats_scores.csv

Outputs
-------
All outputs go to outputs/case_studies/intro_stats/ by default:

- ci_mean_diff_welch_95.csv
- ci_mean_diff_bootstrap_95.csv
- ci_group_means_95.csv
- ci_group_means_95.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as st

DEFAULT_CSV = Path("data") / "intro_stats_scores.csv"
DEFAULT_OUTDIR = Path("outputs") / "case_studies" / "intro_stats"


def _welch_ci_mean_diff_95(control: np.ndarray, treatment: np.ndarray) -> dict[str, float]:
    """Welch t-based 95% CI for (mean(treatment) - mean(control))."""
    n_c = int(control.size)
    n_t = int(treatment.size)
    mean_c = float(control.mean())
    mean_t = float(treatment.mean())
    diff = mean_t - mean_c

    var_c = float(control.var(ddof=1))
    var_t = float(treatment.var(ddof=1))

    se2 = var_t / n_t + var_c / n_c
    se = float(np.sqrt(se2))

    # Welch–Satterthwaite df
    num = se2**2
    den = (var_t / n_t) ** 2 / (n_t - 1) + (var_c / n_c) ** 2 / (n_c - 1)
    df = float(num / den)

    tcrit = float(st.t.ppf(0.975, df=df))
    ci_low = diff - tcrit * se
    ci_high = diff + tcrit * se

    return {
        "n_control": float(n_c),
        "n_treatment": float(n_t),
        "mean_control": mean_c,
        "mean_treatment": mean_t,
        "mean_diff": diff,
        "se": se,
        "df": df,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
    }


def _group_mean_cis_95(df: pd.DataFrame) -> pd.DataFrame:
    """Per-group 95% t CIs for the group means."""
    rows: list[dict[str, object]] = []
    for group, gdf in df.groupby("group", sort=True):
        x = gdf["score"].astype(float).to_numpy()
        n = int(x.size)
        mean = float(x.mean())
        sd = float(x.std(ddof=1))
        se = sd / float(np.sqrt(n))
        tcrit = float(st.t.ppf(0.975, df=n - 1))
        ci_low = mean - tcrit * se
        ci_high = mean + tcrit * se
        rows.append(
            {
                "group": str(group),
                "n": n,
                "mean": mean,
                "sd": sd,
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
            }
        )
    return pd.DataFrame(rows)


def _bootstrap_ci_mean_diff_95(
    control: np.ndarray,
    treatment: np.ndarray,
    *,
    n_boot: int,
    seed: int,
) -> dict[str, float]:
    """Bootstrap percentile 95% CI for (mean(treatment) - mean(control))."""
    rng = np.random.default_rng(seed)
    n_c = int(control.size)
    n_t = int(treatment.size)

    diffs = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        c = rng.choice(control, size=n_c, replace=True)
        t = rng.choice(treatment, size=n_t, replace=True)
        diffs[i] = float(t.mean() - c.mean())

    ci_low, ci_high = np.percentile(diffs, [2.5, 97.5]).astype(float)
    return {
        "n_control": float(n_c),
        "n_treatment": float(n_t),
        "mean_diff": float(treatment.mean() - control.mean()),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n_boot": float(n_boot),
        "seed": float(seed),
    }


def _plot_group_mean_cis(group_cis: pd.DataFrame, out_png: Path) -> None:
    groups = group_cis["group"].astype(str).tolist()
    means = group_cis["mean"].astype(float).to_numpy()
    lows = group_cis["ci_low"].astype(float).to_numpy()
    highs = group_cis["ci_high"].astype(float).to_numpy()

    x = np.arange(len(groups))
    yerr = np.vstack([means - lows, highs - means])

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.errorbar(x, means, yerr=yerr, fmt="o", capsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Score")
    ax.set_title("Group means with 95% CIs")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Intro Stats 4: Confidence intervals")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--n-boot", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    if set(df.columns) != {"id", "group", "score"}:
        raise ValueError("Expected columns: id, group, score")

    control = df.loc[df["group"] == "control", "score"].astype(float).to_numpy()
    treatment = df.loc[df["group"] == "treatment", "score"].astype(float).to_numpy()
    if control.size == 0 or treatment.size == 0:
        raise ValueError("Expected groups 'control' and 'treatment' with non-empty scores")

    args.outdir.mkdir(parents=True, exist_ok=True)

    # 1) Welch CI for mean difference
    welch = _welch_ci_mean_diff_95(control, treatment)
    out_welch = args.outdir / "ci_mean_diff_welch_95.csv"
    pd.DataFrame([welch]).to_csv(out_welch, index=False)

    # 2) Bootstrap CI for mean difference
    boot = _bootstrap_ci_mean_diff_95(control, treatment, n_boot=args.n_boot, seed=args.seed)
    out_boot = args.outdir / "ci_mean_diff_bootstrap_95.csv"
    pd.DataFrame([boot]).to_csv(out_boot, index=False)

    # 3) Group mean CIs + plot
    group_cis = _group_mean_cis_95(df)
    out_group_csv = args.outdir / "ci_group_means_95.csv"
    group_cis.to_csv(out_group_csv, index=False)

    out_group_png = args.outdir / "ci_group_means_95.png"
    _plot_group_mean_cis(group_cis, out_group_png)

    print("Saved:", out_welch)
    print("Saved:", out_boot)
    print("Saved:", out_group_csv)
    print("Saved:", out_group_png)


if __name__ == "__main__":
    main()
