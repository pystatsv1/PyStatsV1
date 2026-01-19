from __future__ import annotations

from pathlib import Path

import pytest

from pystatsv1.trackd._errors import TrackDSchemaError
from pystatsv1.trackd.schema import CONTRACT_TABLES, DATASET_NSO_V1, assert_schema, validate_schema


def _write_csv(path: Path, header: list[str]) -> None:
    path.write_text(",".join(header) + "\n", encoding="utf-8")


def test_validate_schema_reports_missing_tables_and_columns(tmp_path: Path) -> None:
    # Create one required file but with missing required columns.
    # chart_of_accounts requires: account_id, account_name, account_type, normal_side
    _write_csv(
        tmp_path / "chart_of_accounts.csv",
        header=["account_id", "account_name", "account_type"],
    )

    # Create another file that is OK.
    _write_csv(
        tmp_path / "gl_journal.csv",
        header=list(CONTRACT_TABLES["gl_journal"].required_columns),
    )

    report = validate_schema(tmp_path, dataset=DATASET_NSO_V1)

    assert report["ok"] is False

    # Missing file list should include at least one known table.
    assert "trial_balance_monthly.csv" in report["missing_tables"]

    chart = report["tables"]["chart_of_accounts.csv"]
    assert chart["exists"] is True
    assert "normal_side" in chart["missing_columns"]

    gl = report["tables"]["gl_journal.csv"]
    assert gl["exists"] is True
    assert gl["missing_columns"] == []


def test_assert_schema_raises_single_friendly_error(tmp_path: Path) -> None:
    # Leave datadir empty so we get missing-table errors.
    with pytest.raises(TrackDSchemaError) as ei:
        assert_schema(tmp_path, dataset=DATASET_NSO_V1)

    msg = str(ei.value)
    assert "Missing CSV files" in msg
    assert "chart_of_accounts.csv" in msg
    assert "Dataset: nso_v1" in msg
