from __future__ import annotations

from pathlib import Path

import pytest

import scripts._business_schema as shim
from pystatsv1.trackd._errors import TrackDSchemaError
from pystatsv1.trackd import schema as trackd_schema


def test_business_schema_shim_exports_trackd_schema() -> None:
    # The shim should re-export the package implementation (same function objects).
    assert shim.validate_schema is trackd_schema.validate_schema
    assert shim.assert_schema is trackd_schema.assert_schema


def test_business_schema_shim_validate_schema_report_shape(tmp_path: Path) -> None:
    report = shim.validate_schema(tmp_path, dataset=trackd_schema.DATASET_NSO_V1)

    assert isinstance(report, dict)
    assert report["ok"] is False
    assert "missing_tables" in report
    assert "tables" in report


def test_business_schema_shim_assert_schema_is_friendly(tmp_path: Path) -> None:
    with pytest.raises(TrackDSchemaError) as ei:
        shim.assert_schema(tmp_path, dataset=trackd_schema.DATASET_NSO_V1)

    msg = str(ei.value)
    assert "Track D dataset schema check failed" in msg
    assert "Missing CSV files" in msg


def test_track_d_template_business_schema_is_a_shim() -> None:
    root = Path(__file__).resolve().parents[1]
    template = root / "workbooks" / "track_d_template" / "scripts" / "_business_schema.py"
    assert template.exists()

    text = template.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.schema" in text
    assert "validate_schema" in text
    assert "assert_schema" in text
