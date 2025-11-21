from pathlib import Path

import pandas as pd

from scripts import sim_psych_sleep_study as sim


def test_generate_sleep_study_reproducible():
    df1 = sim.generate_sleep_study(n=50, seed=123)
    df2 = sim.generate_sleep_study(n=50, seed=123)
    pd.testing.assert_frame_equal(df1, df2)


def test_generate_sleep_study_basic_properties():
    n = 120
    df = sim.generate_sleep_study(n=n, seed=42)

    # basic shape
    assert df.shape == (n, 5)
    assert list(df.columns) == [
        "id",
        "class_year",
        "sleep_hours",
        "study_method",
        "exam_score",
    ]

    # id is 1..n with no duplicates
    assert df["id"].is_unique
    assert df["id"].min() == 1
    assert df["id"].max() == n

    # sleep is within expected bounds
    assert float(df["sleep_hours"].min()) >= 4.0
    assert float(df["sleep_hours"].max()) <= 10.0

    # study methods limited to the defined set
    allowed = {"flashcards", "rereading", "practice_tests", "mixed"}
    assert set(df["study_method"].unique()).issubset(allowed)

    # exam scores between 40 and 100
    assert float(df["exam_score"].min()) >= 40.0
    assert float(df["exam_score"].max()) <= 100.0


def test_load_sleep_study_creates_csv(tmp_path: Path, monkeypatch):
    # Use a temporary directory so we don't touch the real data folder
    fake_csv = tmp_path / "psych_sleep_study.csv"

    # Monkeypatch the default path used by the module
    monkeypatch.setattr(sim, "SLEEP_CSV", fake_csv)

    # First call should create the file
    df = sim.load_sleep_study(path=fake_csv)
    assert fake_csv.exists()
    assert not df.empty

    # Second call should read the same data
    df2 = sim.load_sleep_study(path=fake_csv)
    pd.testing.assert_frame_equal(df, df2)
