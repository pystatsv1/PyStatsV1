from __future__ import annotations

from pathlib import Path

import pandas as pd


def test_intro_stats_dataset_shape_and_basic_effect_pattern() -> None:
    df = pd.read_csv(Path("data") / "intro_stats_scores.csv")
    assert set(df.columns) == {"id", "group", "score"}
    assert len(df) == 40

    group_means = df.groupby("group", as_index=False)["score"].mean()
    means = dict(zip(group_means["group"], group_means["score"]))

    # We expect treatment > control (by construction of the teaching dataset).
    assert means["treatment"] > means["control"]


def test_intro_stats_pack_files_exist() -> None:
    expected = [
        Path("scripts") / "intro_stats_01_descriptives.py",
        Path("scripts") / "intro_stats_02_simulation.py",
        Path("scripts") / "intro_stats_03_distributions_outliers.py",
        Path("scripts") / "intro_stats_04_confidence_intervals.py",
        Path("scripts") / "intro_stats_05_hypothesis_testing.py",
        Path("writeups") / "intro_stats_interpretation_template.md",
    ]
    for p in expected:
        assert p.exists(), f"Missing expected Intro Stats pack file: {p}"
