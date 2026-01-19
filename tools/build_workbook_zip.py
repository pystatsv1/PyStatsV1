"""Build committed workbook template ZIPs from source-of-truth directories.

Why this exists
--------------
Historically, workbook templates were edited by manually opening a ZIP.
That inevitably causes drift and makes refactors scary.

For Track D, the source template lives at:
    workbooks/track_d_template/

This script (re)builds:
    src/pystatsv1/assets/workbook_track_d.zip

Usage
-----
    python tools/build_workbook_zip.py

Or explicitly:
    python tools/build_workbook_zip.py --src workbooks/track_d_template --dest src/pystatsv1/assets/workbook_track_d.zip
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipInfo, ZipFile


_FIXED_ZIP_DT = (2020, 1, 1, 0, 0, 0)
_SKIP_BASENAMES = {".DS_Store", "Thumbs.db"}


def _iter_files(src_dir: Path) -> Iterable[tuple[Path, str]]:
    """Yield (path, zip_relpath) for all files under src_dir (sorted)."""
    candidates = [p for p in src_dir.rglob("*") if p.is_file()]
    for p in sorted(candidates):
        if p.name in _SKIP_BASENAMES:
            continue
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(src_dir).as_posix()
        yield p, rel


def build_zip(src_dir: Path, dest_zip: Path) -> list[str]:
    """Build a deterministic ZIP from src_dir.

    Returns a list of archived file paths (POSIX style) in the ZIP.
    """
    if not src_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {src_dir}")
    if not src_dir.is_dir():
        raise NotADirectoryError(f"Template path is not a directory: {src_dir}")

    files = list(_iter_files(src_dir))
    if not files:
        raise ValueError(f"Template directory is empty: {src_dir}")

    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    archived: list[str] = []
    with ZipFile(dest_zip, "w") as zf:
        for fs_path, arc_path in files:
            info = ZipInfo(arc_path)
            info.date_time = _FIXED_ZIP_DT
            info.compress_type = ZIP_DEFLATED
            # Preserve unix permission bits where meaningful.
            info.external_attr = (fs_path.stat().st_mode & 0o777) << 16

            data = fs_path.read_bytes()
            zf.writestr(info, data, compress_type=ZIP_DEFLATED)
            archived.append(arc_path)

    return archived


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    default_src = root / "workbooks" / "track_d_template"
    default_dest = root / "src" / "pystatsv1" / "assets" / "workbook_track_d.zip"

    p = argparse.ArgumentParser(description="Build workbook ZIP templates from source directories.")
    p.add_argument("--src", type=Path, default=default_src, help=f"Template directory (default: {default_src})")
    p.add_argument("--dest", type=Path, default=default_dest, help=f"Destination ZIP path (default: {default_dest})")
    p.add_argument(
        "--list",
        action="store_true",
        help="Print archived file list after building.",
    )

    ns = p.parse_args(argv)

    archived = build_zip(ns.src, ns.dest)
    print(f"Wrote: {ns.dest} ({len(archived)} files, sha256={_sha256(ns.dest)[:12]}…)")
    if ns.list:
        for name in archived:
            print(name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
