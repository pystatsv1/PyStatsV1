# SPDX-License-Identifier: MIT
"""
Simulate data for Chapter 14: Two-Sample (Welch's) t-test
Education Case Study: Control vs. Tutoring Group

Generates a CSV file with student scores from two independent groups.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import numpy as np
import pandas as pd

from scripts._cli import base_parser, apply_seed


def main() -> None:
    """
    Generates a CSV of simulated student scores (Control vs. Tutor)
    and a _meta.json file describing the simulation parameters.
    """
    parser = base_parser("Chapter 14 Simulator: A/B Tutoring Study (Welch's t-test)")
    parser.add_argument(
        "--n-per-group",
        type=int,
        default=50,
        help="Number of students per group (Control, Tutor)",
    )
    parser.add_argument(
        "--mu-control",
        type=float,
        default=70.0,
        help="Mean score for the Control group",
    )
    parser.add_argument(
        "--mu-tutor",
        type=float,
        default=75.0,
        help="Mean score for the Tutoring group",
    )
    parser.add_argument(
        "--sd-control",
        type=float,
        default=10.0,
        help="Standard deviation for the Control group",
    )
    parser.add_argument(
        "--sd-tutor",
        type=float,
        default=12.0,
        help="Standard deviation for the Tutoring group (unequal variance)",
    )
    args = parser.parse_args()

    # Setup
    apply_seed(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    # Data generation
    control_scores = rng.normal(
        loc=args.mu_control, scale=args.sd_control, size=args.n_per_group
    )
    tutor_scores = rng.normal(
        loc=args.mu_tutor, scale=args.sd_tutor, size=args.n_per_group
    )

    # Tidy frame
    df = pd.DataFrame(
        {
            "id": np.arange(1, (args.n_per_group * 2) + 1),
            "group": np.repeat(["Control", "Tutor"], args.n_per_group),
            "score": np.concatenate([control_scores, tutor_scores]),
        }
    )

    # Artifacts
    data_path = args.outdir / "ch14_tutoring_data.csv"
    meta_path = args.outdir / "ch14_tutoring_meta.json"

    df.to_csv(data_path, index=False)

    meta: dict[str, Any] = {
        "simulation": "ch14_tutoring_ab",
        "n_per_group": int(args.n_per_group),
        "total_n": int(df.shape[0]),
        "seed": int(args.seed) if args.seed is not None else None,
        "dgp_params": {
            "control": {"mean": float(args.mu_control), "sd": float(args.sd_control)},
            "tutor": {"mean": float(args.mu_tutor), "sd": float(args.sd_tutor)},
        },
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {df.shape[0]} rows → {data_path}")
    print(f"Wrote meta → {meta_path}")


if __name__ == "__main__":
    main()
