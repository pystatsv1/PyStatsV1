"""Regression tests for the workbook starter asset shipped via PyPI.

The workbook starter is a ZIP embedded as package data. These tests verify that the
ZIP contains a usable Makefile (no truncated placeholders, correct .PHONY lines),
so that `pystatsv1 workbook init` produces a good starter for students.
"""

from __future__ import annotations

import importlib.resources as resources
import zipfile

CHAPTERS = [10, 11, 12, 14, 15, 16, 17, 18, 19, 20]


def _read_from_zip(member: str) -> str:
    zip_trav = resources.files("pystatsv1.assets") / "workbook_starter.zip"
    with resources.as_file(zip_trav) as zip_path:
        with zipfile.ZipFile(zip_path) as zf:
            return zf.read(member).decode("utf-8")


def test_workbook_starter_makefile_is_not_truncated_or_mangled() -> None:
    makefile = _read_from_zip("Makefile")

    # The starter Makefile must not contain placeholder lines from earlier development.
    assert "\n...\n" not in makefile

    # Historically we had a bad escape/mangle like:
    #   .PHONY: psych-ch10-problems\psych-ch10-problems:
    assert "\\psych-" not in makefile

    # Sanity checks for expected targets.
    assert "PYTHON ?= python" in makefile
    assert ".PHONY: test" in makefile
    assert "test:" in makefile

    for ch in CHAPTERS:
        assert f".PHONY: psych-ch{ch}-problems" in makefile
        assert f"psych-ch{ch}-problems:" in makefile
        assert f".PHONY: test-ch{ch}" in makefile
        assert f"test-ch{ch}:" in makefile


def test_workbook_starter_readme_mentions_make_test() -> None:
    readme = _read_from_zip("README.md")
    assert "pystatsv1[workbook]" in readme
    assert (
    "make test" in readme
    or "pystatsv1 workbook" in readme
    or "pystatsv1 my-data" in readme
    )