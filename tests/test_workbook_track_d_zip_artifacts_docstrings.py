# SPDX-License-Identifier: MIT

from __future__ import annotations

import zipfile
from pathlib import Path


def test_track_d_zip_cli_default_outdir_is_track_d() -> None:
    """Workbook Track D scripts should default to outputs/track_d.

    This keeps the student mental model consistent and makes --outdir behave
    like a true destination override.
    """

    zip_path = Path("src/pystatsv1/assets/workbook_track_d.zip")
    with zipfile.ZipFile(zip_path) as zf:
        txt = zf.read("scripts/_cli.py").decode("utf-8")

    assert "default=pathlib.Path(\"outputs/track_d\")" in txt
    assert "Default: ./outputs/track_d" in txt


def test_track_d_zip_scripts_have_artifacts_docstring_blocks() -> None:
    """Ensure every Track D run script advertises its artifacts.

    Students should be able to open a script and immediately see which files
    to expect under --outdir.
    """

    zip_path = Path("src/pystatsv1/assets/workbook_track_d.zip")
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        targets = [
            n
            for n in names
            if (
                (n.startswith("scripts/business_ch") and n.endswith(".py"))
                or (n.startswith("scripts/d") and n.endswith(".py"))
            )
        ]

        missing: list[str] = []
        for name in sorted(targets):
            txt = zf.read(name).decode("utf-8")
            if "Artifacts written to" not in txt:
                missing.append(name)

        assert not missing, "Scripts missing 'Artifacts written to' docstring block:\n" + "\n".join(
            missing
        )


def test_track_d_zip_no_outdir_appends_track_d_subfolder() -> None:
    """Guardrail: --outdir should be the final destination.

    No script should do args.outdir / 'track_d' internally.
    """

    zip_path = Path("src/pystatsv1/assets/workbook_track_d.zip")
    with zipfile.ZipFile(zip_path) as zf:
        bad: list[str] = []
        for name in sorted(n for n in zf.namelist() if n.startswith("scripts/") and n.endswith(".py")):
            txt = zf.read(name).decode("utf-8")
            if "args.outdir / \"track_d\"" in txt or "args.outdir/\"track_d\"" in txt:
                bad.append(name)

    assert not bad, "Scripts still append /track_d to args.outdir:\n" + "\n".join(bad)
