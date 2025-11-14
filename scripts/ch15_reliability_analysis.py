# SPDX-License-Identifier: MIT
"""Chapter 15: Reliability Analysis

Case 1: Internal Consistency (Cronbach's Alpha)
Case 2: Test–Retest Reliability (ICC) with Bland–Altman plot
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Tuple

import matplotlib
# Use non-interactive backend for CI
matplotlib.use("Agg")
import pandas as pd
import pingouin as pg

from scripts._cli import apply_seed, base_parser




def _cronbach_alpha(df_items: pd.DataFrame) -> Tuple[float, Tuple[float, float]]:
    alpha, ci = pg.cronbach_alpha(data=df_items)
    return float(alpha), (float(ci[0]), float(ci[1]))


def _icc_both(df_long: pd.DataFrame) -> dict:
    """Compute ICC(3,1) and ICC(2,1); return values and CIs."""
    icc = (
        pg.intraclass_corr(
            data=df_long, targets="id", raters="day", ratings="measurement"
        )
        .set_index("Type")
        .loc[["ICC2", "ICC3"], ["ICC", "CI95%"]]
    )
    out = {}
    for typ in ("ICC2", "ICC3"):
        out[typ] = {
            "value": float(icc.loc[typ, "ICC"]),
            "ci95": [float(x) for x in icc.loc[typ, "CI95%"]],
        }
    return out


def main() -> int:
    parser = base_parser(
        description="Chapter 15 Analyzer: Reliability (Cronbach's Alpha & ICC)"
    )
    parser.add_argument(
        "--datadir",
        type=pathlib.Path,
        default=pathlib.Path("data/synthetic"),
        help="Directory with ch15_survey_items.csv and ch15_test_retest.csv",
    )
    args: argparse.Namespace = parser.parse_args()

    apply_seed(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)

    p_survey = args.datadir / "ch15_survey_items.csv"
    p_retest = args.datadir / "ch15_test_retest.csv"
    if not p_survey.exists() or not p_retest.exists():
        print(f"Error: Data files not found in {args.datadir}", file=sys.stderr)
        print("Run: python -m scripts.sim_ch15_reliability --outdir data/synthetic", file=sys.stderr)
        return 1

    df_survey = pd.read_csv(p_survey)
    df_retest = pd.read_csv(p_retest)

    # --- Analysis 1: Cronbach's Alpha ---
    item_cols = [c for c in df_survey.columns if c.startswith("q")]
    alpha_val, alpha_ci = _cronbach_alpha(df_survey[item_cols])

    # --- Analysis 2: ICC ---
    df_long = pd.melt(
        df_retest,
        id_vars="id",
        value_vars=["day1_jump", "day2_jump"],
        var_name="day",
        value_name="measurement",
    )
    icc_info = _icc_both(df_long)
    icc3 = icc_info["ICC3"]  # primary (sessions fixed)
    icc2 = icc_info["ICC2"]  # reference (sessions random)

    # --- Save JSON Summary ---
    summary = {
        "analysis_1_survey": {
            "statistic": "Cronbach's Alpha",
            "value": alpha_val,
            "ci95": [round(alpha_ci[0], 6), round(alpha_ci[1], 6)],
            "n_subjects": int(df_survey.shape[0]),
            "n_items": int(len(item_cols)),
        },
        "analysis_2_retest": {
            "primary": {
                "statistic": "ICC(3,1) Absolute Agreement",
                "value": round(icc3["value"], 6),
                "ci95": [round(icc3["ci95"][0], 6), round(icc3["ci95"][1], 6)],
            },
            "reference": {
                "statistic": "ICC(2,1) Absolute Agreement",
                "value": round(icc2["value"], 6),
                "ci95": [round(icc2["ci95"][0], 6), round(icc2["ci95"][1], 6)],
            },
            "n_subjects": int(df_retest.shape[0]),
        },
    }
    summary_path = args.outdir / "ch15_reliability_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Wrote: {summary_path}")



    # --- Bland–Altman Plot ---
    ax = pg.plot_blandaltman(df_retest["day1_jump"], df_retest["day2_jump"])
    fig = ax.get_figure()
    fig.set_size_inches(7, 5)
    ax.set_title(f"Bland–Altman (n={df_retest.shape[0]})")
    ax.set_xlabel("Average of Day 1 and Day 2")
    ax.set_ylabel("Difference (Day 2 - Day 1)")
    plot_path = args.outdir / "ch15_bland_altman.png"
    fig.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Wrote: {plot_path}")





    return 0


if __name__ == "__main__":
    sys.exit(main())
