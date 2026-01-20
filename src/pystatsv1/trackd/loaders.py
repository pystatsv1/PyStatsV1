"""Track D dataset loaders.

These helpers centralize the repetitive "find datadir + read CSV + friendly errors"
logic used by Track D chapter runner scripts and (later) BYOD adapters.

This module is intentionally small and stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from ._errors import TrackDDataError
from ._types import DataFrame, DataFrames, PathLike
from .csvio import read_csv_required


def resolve_datadir(datadir: PathLike | None) -> Path:
    """Resolve and validate a Track D data directory.

    Parameters
    ----------
    datadir:
        A path to the directory containing Track D input CSV tables.

    Returns
    -------
    pathlib.Path
        The validated data directory path.

    Raises
    ------
    TrackDDataError
        If the directory is missing or not a folder.
    """
    if datadir is None:
        raise TrackDDataError(
            "Data directory is required.\n"
            "Hint: pass --datadir to the chapter runner, or set DATADIR in the "
            "workbook Makefile."
        )

    p = Path(datadir).expanduser()

    if not p.exists():
        raise TrackDDataError(
            f"Data directory not found: {p}.\n"
            "Hint: confirm the path exists, then try again."
        )
    if not p.is_dir():
        raise TrackDDataError(
            f"Data directory is not a folder: {p}.\n"
            "Hint: pass a folder path containing your exported CSV tables."
        )
    return p


def load_table(
    datadir: PathLike | None,
    filename: str,
    *,
    required_cols: Sequence[str] | None = None,
    parse_dates: Sequence[str] | None = None,
    dtypes: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> DataFrame:
    """Load a single CSV table from a Track D data directory.

    This is a thin wrapper around :func:`pystatsv1.trackd.csvio.read_csv_required`
    that resolves the data directory first.
    """
    root = resolve_datadir(datadir)
    path = root / filename
    return read_csv_required(
        path,
        required_cols=required_cols,
        parse_dates=parse_dates,
        dtypes=dtypes,
        **kwargs,
    )


def load_tables(
    datadir: PathLike | None,
    spec: Mapping[str, Sequence[str] | Mapping[str, Any]],
) -> DataFrames:
    """Load multiple tables using a small spec mapping.

    Parameters
    ----------
    datadir:
        Folder containing the CSV tables.
    spec:
        Mapping from *key* to either:

        - a sequence of required column names (filename defaults to the key), or
        - a dict with optional fields:
            - filename: override CSV filename (defaults to key)
            - required_cols: list/tuple/set of required columns
            - parse_dates: list/tuple/set of date columns to parse
            - dtypes: dict of dtypes to pass to pandas
            - kwargs: dict of additional pandas.read_csv kwargs

    Returns
    -------
    dict[str, pandas.DataFrame]
        Loaded tables keyed by the spec keys.
    """
    out: DataFrames = {}
    for key, cfg in spec.items():
        if isinstance(cfg, (list, tuple, set)):
            out[key] = load_table(datadir, key, required_cols=list(cfg))
            continue

        filename = str(cfg.get("filename", key))

        required_cols_raw = cfg.get("required_cols")
        if required_cols_raw is None:
            required_cols = None
        elif isinstance(required_cols_raw, (list, tuple, set)):
            required_cols = list(required_cols_raw)
        else:
            raise TrackDDataError(
                f"Invalid load_tables spec for {key}: 'required_cols' must be a "
                "list/tuple/set."
            )

        parse_dates_raw = cfg.get("parse_dates")
        if parse_dates_raw is None:
            parse_dates = None
        elif isinstance(parse_dates_raw, (list, tuple, set)):
            parse_dates = list(parse_dates_raw)
        else:
            raise TrackDDataError(
                f"Invalid load_tables spec for {key}: 'parse_dates' must be a "
                "list/tuple/set."
            )

        dtypes_raw = cfg.get("dtypes")
        if dtypes_raw is None:
            dtypes = None
        elif isinstance(dtypes_raw, dict):
            dtypes = dtypes_raw
        else:
            raise TrackDDataError(
                f"Invalid load_tables spec for {key}: 'dtypes' must be a dict."
            )

        extra_kwargs = cfg.get("kwargs", {})
        if not isinstance(extra_kwargs, dict):
            raise TrackDDataError(
                f"Invalid load_tables spec for {key}: 'kwargs' must be a dict."
            )

        out[key] = load_table(
            datadir,
            filename,
            required_cols=required_cols,
            parse_dates=parse_dates,
            dtypes=dtypes,
            **extra_kwargs,
        )
    return out
