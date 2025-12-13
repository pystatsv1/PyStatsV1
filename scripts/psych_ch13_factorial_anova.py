"""
Track C – Chapter 13: Factorial Designs (Two-Way ANOVA) lab simulator.

Scenario
--------
Study Strategy (Flashcards vs Concept Mapping) x
Test Environment (Quiet vs Distracting) on standardized memory test scores.

This script:
- Simulates a 2x2 between-subjects factorial design.
- Writes a long-format CSV with one row per participant.
- Writes a small summary CSV with cell means and SDs.

Intended usage (from project root)
----------------------------------
python -m scripts.psych_ch13_factorial_anova \
    --n-per-cell 30 \
    --seed 123 \
    --outdir data/synthetic/psych_ch13
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CellSpec:
    study_strategy: str
    environment: str
    mean: float
    sd: float


CELL_SPECS: Tuple[CellSpec, ...] = (
    CellSpec("flashcards", "quiet", 78.0, 8.0),
    CellSpec("flashcards", "distracting", 70.0, 8.0),
    CellSpec("concept_mapping", "quiet", 88.0, 8.0),
    CellSpec("concept_mapping", "distracting", 75.0, 8.0),
)


def simulate_cell(cell: CellSpec, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Simulate n participants in a single cell."""
    scores = rng.normal(loc=cell.mean, scale=cell.sd, size=n)

    return pd.DataFrame(
        {
            "study_strategy": cell.study_strategy,
            "environment": cell.environment,
            "score": scores,
        }
    )


def simulate_factorial(n_per_cell: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    frames = [simulate_cell(spec, n_per_cell, rng) for spec in CELL_SPECS]
    df = pd.concat(frames, ignore_index=True)

    # Add a simple subject ID per row
    df.insert(0, "subject_id", np.arange(1, len(df) + 1))
    return df


def summarize_cells(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["study_strategy", "environment"], as_index=False)
        .agg(
            n=("score", "size"),
            mean_score=("score", "mean"),
            sd_score=("score", "std"),
        )
        .sort_values(["study_strategy", "environment"])
    )
    return grouped


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate a 2x2 factorial design (Study Strategy x Environment)."
    )
    parser.add_argument(
        "--n-per-cell",
        type=int,
        default=30,
        help="Number of participants per cell (default: 30).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=123,
        help="Random seed for reproducibility (default: 123).",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="data/synthetic/psych_ch13",
        help="Directory where CSV outputs will be saved.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = simulate_factorial(n_per_cell=args.n_per_cell, seed=args.seed)
    summary = summarize_cells(df)

    data_path = outdir / "psych_ch13_factorial_data.csv"
    summary_path = outdir / "psych_ch13_factorial_summary.csv"

    df.to_csv(data_path, index=False)
    summary.to_csv(summary_path, index=False)

    print("Track C – Chapter 13 factorial lab data written to:")
    print(f"  {data_path}")
    print(f"  {summary_path}")


if __name__ == "__main__":
    main()
