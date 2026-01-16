"""Intro Stats case study pack (Part 2): simulation.

Beginners often ask: "If I repeated this class again, would I get the same
result?" This script answers that using simulation.

We compute the observed mean difference in score between groups and then use a
simple bootstrap (resampling with replacement) to approximate the sampling
variability of that difference.

Outputs are written under outputs/case_studies/intro_stats/.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "data" / "intro_stats_scores.csv"
    outdir = root / "outputs" / "case_studies" / "intro_stats"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    control = df.loc[df["group"] == "control", "score"].to_numpy(dtype=float)
    treatment = df.loc[df["group"] == "treatment", "score"].to_numpy(dtype=float)

    obs_diff = float(treatment.mean() - control.mean())

    rng = np.random.default_rng(123)
    n_boot = 2000

    boot_diffs = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        c = rng.choice(control, size=control.size, replace=True)
        t = rng.choice(treatment, size=treatment.size, replace=True)
        boot_diffs[b] = t.mean() - c.mean()

    lo, hi = np.percentile(boot_diffs, [2.5, 97.5])

    print("Intro Stats — simulation (bootstrap)")
    print("--------------------------------")
    print(f"Observed mean diff (treatment - control): {obs_diff:0.2f}")
    print(f"Bootstrap 95% CI: [{lo:0.2f}, {hi:0.2f}]")

    out_samples = outdir / "bootstrap_mean_diffs.csv"
    pd.DataFrame({"boot_mean_diff": boot_diffs}).to_csv(out_samples, index=False)

    out_summary = outdir / "bootstrap_summary.csv"
    pd.DataFrame(
        {
            "observed_mean_diff": [obs_diff],
            "ci_2_5": [lo],
            "ci_97_5": [hi],
            "n_boot": [n_boot],
            "seed": [123],
        }
    ).to_csv(out_summary, index=False)

    print("Saved:", out_samples)
    print("Saved:", out_summary)

    try:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(boot_diffs, bins=40)
        ax.axvline(obs_diff, linestyle="--")
        ax.set_title("Bootstrap distribution of mean difference")
        ax.set_xlabel("mean_diff (treatment - control)")
        ax.set_ylabel("count")

        out_png = outdir / "bootstrap_mean_diff_hist.png"
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print("Saved:", out_png)
    except Exception as e:  # pragma: no cover
        print("(Plot skipped)")
        print("Reason:", e)


if __name__ == "__main__":
    main()
