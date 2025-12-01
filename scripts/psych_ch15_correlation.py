# scripts/psych_ch15_correlation.py

from __future__ import annotations

from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import seaborn as sns


ROOT: Final[Path] = Path(__file__).resolve().parents[1]
DATA_DIR: Final[Path] = ROOT / "data" / "synthetic"
OUTPUT_DIR: Final[Path] = ROOT / "outputs" / "track_b"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def simulate_bivariate_correlation(
    n: int = 120,
    rho: float = 0.5,
    random_state: int | None = 123,
) -> pd.DataFrame:
    """Simulate a bivariate normal sample with a known population correlation.

    Parameters
    ----------
    n:
        Sample size.
    rho:
        Population correlation between X and Y (must be between -1 and 1).
    random_state:
        Seed for the NumPy random number generator (for reproducibility).

    Returns
    -------
    pandas.DataFrame
        DataFrame with two columns: ``"x"`` and ``"y"``.
    """
    if not (-1.0 <= rho <= 1.0):
        raise ValueError("rho must be between -1 and 1.")

    rng = np.random.default_rng(random_state)
    mean = np.array([0.0, 0.0])
    cov = np.array([[1.0, rho], [rho, 1.0]])

    x, y = rng.multivariate_normal(mean, cov, size=n).T
    df = pd.DataFrame({"x": x, "y": y})
    return df


def pingouin_pearsonr(df: pd.DataFrame, x: str, y: str) -> float:
    """Return Pearson's r estimated by Pingouin for columns x and y.

    This is a tiny wrapper used by the unit tests to compare NumPy and
    Pingouin implementations.
    """
    corr_table = pg.corr(df[x], df[y], method="pearson")
    # Pingouin returns a 1-row DataFrame; the "r" column holds the estimate.
    return float(corr_table["r"].iloc[0])


def simulate_psych_correlation_dataset(
    n: int = 200,
    random_state: int | None = 123,
) -> pd.DataFrame:
    """Simulate a small psychology-style dataset with correlated variables.

    Columns
    -------
    stress:
        Higher values = more stress.
    sleep_hours:
        Fewer hours tend to go with higher stress.
    anxiety:
        Positively related to stress, negatively to sleep_hours.
    study_hours:
        More studying is mildly associated with less stress and more sleep.
    exam_score:
        Higher for students who study more and sleep more, lower for stress.
    """
    rng = np.random.default_rng(random_state)

    # Base latent variable driving several measures (e.g., "overall strain")
    strain = rng.normal(loc=0.0, scale=1.0, size=n)

    # Stress is mostly strain plus noise
    stress = 50 + 10 * strain + rng.normal(0.0, 5.0, size=n)

    # Sleep goes down as strain goes up
    sleep_hours = 7.5 - 0.4 * strain + rng.normal(0.0, 0.6, size=n)

    # Anxiety is strongly positively associated with strain
    anxiety = 40 + 8 * strain + rng.normal(0.0, 4.0, size=n)

    # Study hours: mildly *negatively* related to strain (stressed students study less)
    study_hours = 10 - 0.7 * strain + rng.normal(0.0, 1.0, size=n)

    # Exam score: better with more study and sleep, worse with more stress
    exam_score = (
        60
        + 2.2 * study_hours
        + 1.5 * sleep_hours
        - 0.3 * (stress - 50)
        + rng.normal(0.0, 5.0, size=n)
    )

    df = pd.DataFrame(
        {
            "stress": stress,
            "sleep_hours": sleep_hours,
            "anxiety": anxiety,
            "study_hours": study_hours,
            "exam_score": exam_score,
        }
    )
    return df


def run_lab() -> None:
    """Run the Chapter 15 correlation lab demo and print/save outputs."""
    # ------------------------------------------------------------------
    # 1) Bivariate simulation with known population correlation
    # ------------------------------------------------------------------
    print("Bivariate correlation demo")
    print("--------------------------")

    df_xy = simulate_bivariate_correlation(n=120, rho=0.5, random_state=123)
    print("First 5 rows of simulated data (x, y):")
    print(df_xy.head())

    r_np = np.corrcoef(df_xy["x"], df_xy["y"])[0, 1]
    r_pg = pingouin_pearsonr(df_xy, "x", "y")

    print(f"\nNumPy correlation r_np    = {r_np: .3f}")
    print(f"Pingouin correlation r_pg = {r_pg: .3f}")
    print("Difference (r_pg - r_np)  = {:.6f}".format(r_pg - r_np))

    bivariate_path = DATA_DIR / "psych_ch15_bivariate_correlation.csv"
    df_xy.to_csv(bivariate_path, index=False)
    print(f"\nBivariate data saved to: {bivariate_path}")

    # ------------------------------------------------------------------
    # 2) Psychology-style dataset with several correlated variables
    # ------------------------------------------------------------------
    print("\nPsychological variables correlation demo")
    print("----------------------------------------")

    df_psych = simulate_psych_correlation_dataset(n=200, random_state=456)
    print("First 5 rows of psych dataset:")
    print(df_psych.head())

    corr_matrix = df_psych.corr()
    print("\nCorrelation matrix (pandas):")
    print(corr_matrix.round(2))

    # Pairwise correlations with Pingouin (gives p-values, CI, etc.)
    pairwise_corr = pg.pairwise_corr(
        data=df_psych,
        columns=df_psych.columns,
        method="pearson",
    )

    print("\nPingouin pairwise correlations (first 10 rows):")
    print(pairwise_corr.head(10))

    # Save data and correlation table
    psych_path = DATA_DIR / "psych_ch15_correlation.csv"
    df_psych.to_csv(psych_path, index=False)

    pairwise_path = OUTPUT_DIR / "ch15_pairwise_corr.csv"
    pairwise_corr.to_csv(pairwise_path, index=False)

    print(f"\nPsych data saved to: {psych_path}")
    print(f"Pairwise correlation table saved to: {pairwise_path}")

    # ------------------------------------------------------------------
    # 3) Heatmap of the correlation matrix
    # ------------------------------------------------------------------
    heatmap_path = OUTPUT_DIR / "ch15_corr_heatmap.png"
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        square=True,
        cbar=True,
    )
    plt.title("Chapter 15 – Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=150)
    plt.close()
    print(f"Correlation heatmap saved to: {heatmap_path}")

    # ------------------------------------------------------------------
    # 4) Example partial correlation
    # ------------------------------------------------------------------
    print("\nPartial correlation example:")
    print("Exam score ~ Study hours, controlling for motivation (proxy = stress).")

    partial = pg.partial_corr(
        data=df_psych,
        x="study_hours",
        y="exam_score",
        covar="stress",
        method="pearson",
    )
    print(partial)

    print("\nChapter 15 correlation lab complete.")


def main() -> None:
    run_lab()


if __name__ == "__main__":
    main()
