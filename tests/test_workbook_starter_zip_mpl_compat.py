"""Regression: workbook starter zip should be Matplotlib 3.9+ friendly.

The workbook starter is what students get when they run:

    pystatsv1 workbook init

Those extracted scripts must avoid Matplotlib's deprecated boxplot keyword
(`labels` renamed to `tick_labels`) so beginners don't see warnings and
Matplotlib 3.11 won't break them.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path


def test_workbook_starter_zip_includes_mpl_compat_helper() -> None:
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists(), f"Missing starter zip at: {zip_path}"

    with zipfile.ZipFile(zip_path, "r") as z:
        names = set(z.namelist())

    assert "scripts/_mpl_compat.py" in names


def test_workbook_starter_zip_has_no_legacy_boxplot_labels_calls() -> None:
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists(), f"Missing starter zip at: {zip_path}"

    # We only check the known scripts that use boxplots today.
    scripts = [
        "scripts/intro_stats_01_descriptives.py",
        "scripts/intro_stats_03_distributions_outliers.py",
        "scripts/psych_ch19_problem_set.py",
    ]

    # Detect any Axes.boxplot(... labels=...) usage.
    legacy_call = re.compile(r"\bboxplot\s*\(.*?\blabels\s*=", re.DOTALL)

    with zipfile.ZipFile(zip_path, "r") as z:
        for member in scripts:
            text = z.read(member).decode("utf-8")
            assert not legacy_call.search(text), f"Found legacy labels= call in {member}"
            assert "ax_boxplot" in text, f"Expected ax_boxplot wrapper in {member}"
