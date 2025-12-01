from __future__ import annotations

from pathlib import Path
from typing import Final

import pingouin as pg

from scripts.psych_ch15_correlation import simulate_psych_correlation_dataset

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
DATA_DIR: Final[Path] = ROOT / "data" / "synthetic"
OUTPUT_DIR: Final[Path] = ROOT / "outputs" / "track_b"


def compute_pairwise_corr(
    method: str = "pearson",
    padjust: str | None = None,
    n: int = 200,
    random_state: int = 456,
):
    """Return Pingouin pairwise_corr table for the Ch15 synthetic dataset.

    Parameters
    ----------
    method:
        Correlation method for Pingouin (e.g. "pearson", "spearman").
    padjust:
        Multiple-comparisons correction method (e.g. "none", "fdr_bh").
        If None, defaults to "none".
    n:
        Sample size for the synthetic dataset.
    random_state:
        Seed for the random number generator.

    Returns
    -------
    pandas.DataFrame
        One row per unique variable pair.
    """
    df = simulate_psych_correlation_dataset(n=n, random_state=random_state)
    padjust = padjust or "none"

    pairwise = pg.pairwise_corr(
        data=df,
        columns=df.columns,
        method=method,
        padjust=padjust,
    )
    return pairwise


def run_pairwise_demo() -> None:
    """Run a small demo and save outputs to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = simulate_psych_correlation_dataset(n=200, random_state=456)
    print("Chapter 15a pairwise correlation demo")
    print("-------------------------------------")
    print("First 5 rows of the synthetic dataset:")
    print(df.head(), end="\n\n")

    pairwise_pearson = compute_pairwise_corr(
        method="pearson",
        padjust="fdr_bh",
        n=200,
        random_state=456,
    )
    pairwise_spearman = compute_pairwise_corr(
        method="spearman",
        padjust="fdr_bh",
        n=200,
        random_state=456,
    )

    print("First 8 rows of Pearson pairwise correlations (FDR-corrected):")
    print(pairwise_pearson.head(8), end="\n\n")

    print("First 8 rows of Spearman pairwise correlations (FDR-corrected):")
    print(pairwise_spearman.head(8), end="\n\n")

    pearson_path = OUTPUT_DIR / "ch15a_pairwise_corr_pearson.csv"
    spearman_path = OUTPUT_DIR / "ch15a_pairwise_corr_spearman.csv"

    pairwise_pearson.to_csv(pearson_path, index=False)
    pairwise_spearman.to_csv(spearman_path, index=False)

    print(f"Pearson pairwise table saved to: {pearson_path}")
    print(f"Spearman pairwise table saved to: {spearman_path}")


if __name__ == "__main__":
    run_pairwise_demo()
