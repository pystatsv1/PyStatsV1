from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


# NOTE: This guardrail is intended to prevent *template drift* (files added/removed/edited)
# rather than enforce an OS-specific newline convention. Some Git checkouts (and some tools)
# may produce CRLF vs LF differences for text files, which should not fail CI.
_TEXT_NAMES = {"Makefile", "makefile"}
_TEXT_EXTS = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}


def _normalized_member_bytes(name: str, data: bytes) -> bytes:
    """Normalize member bytes for cross-platform comparison.

    We only normalize *text-like* files by converting CRLF -> LF (and bare CR -> LF).
    Binary files are hashed as-is.
    """
    base = name.rsplit("/", 1)[-1]
    ext = (base.rsplit(".", 1)[-1] if "." in base else "").lower()
    if base in _TEXT_NAMES or (ext and f".{ext}" in _TEXT_EXTS):
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def _zip_payload_hashes(zip_path: Path) -> dict[str, str]:
    """Return sha256 hashes of *decompressed* member bytes.

    This intentionally ignores ZIP metadata (timestamps, compression levels, etc.).
    """
    out: dict[str, str] = {}
    with ZipFile(zip_path, "r") as zf:
        for name in sorted(n for n in zf.namelist() if not n.endswith("/")):
            data = _normalized_member_bytes(name, zf.read(name))
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

        if built != committed:
            built_names = set(built)
            committed_names = set(committed)
            only_in_built = sorted(built_names - committed_names)
            only_in_committed = sorted(committed_names - built_names)
            changed = sorted(n for n in built_names & committed_names if built[n] != committed[n])

            lines: list[str] = [
                "Committed Track D workbook ZIP is stale or mismatched vs template source-of-truth.",
                "",
            ]
            if only_in_built:
                lines += ["Only in rebuilt ZIP:"] + [f"  - {n}" for n in only_in_built] + [""]
            if only_in_committed:
                lines += ["Only in committed ZIP:"] + [f"  - {n}" for n in only_in_committed] + [""]
            if changed:
                lines += [
                    "Same path, different content (after newline-normalization for text files):",
                    *[f"  - {n}" for n in changed],
                    "",
                ]
            lines += ["Fix: run `python tools/build_workbook_zip.py` and commit the updated ZIP."]

            raise AssertionError("\n".join(lines))