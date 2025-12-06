"""
Tests for Chapter 10 Track C problem set – independent-samples t-test.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.psych_ch10_problem_set import (
    DATA_DIR,
    OUTPUT_DIR,
    exercise_1_large_sample,
    exercise_2_small_sample,
    exercise_3_large_effect,
    run_independent_t,
    simulate_independent_t_dataset,
)


def test_simulate_independent_t_dataset_structure() -> None:
    """Simulated dataset has the expected size and columns."""
    df = simulate_independent_t_dataset(
        n_per_group=15,
        effect_size=0.5,
        random_state=123,
    )

    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {"group", "score"}
    assert len(df) == 30
    assert set(df["group"].unique()) == {"control", "treatment"}


def test_exercise_1_detects_effect() -> None:
    """Exercise 1 should detect a moderate treatment effect."""
    result = exercise_1_large_sample()
    df = result.data
    t_table = run_independent_t(df)
    row = t_table.iloc[0]

    p_val = float(row["p-val"])
    d = float(row["cohen-d"])

    mean_control = float(
        df.loc[df["group"] == "control", "score"].mean(),
    )
    mean_treatment = float(
        df.loc[df["group"] == "treatment", "score"].mean(),
    )

    # Moderate effect size and treatment > control.
    assert d > 0.4
    assert mean_treatment > mean_control
    assert p_val < 0.05


def test_exercise_2_and_3_outputs_created(tmp_path: Path) -> None:
    """
    Running exercises 2 and 3 should produce sensible t-tests and
    allow saving of data / outputs.
    """
    # Run the exercises
    result2 = exercise_2_small_sample()
    result3 = exercise_3_large_effect()

    # Basic sanity checks on t-test results
    for result in (result2, result3):
        t_table = run_independent_t(result.data)
        row = t_table.iloc[0]
        float(row["p-val"])
        float(row["cohen-d"])
        assert "p-val" in t_table.columns
        assert "cohen-d" in t_table.columns

    # Check that the data directory is ready for saving CSVs.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Try saving one CSV to ensure path is valid.
    out_csv = DATA_DIR / "psych_ch10_test_write.csv"
    result2.data.to_csv(out_csv, index=False)
    assert out_csv.exists()
