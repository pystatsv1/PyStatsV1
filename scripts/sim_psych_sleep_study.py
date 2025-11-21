"""Synthetic psychology datasets for Track B labs.

This module generates small, deterministic datasets for the
introductory psychology labs (sleep study, study methods, etc.).

It follows the existing PyStatsV1 pattern:

* pure-Python functions that return pandas DataFrames
* a stable random seed so tests and docs stay in sync
* CSVs stored under ``data/synthetic`` for quick loading

The guiding use-case is Chapter 4 of the psychology track,
where students look at the distribution of sleep duration and
the frequency of different study methods.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "synthetic"
SLEEP_CSV = DATA_DIR / "psych_sleep_study.csv"

StudyMethod = Literal["flashcards", "rereading", "practice_tests", "mixed"]


def _rng(seed: int | np.random.Generator = 42) -> np.random.Generator:
    """Return a NumPy random generator.

    Accepts either an integer seed or an existing Generator so that tests
    can pass in their own RNG if desired.
    """
    if isinstance(seed, np.random.Generator):
        return seed
    return np.random.default_rng(seed)


# ---------------------------------------------------------------------
# Core generator
# ---------------------------------------------------------------------


def generate_sleep_study(
    n: int = 120,
    *,
    seed: int | np.random.Generator = 42,
) -> pd.DataFrame:
    """Generate a synthetic 'sleep and exam' dataset.

    Columns
    -------
    id : int
        Participant ID (1..n).
    class_year : {"first_year", "second_year", "third_year", "fourth_year"}
    sleep_hours : float
        Average weeknight sleep in hours (roughly 4–10).
    study_method : StudyMethod
        Primary reported study strategy.
    exam_score : float
        Exam percentage (0–100), weakly related to sleep and method.

    Notes
    -----
    The relationships are intentionally simple:

    * students using practice tests score a bit higher on average;
    * extremely short sleep (< 6 hours) is associated with slightly
      lower exam scores;
    * random noise is added so patterns are realistic but not perfect.
    """
    rng = _rng(seed)

    ids = np.arange(1, n + 1)

    class_years = rng.choice(
        ["first_year", "second_year", "third_year", "fourth_year"],
        size=n,
        p=[0.30, 0.30, 0.25, 0.15],
    )

    # Base sleep: around 7.2 hours with some spread
    sleep = rng.normal(loc=7.2, scale=0.9, size=n)
    # Truncate to [4, 10]
    sleep = np.clip(sleep, 4.0, 10.0)

    study_methods: list[StudyMethod] = list(
        rng.choice(
            ["flashcards", "rereading", "practice_tests", "mixed"],
            size=n,
            p=[0.30, 0.25, 0.30, 0.15],
        )
    )

    # Exam score model:
    #   baseline 78
    #   + sleep_effect * (sleep - 7)
    #   + method_effect
    #   + random noise
    baseline = 78.0
    sleep_effect = 1.8  # every extra hour above 7 adds ~1.8 points

    method_effect_map = {
        "flashcards": 1.0,
        "rereading": -1.5,
        "practice_tests": 3.0,
        "mixed": 0.5,
    }

    method_effect = np.array([method_effect_map[m] for m in study_methods])
    noise = rng.normal(loc=0.0, scale=5.0, size=n)

    exam = baseline + sleep_effect * (sleep - 7.0) + method_effect + noise
    # Clamp to [40, 100] so scores stay plausible
    exam = np.clip(exam, 40.0, 100.0)

    df = pd.DataFrame(
        {
            "id": ids,
            "class_year": class_years,
            "sleep_hours": np.round(sleep, 2),
            "study_method": study_methods,
            "exam_score": np.round(exam, 1),
        }
    )

    return df


# ---------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------


def write_sleep_study_csv(
    path: Path | str = SLEEP_CSV, *, n: int = 120, seed: int = 42
) -> Path:
    """Generate the sleep study and save it as a CSV file.

    Returns the path to the written file. Parent directories are created
    if needed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_sleep_study(n=n, seed=seed)
    df.to_csv(path, index=False)
    return path


def load_sleep_study(path: Path | str = SLEEP_CSV) -> pd.DataFrame:
    """Load the sleep study CSV, generating it if missing.

    This keeps the workflow simple for students::

        from scripts.sim_psych_sleep_study import load_sleep_study
        df = load_sleep_study()
        df.head()

    When the repository is cloned fresh, the first call will create
    ``data/synthetic/psych_sleep_study.csv`` using the default generator.
    Subsequent calls simply read the cached CSV.
    """
    path = Path(path)
    if not path.exists():
        write_sleep_study_csv(path)
    return pd.read_csv(path)
