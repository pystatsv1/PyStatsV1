from __future__ import annotations

from pathlib import Path

import pytest

from pystatsv1.trackd import TrackDDataError, TrackDSchemaError
from pystatsv1.trackd.loaders import load_table, resolve_datadir


def test_resolve_datadir_missing_is_friendly(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    with pytest.raises(TrackDDataError) as excinfo:
        resolve_datadir(missing)

    msg = str(excinfo.value)
    assert "Data directory not found" in msg
    assert "Hint:" in msg


def test_load_table_missing_csv_is_friendly(tmp_path: Path) -> None:
    # datadir exists, but the CSV does not
    with pytest.raises(TrackDDataError) as excinfo:
        load_table(tmp_path, "missing.csv", required_cols=["a"])

    msg = str(excinfo.value)
    assert "Missing CSV file" in msg
    assert "missing.csv" in msg
    assert "Hint:" in msg


def test_load_table_missing_required_columns_is_friendly(tmp_path: Path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")

    with pytest.raises(TrackDSchemaError) as excinfo:
        load_table(tmp_path, "data.csv", required_cols=["a", "c"])

    msg = str(excinfo.value)
    assert "Missing required columns" in msg
    assert "c" in msg
    assert "Found columns" in msg
    assert "Hint:" in msg
