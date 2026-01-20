from __future__ import annotations

from pathlib import Path

from pystatsv1.cli import main


def _write_chart_of_accounts(p: Path, *, missing_normal_side: bool = False) -> None:
    # Minimal valid header set for the contract.
    cols = ["account_id", "account_name", "account_type"]
    if not missing_normal_side:
        cols.append("normal_side")
    row = "1,Cash,asset" + ("" if missing_normal_side else ",debit")
    p.write_text(",".join(cols) + "\n" + row + "\n", encoding="utf-8")


def _write_gl_journal(p: Path, *, missing_credit: bool = False) -> None:
    cols = ["txn_id", "date", "doc_id", "description", "account_id", "debit"]
    if not missing_credit:
        cols.append("credit")
    row = "t1,2025-01-01,d1,Example,1,100" + ("" if missing_credit else ",0")
    p.write_text(",".join(cols) + "\n" + row + "\n", encoding="utf-8")


def test_trackd_validate_missing_datadir_is_friendly(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "nope"
    rc = main(["trackd", "validate", "--datadir", str(missing), "--profile", "core_gl"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "Data directory not found" in out
    assert "Hint:" in out


def test_trackd_validate_missing_csv_is_friendly(tmp_path: Path, capsys) -> None:
    # Only chart_of_accounts.csv exists; gl_journal.csv is missing.
    _write_chart_of_accounts(tmp_path / "chart_of_accounts.csv")

    rc = main(["trackd", "validate", "--datadir", str(tmp_path), "--profile", "core_gl"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "Track D dataset validation failed" in out
    assert "Profile: core_gl" in out
    assert "Missing CSV files" in out
    assert "gl_journal.csv" in out


def test_trackd_validate_missing_required_columns_is_friendly(tmp_path: Path, capsys) -> None:
    _write_chart_of_accounts(tmp_path / "chart_of_accounts.csv")
    _write_gl_journal(tmp_path / "gl_journal.csv", missing_credit=True)

    rc = main(["trackd", "validate", "--datadir", str(tmp_path), "--profile", "core_gl"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "CSV files with missing required columns" in out
    assert "gl_journal.csv" in out
    assert "credit" in out
    assert "Found columns" in out
