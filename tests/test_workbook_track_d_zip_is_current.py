from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


def _zip_payload_hashes(zip_path: Path) -> dict[str, str]:
    """Return sha256 hashes of *decompressed* member bytes.

    This intentionally ignores ZIP metadata (timestamps, compression levels, etc.).
    """
    out: dict[str, str] = {}
    with ZipFile(zip_path, "r") as zf:
        for name in sorted(n for n in zf.namelist() if not n.endswith("/")):
            data = zf.read(name)
            out[name] = hashlib.sha256(data).hexdigest()
    return out


def test_workbook_track_d_zip_is_current() -> None:
    """Guardrail: committed Track D workbook ZIP must match the template source."""
    root = Path(__file__).resolve().parents[1]
    template_dir = root / "workbooks" / "track_d_template"
    committed_zip = root / "src" / "pystatsv1" / "assets" / "workbook_track_d.zip"
    builder = root / "tools" / "build_workbook_zip.py"

    assert template_dir.exists(), (
        f"Missing template source directory: {template_dir}. "
        "Did you forget to apply the Track D template source-of-truth patch?"
    )
    assert committed_zip.exists(), f"Missing committed ZIP: {committed_zip}"
    assert builder.exists(), f"Missing ZIP builder script: {builder}"

    with tempfile.TemporaryDirectory() as td:
        built_zip = Path(td) / "workbook_track_d.zip"
        subprocess.run(
            [
                sys.executable,
                str(builder),
                "--src",
                str(template_dir),
                "--dest",
                str(built_zip),
            ],
            check=True,
        )

        built = _zip_payload_hashes(built_zip)
        committed = _zip_payload_hashes(committed_zip)

        assert built == committed, (
            "Committed Track D workbook ZIP is stale or mismatched vs template source-of-truth.\n\n"
            "Fix: run `python tools/build_workbook_zip.py` and commit the updated ZIP."
        )