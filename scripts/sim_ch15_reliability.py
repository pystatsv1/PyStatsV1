# SPDX-License-Identifier: MIT
"""Chapter 15 Simulator: Reliability & Psychometrics

Case 1 (Psych/Soc): Internal Consistency (Cronbach's Alpha)
Case 2 (Sports/Fitness): Test–Retest Reliability (ICC)

Generates two CSV files into --outdir:
- ch15_survey_items.csv (id, q1..q10)
- ch15_test_retest.csv (id, day1_jump, day2_jump)
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser


def simulate_survey_data(
    rng: np.random.Generator, n_subjects: int = 100, n_items: int = 10
) -> pd.DataFrame:
    """Simulate Likert-scale survey with a single underlying factor."""
    cov = np.full((n_items, n_items), 0.5, dtype=float)
    np.fill_diagonal(cov, 1.0)
    scores = rng.multivariate_normal(mean=np.zeros(n_items), cov=cov, size=n_subjects)

    # Convert to 1–5 Likert
    likert = np.floor(scores * 1.5 + 3.5)
    likert = np.clip(likert, 1, 5).astype(int)

    cols = {f"q{i+1}": likert[:, i] for i in range(n_items)}
    df = pd.DataFrame(cols)
    df["id"] = np.arange(1, n_subjects + 1)
    return df[["id"] + [f"q{i+1}" for i in range(n_items)]]


def simulate_retest_data(
    rng: np.random.Generator, n_subjects: int = 30, icc_true: float = 0.85
) -> pd.DataFrame:
    """Simulate Day1/Day2 device readings targeting a given ICC."""
    # True score variance = 10^2 = 100
    var_true = 100.0
    var_error = var_true * (1.0 - icc_true) / icc_true  # algebra from ICC = vt/(vt+ve)
    sd_error = float(np.sqrt(var_error))

    true_score = rng.normal(loc=50.0, scale=np.sqrt(var_true), size=n_subjects)
    day1 = true_score + rng.normal(loc=0.0, scale=sd_error, size=n_subjects)
    day2 = true_score + rng.normal(loc=0.0, scale=sd_error, size=n_subjects)

    return pd.DataFrame(
        {"id": np.arange(1, n_subjects + 1), "day1_jump": day1, "day2_jump": day2}
    )


def main() -> int:
    parser = base_parser(
        description="Chapter 15 Simulator: Reliability (Cronbach's Alpha & ICC)"
    )
    parser.add_argument(
        "--n-survey",
        type=int,
        default=150,
        help="Number of subjects for the survey (Cronbach's Alpha).",
    )
    parser.add_argument(
        "--n-retest",
        type=int,
        default=40,
        help="Number of subjects for the test–retest (ICC).",
    )
    args: argparse.Namespace = parser.parse_args()

    apply_seed(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    # Survey
    df_survey = simulate_survey_data(rng, n_subjects=args.n_survey)
    p_survey = args.outdir / "ch15_survey_items.csv"
    df_survey.to_csv(p_survey, index=False)

    # Test–retest
    df_retest = simulate_retest_data(rng, n_subjects=args.n_retest)
    p_retest = args.outdir / "ch15_test_retest.csv"
    df_retest.to_csv(p_retest, index=False)

    # Meta
    meta = {
        "simulation": "ch15_reliability",
        "seed": args.seed,
        "survey_params": {"n_subjects": args.n_survey, "n_items": 10},
        "retest_params": {"n_subjects": args.n_retest, "target_icc": 0.85},
    }
    (args.outdir / "ch15_reliability_meta.json").write_text(
        json.dumps(meta, indent=2)
    )

    print(f"Wrote: {p_survey}")
    print(f"Wrote: {p_retest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())