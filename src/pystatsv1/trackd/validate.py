# SPDX-License-Identifier: MIT
"""Validation helpers for Track D dataset folders.

Unlike :func:`pystatsv1.trackd.loaders.load_table`, which is intentionally
fail-fast, the functions here aggregate all schema issues into one friendly
summary that is suitable for student-facing CLI output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ._errors import TrackDDataError, TrackDSchemaError
from ._types import PathLike
from .contracts import ALLOWED_PROFILES, schemas_for_profile
from .loaders import resolve_datadir


def _read_header(path: Path) -> list[str]:
    # Cheap header-only read for required-column validation.
    df = pd.read_csv(path, nrows=0)
    return [str(c) for c in df.columns]


def _format_report(report: dict[str, Any]) -> str:
    profile = str(report.get("profile", ""))
    datadir = str(report.get("datadir", ""))

    missing_files: list[str] = list(report.get("missing_files", []))
    missing_cols: dict[str, list[str]] = dict(report.get("missing_columns", {}))
    found_cols: dict[str, list[str]] = dict(report.get("found_columns", {}))

    lines: list[str] = [
        "Track D dataset validation failed.",
        f"Profile: {profile}",
        f"Data directory: {datadir}",
        "",
    ]

    if missing_files:
        lines += ["Missing CSV files:", *[f"  - {n}" for n in missing_files], ""]

    if missing_cols:
        lines.append("CSV files with missing required columns:")
        for name in sorted(missing_cols.keys()):
            cols = missing_cols[name]
            lines.append(f"  - {name}: missing {', '.join(cols)}")
            found = found_cols.get(name)
            if found:
                lines.append(f"      Found columns: {', '.join(found)}")
        lines.append("")

    lines += [
        "Fix: export the required CSV(s) and ensure the header names match the Track D contract.",
        "Tip: generate a header-only template pack with: pystatsv1 trackd byod init --dest my_byod --profile <profile>",
    ]
    return "\n".join(lines)


def validate_dataset(datadir: PathLike | None, *, profile: str = "full") -> dict[str, Any]:
    """Validate a Track D dataset folder against a profile.

    Parameters
    ----------
    datadir:
        Folder containing CSV inputs.
    profile:
        One of: core_gl, ar, full.

    Returns
    -------
    dict
        A report dict with keys:
        ok, profile, datadir, missing_files, missing_columns, found_columns.

    Raises
    ------
    TrackDDataError
        If *datadir* is missing or not a directory.
    TrackDSchemaError
        If required files or required columns are missing.
    """

    root = resolve_datadir(datadir)

    p = (profile or "").strip().lower()
    try:
        schemas = schemas_for_profile(p)
    except ValueError as e:
        raise TrackDDataError(
            f"Unknown profile: {profile}.\n"
            f"Use one of: {', '.join(ALLOWED_PROFILES)}"
        ) from e

    report: dict[str, Any] = {
        "ok": True,
        "profile": p,
        "datadir": str(root),
        "missing_files": [],
        "missing_columns": {},
        "found_columns": {},
    }

    missing_files: list[str] = []
    missing_columns: dict[str, list[str]] = {}
    found_columns: dict[str, list[str]] = {}

    for schema in schemas:
        table_path = root / schema.name
        if not table_path.exists():
            missing_files.append(schema.name)
            continue

        cols = _read_header(table_path)
        found_columns[schema.name] = cols
        missing = [c for c in schema.required_columns if c not in set(cols)]
        if missing:
            missing_columns[schema.name] = missing

    if missing_files or missing_columns:
        report["ok"] = False
        report["missing_files"] = missing_files
        report["missing_columns"] = missing_columns
        report["found_columns"] = found_columns
        raise TrackDSchemaError(_format_report(report))

    report["missing_files"] = []
    report["missing_columns"] = {}
    report["found_columns"] = found_columns
    return report
