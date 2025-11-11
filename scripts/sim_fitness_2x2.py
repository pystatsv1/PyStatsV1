# SPDX-License-Identifier: MIT
"""
Simulate a 2x2 mixed design (Group between × Time within) fitness study.
Creates in --outdir (default: data/synthetic):
  fitness_subjects.csv
  fitness_long.csv
  fitness_meta.json
"""

import argparse
import json
import time
import pathlib
from pathlib import Path

import numpy as np
import pandas as pd

# Defaults
DEFAULT_SEED = 7
GROUPS = ["ProgramA", "ProgramB"]
N_PER_GROUP_DEFAULT = 40  # total N = n_per_group * 2


def simulate(
    n_per_group: int = N_PER_GROUP_DEFAULT,
    seed: int = DEFAULT_SEED,
    outdir: Path = Path("data/synthetic"),
):
    """Simulates a simple strength-training experiment and writes CSV/JSON to outdir."""
    rng = np.random.default_rng(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    n_total = n_per_group * len(GROUPS)

    subjects = pd.DataFrame(
        {
            "id": np.arange(1, n_total + 1),
            "group": rng.choice(GROUPS, size=n_total, replace=True),
            "age": rng.integers(18, 45, size=n_total),  # 18..44
            "sex": rng.choice(["F", "M"], size=n_total, p=[0.5, 0.5]),
            "bmi": rng.normal(24, 3.5, size=n_total).clip(17, 38),
        }
    )

    # Baseline strength with small covariate effects
    base = (
        80
        + 0.8 * (subjects["age"] - 30)
        + 1.2 * (subjects["bmi"] - 24)
        + rng.normal(0, 8, size=n_total)
    )

    # Program gains (B > A on average)
    gain_A = rng.normal(8, 4, size=n_total)
    gain_B = rng.normal(12, 4, size=n_total)
    gain = np.where(subjects["group"].to_numpy() == "ProgramA", gain_A, gain_B)

    long = pd.concat(
        [
            pd.DataFrame(
                {
                    "id": subjects["id"],
                    "time": "pre",
                    "strength": base + rng.normal(0, 3, size=n_total),
                }
            ),
            pd.DataFrame(
                {
                    "id": subjects["id"],
                    "time": "post",
                    "strength": base + gain + rng.normal(0, 3, size=n_total),
                }
            ),
        ],
        ignore_index=True,
    ).merge(subjects, on="id")

    # Write artifacts
    subjects_path = outdir / "fitness_subjects.csv"
    long_path = outdir / "fitness_long.csv"
    subjects.to_csv(subjects_path, index=False)
    long.to_csv(long_path, index=False)

    meta = dict(
        seed=seed,
        n=int(n_total),
        n_per_group=int(n_per_group),
        design="2x2 mixed (Group between × Time within)",
        programs=GROUPS,
        dv="strength_1RM_like",
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    meta_path = outdir / "fitness_meta.json"
    with meta_path.open("w") as f:
        json.dump(meta, f, indent=2)

    print(f"Wrote {subjects_path}, {long_path}, {meta_path}")
    return subjects, long


def main():
    ap = argparse.ArgumentParser(description="Simulate mixed-design fitness study data")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED, help="RNG seed")
    ap.add_argument(
        "--n-per-group",
        type=int,
        default=N_PER_GROUP_DEFAULT,
        help="Number of subjects per program",
    )
    ap.add_argument(
        "--outdir",
        type=pathlib.Path,
        default=Path("data/synthetic"),
        help="Where to write outputs (CSV/JSON).",
    )
    args = ap.parse_args()

    simulate(n_per_group=args.n_per_group, seed=args.seed, outdir=args.outdir)


if __name__ == "__main__":
    main()
