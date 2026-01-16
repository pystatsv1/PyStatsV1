from __future__ import annotations

from pathlib import Path

import pandas as pd


def test_intro_stats_dataset_contract() -> None:
    csv_path = Path("data/intro_stats_scores.csv")
    assert csv_path.exists(), "Missing data/intro_stats_scores.csv"

    df = pd.read_csv(csv_path)
    assert list(df.columns) == ["id", "group", "score"]
    assert df.isna().sum().sum() == 0

    counts = df["group"].value_counts().to_dict()
    assert counts == {"control": 20, "treatment": 20}

    means = df.groupby("group")["score"].mean().to_dict()
    assert means["treatment"] - means["control"] >= 8.0
