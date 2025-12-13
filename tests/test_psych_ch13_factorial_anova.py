"""Tests for the Track C Chapter 13 factorial ANOVA simulator."""

from pathlib import Path

import pandas as pd

from scripts import psych_ch13_factorial_anova as ch13


def test_simulate_factorial_shape_and_reproducibility(tmp_path: Path) -> None:
    """Simulated data should have 4 * n_per_cell rows and be reproducible."""
    n_per_cell = 10
    seed = 42

    df1 = ch13.simulate_factorial(n_per_cell=n_per_cell, seed=seed)
    df2 = ch13.simulate_factorial(n_per_cell=n_per_cell, seed=seed)

    # 4 cells * n_per_cell rows
    assert df1.shape[0] == 4 * n_per_cell

    # Same data for same seed
    pd.testing.assert_frame_equal(df1, df2)

    # Means should respect ordering of cell specs
    summary = ch13.summarize_cells(df1)
    assert set(summary["study_strategy"]) == {"flashcards", "concept_mapping"}
    assert set(summary["environment"]) == {"quiet", "distracting"}
