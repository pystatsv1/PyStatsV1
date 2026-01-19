from __future__ import annotations

from pathlib import Path

import pytest

from pystatsv1.trackd import TrackDDataError, TrackDSchemaError
from pystatsv1.trackd.csvio import read_csv_required


def test_read_csv_required_missing_file_is_friendly(tmp_path: Path) -> None:
    missing = tmp_path / "nope.csv"
    with pytest.raises(TrackDDataError) as excinfo:
        read_csv_required(missing, required_cols=["a"])

    msg = str(excinfo.value)
    assert "Missing CSV file" in msg
    assert "nope.csv" in msg
    assert "Hint:" in msg


def test_read_csv_required_missing_columns_is_friendly(tmp_path: Path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")

    with pytest.raises(TrackDSchemaError) as excinfo:
        read_csv_required(p, required_cols=["a", "c"])

    msg = str(excinfo.value)
    assert "Missing required columns" in msg
    assert "c" in msg
    assert "Found columns" in msg
    assert "Hint:" in msg


def test_read_csv_required_success(tmp_path: Path) -> None:
    p = tmp_path / "ok.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")

    df = read_csv_required(p, required_cols=["a", "b"])
    assert list(df.columns) == ["a", "b"]
    assert df.shape == (1, 2)
