"""
Track C – Chapter 11 problem set (paired-samples t-test).

This script provides three synthetic exercises that mirror common
paired-samples scenarios:

1. A moderate training effect.
2. A small training effect.
3. No training effect (null effect).

Each exercise returns a ProblemResult bundling the raw data and the
paired-samples t-test results from `psych_ch11_paired_t`. The tests
call the exercise functions directly and the main() function writes
CSV files plus a compact summary table, similar to Chapter 12.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from pystatsv1.paths import (
    SYNTHETIC_DATA_DIR,
    TRACK_C_OUTPUT_DIR,
    ensure_dir,
)
from scripts.psych_ch11_paired_t import (
    PairedTResult,
    paired_t_test_from_wide,
    simulate_paired_training_study,
)

# Chapter-specific directories
CH11_SYNTHETIC_DIR = ensure_dir(SYNTHETIC_DATA_DIR / "psych_ch11")
CH11_OUTPUT_DIR = ensure_dir(TRACK_C_OUTPUT_DIR / "ch11")


@dataclass
class ProblemResult:
    """Container for a Chapter 11 problem-set exercise."""
    name: str
    data: pd.DataFrame
    result: PairedTResult


# ---------------------------------------------------------------------------
# Individual exercises
# ---------------------------------------------------------------------------


def exercise_moderate_effect(random_state: int = 11) -> ProblemResult:
    """Moderate pre–post improvement."""
    df = simulate_paired_training_study(
        n=30,
        mean_change=5.0,
        random_state=random_state,
    )
    result = paired_t_test_from_wide(df)
    return ProblemResult("moderate_effect", df, result)


def exercise_small_effect(random_state: int = 12) -> ProblemResult:
    """Small pre–post improvement (harder to detect)."""
    df = simulate_paired_training_study(
        n=30,
        mean_change=2.0,
        random_state=random_state,
    )
    result = paired_t_test_from_wide(df)
    return ProblemResult("small_effect", df, result)


def exercise_no_effect(random_state: int = 13) -> ProblemResult:
    """Null effect: mean change is zero."""
    df = simulate_paired_training_study(
        n=30,
        mean_change=0.0,
        random_state=random_state,
    )
    result = paired_t_test_from_wide(df)
    return ProblemResult("no_effect", df, result)


# ---------------------------------------------------------------------------
# Orchestrator used by tests and CLI
# ---------------------------------------------------------------------------


def generate_ch11_problem_set() -> List[ProblemResult]:
    """
    Run all Chapter 11 exercises and return their results.
    """
    return [
        exercise_moderate_effect(),
        exercise_small_effect(),
        exercise_no_effect(),
    ]


def _write_outputs(results: List[ProblemResult]) -> Path:
    """
    Write per-exercise CSVs and a single summary table.

    Returns
    -------
    summary_path : Path
        Location of the summary CSV file.
    """
    ensure_dir(CH11_SYNTHETIC_DIR)
    ensure_dir(CH11_OUTPUT_DIR)

    rows = []
    for idx, res in enumerate(results, start=1):
        csv_path = CH11_SYNTHETIC_DIR / f"psych_ch11_ex{idx}_{res.name}.csv"
        res.data.to_csv(csv_path, index=False)

        rows.append(
            {
                "exercise": res.name,
                "n": res.result.n,
                "t_stat": res.result.t_stat,
                "p_two_sided": res.result.p_value_two_sided,
                "mean_pre": res.result.mean_pre,
                "mean_post": res.result.mean_post,
                "mean_diff": res.result.mean_diff,
            }
        )

    summary = pd.DataFrame(rows)
    summary_path = CH11_OUTPUT_DIR / "ch11_problem_set_results.csv"
    summary.to_csv(summary_path, index=False)
    return summary_path


def main() -> None:
    results = generate_ch11_problem_set()
    summary_path = _write_outputs(results)

    print(f"Data for each exercise saved under: {CH11_SYNTHETIC_DIR}")
    print(f"Summary table saved to: {summary_path}")
    print("\nChapter 11 problem-set lab complete.")


if __name__ == "__main__":
    main()
