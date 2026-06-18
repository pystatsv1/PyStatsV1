from __future__ import annotations

from pathlib import Path
from typing import Final, Sequence

import pandas as pd
import pingouin as pg

from scripts.psych_ch15_correlation import simulate_psych_correlation_dataset

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
OUTPUT_DIR: Final[Path] = ROOT / "outputs" / "track_b"


def compute_partial_corr(
    df: pd.DataFrame,
    x: str,
    y: str,
    covars: Sequence[str],
    method: str = "pearson",
) -> float:
    """Return the partial correlation coefficient r for x–y | covars."""
    result = pg.partial_corr(
        data=df,
        x=x,
        y=y,
        covar=list(covars),
        method=method,
    )
    return float(result["r"].iloc[0])


def run_partial_demo() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = simulate_psych_correlation_dataset(n=200, random_state=789)

    print("Chapter 15a partial correlation demo")
    print("------------------------------------")
    print("First 5 rows of the synthetic dataset:")
    print(df.head(), end="\n\n")

    # Zero-order correlation between study_hours and exam_score
    zero = pg.corr(df["study_hours"], df["exam_score"])
    r_zero = float(zero["r"].iloc[0])

    r_partial_stress = compute_partial_corr(
        df,
        x="study_hours",
        y="exam_score",
        covars=["stress"],
    )

    r_partial_stress_anxiety = compute_partial_corr(
        df,
        x="study_hours",
        y="exam_score",
        covars=["stress", "anxiety"],
    )

    summary = pd.DataFrame(
        {
            "model": [
                "zero-order",
                "partial | stress",
                "partial | stress, anxiety",
            ],
            "r": [r_zero, r_partial_stress, r_partial_stress_anxiety],
        }
    )

    print("Comparison of zero-order and partial correlations:")
    print(summary, end="\n\n")

    out_path = OUTPUT_DIR / "ch15a_partial_corr_summary.csv"
    summary.to_csv(out_path, index=False)
    print(f"Partial correlation summary saved to: {out_path}")


if __name__ == "__main__":
    run_partial_demo()
