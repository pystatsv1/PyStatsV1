# SPDX-License-Identifier: MIT
"""
Chapter 13 — Within-Subjects (Stroop): paired t-test vs. mixed model

Usage:
  python -m scripts.ch13_stroop_within --save-plots \
      --data data/synthetic/psych_stroop_trials.csv \
      --outdir outputs/ch13 --seed 123

Options:
  --data   Path to trial-level CSV (default: data/synthetic/psych_stroop_trials.csv)
  --outdir Where to write plots (default: outputs)
  --seed   RNG seed (not required; included for consistency across scripts)
  --min-rt 200 --max-rt 2000    # trial-level trims
"""

import argparse
import pathlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Safe for CI/headless environments
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm  # noqa: F401 (imported for users who inspect models)
import statsmodels.formula.api as smf
from scipy import stats


def load_trials(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["condition"] = df["condition"].astype("category")
    return df


def cohen_dz(a: pd.Series, b: pd.Series) -> float:
    """Within-subject effect size (dz) for paired data."""
    diff = a - b
    return float(diff.mean() / diff.std(ddof=1))


def main() -> None:
    ap = argparse.ArgumentParser(description="Paired t-test vs. mixed model on Stroop data")
    ap.add_argument(
        "--data",
        type=pathlib.Path,
        default=Path("data/synthetic/psych_stroop_trials.csv"),
        help="Path to trial-level CSV.",
    )
    ap.add_argument("--min-rt", type=float, default=200.0, help="Min RT (ms) to keep")
    ap.add_argument("--max-rt", type=float, default=2000.0, help="Max RT (ms) to keep")
    ap.add_argument("--save-plots", action="store_true", help="Save summary plots")
    ap.add_argument(
        "--outdir",
        type=pathlib.Path,
        default=Path("outputs"),
        help="Where to write plots (if --save-plots).",
    )
    # Included for CLI consistency; not used by the current analyses but harmless.
    ap.add_argument("--seed", type=int, default=None, help="RNG seed (optional)")
    args = ap.parse_args()

    # Optional seeding keeps behavior consistent with other scripts
    if args.seed is not None:
        np.random.seed(args.seed)

    # Ensure output directory exists when saving plots
    if args.save_plots:
        args.outdir.mkdir(parents=True, exist_ok=True)

    df = load_trials(args.data)

    # Keep correct trials and trim RTs
    before = len(df)
    df = df[(df["correct"] == 1) & (df["rt_ms"].between(args.min_rt, args.max_rt))].copy()
    print(
        f"Filtered: kept {len(df)}/{before} trials "
        f"(correct & {args.min_rt}-{args.max_rt} ms)"
    )

    # Log-transform RT (typical for skew)
    df["log_rt"] = np.log(df["rt_ms"])

    # Subject means per condition (paired t-test)
    subj_means = (
        df.groupby(["subject", "condition"], as_index=False, observed=False)["log_rt"]
        .mean()
    )
    wide = subj_means.pivot(index="subject", columns="condition", values="log_rt")

    # paired t-test (incongruent > congruent expected)
    tstat, pval = stats.ttest_rel(
        wide["incongruent"], wide["congruent"], nan_policy="omit"
    )
    dz = cohen_dz(wide["incongruent"], wide["congruent"])

    print("\n=== Paired t-test on subject means (log RT) ===")
    print(f"t = {tstat:.3f}, p = {pval:.3g}, Cohen's dz = {dz:.3f}")
    delta_ms = np.exp(wide["incongruent"].mean()) - np.exp(wide["congruent"].mean())
    print(f"Back-translated mean RT difference ≈ {delta_ms:.1f} ms (incongruent - congruent)")

    # Mixed model on trial-level log RT
    # random intercepts for subjects; (you can extend to random slopes)
    md = smf.mixedlm("log_rt ~ C(condition)", df, groups=df["subject"])
    m = md.fit(reml=False)
    print("\n=== Mixed Model (trial-level log RT) ===")
    print(m.summary())

    # Simple marginal means (back-transform)
    emmeans = df.groupby("condition", observed=False)["log_rt"].mean().apply(np.exp)
    print("\nEstimated marginal means (back-transformed ms):")
    for k, v in emmeans.items():
        print(f"  {k:<12} = {v:.1f} ms")

    # Plots
    if args.save_plots:
        # per-subject spaghetti of means
        plt.figure(figsize=(6, 4))
        for _, row in wide.iterrows():
            plt.plot([0, 1], [row["congruent"], row["incongruent"]], alpha=0.3)
        plt.xticks([0, 1], ["congruent", "incongruent"])
        plt.ylabel("Mean log RT")
        plt.title("Within-subject means (log RT)")
        plt.tight_layout()
        p1 = args.outdir / "ch13_stroop_subject_means.png"
        plt.savefig(p1, dpi=150)

        # violin/box of trial-level log RT by condition
        plt.figure(figsize=(6, 4))
        data_c = [df.loc[df["condition"] == c, "log_rt"].values for c in ["congruent", "incongruent"]]
        plt.violinplot(data_c, showmeans=True)
        plt.xticks([1, 2], ["congruent", "incongruent"])
        plt.ylabel("Trial log RT")
        plt.title("Trial-level distribution by condition")
        plt.tight_layout()
        p2 = args.outdir / "ch13_stroop_violins.png"
        plt.savefig(p2, dpi=150)

        print(f"Saved plots -> {p1}, {p2}")


if __name__ == "__main__":
    main()
