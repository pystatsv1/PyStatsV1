from __future__ import annotations

import re
import zipfile
from pathlib import Path


def test_track_d_chapter_index_lists_all_runs_and_commands() -> None:
    """Guardrail: the chapter index should stay in sync with the packaged Track D workbook."""

    repo_root = Path(__file__).resolve().parents[1]
    index_path = repo_root / "docs/source/workbook/track_d_chapter_index.rst"
    assert index_path.exists(), "Missing Track D chapter index page"

    text = index_path.read_text(encoding="utf-8")

    zip_path = repo_root / "src/pystatsv1/assets/workbook_track_d.zip"
    assert zip_path.exists(), "Missing packaged workbook_track_d.zip"

    with zipfile.ZipFile(zip_path, "r") as zf:
        wrapper_runs = sorted(
            {
                Path(name).stem
                for name in zf.namelist()
                if name.startswith("scripts/d") and name.endswith(".py")
            }
        )

    # We expect D00 helpers + D01..D23.
    expected = sorted(["d00_setup_data", "d00_peek_data"] + [f"d{i:02d}" for i in range(1, 24)])
    assert wrapper_runs == expected, (
        "Packaged Track D wrapper scripts changed. "
        "Update docs/source/workbook/track_d_chapter_index.rst accordingly."
    )

    for run_id in expected:
        # Every run should appear as a runnable command in the index.
        assert f"pystatsv1 workbook run {run_id}" in text

    # Quick sanity: the page should have section anchors for D01..D23.
    for i in range(1, 24):
        assert re.search(rf"^.. _track_d_run_d{i:02d}:\s*$", text, flags=re.M) is not None
